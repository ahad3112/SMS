from datetime import date
import os
import sys
from subprocess import (
    Popen, PIPE, call
)
import config
from utilities.display import Display


class Session:

    def __init__(self, *, name=None, subcommand, parser, args, db=None):
        self.name = name if name else '{0}-{1}'.format(os.environ['USER'], str(date.today()))
        self.parser = parser
        self.args = args

        self.db = db
        getattr(self, subcommand)()

    def __all_sessions(self, *, tables):
        sessions = []
        for table in tables:
            query_string = 'select session from {0}'.format(table)
            self.db.query(table=table, query_string=query_string)
            results = [session[0] for session in self.db.cursor.fetchall()]
            result = list(set(results))
            if not results:
                continue

            sessions.append([table, result])

        return sessions

    def __save_links(self):
        Display.title(title='Saving links to : {0}'.format(self.name))
        cmd = "/usr/bin/osascript -e 'tell application \"{0}\"' -e 'get URL of every tab of every window' -e 'end tell'"
        links = {}

        total_links = 0
        for browser in config.SUPPORTED_BROWSERS:
            pipe = Popen(cmd.format(browser), stdout=PIPE, shell=True)
            links[browser] = pipe.communicate()[0].strip().split(b',')
            total_links += len(links[browser])

        # saving all opened tabs along with session name, open command
        sql_string = 'insert into {0} values(?,?,?)'.format(config.TABLES['links'])

        # variable related to diplaying progress bar
        progress_bar_step = 0
        percentage_step_length = 100 // total_links

        from time import sleep

        for browser in config.SUPPORTED_BROWSERS:
            browser_links = links.get(browser, None)
            if browser_links:
                for link in browser_links:
                    if link:
                        # Checking whether there is any record for the session, command and args
                        query_string = 'select * from {0} where session=? and command=? and links=?'.format(config.TABLES['links'])
                        self.db.query(table=config.TABLES['links'], query_string=query_string, values=(self.name, config.SUPPORTED_BROWSERS[browser], link.strip().decode()))
                        query_length = len(self.db.cursor.fetchall())
                        if query_length == 1:
                            pass
                        elif query_length > 1:
                            raise AssertionError('Multiple same entry for the Session: "{0}"'.format(self.name))
                        else:
                            # save unique entry
                            self.db.update(
                                table=config.TABLES['links'],
                                sql_string=sql_string,
                                values=(self.name, config.SUPPORTED_BROWSERS[browser], link.strip().decode()),
                                commit=True,
                                create_if_required=True
                            )
                    progress_bar_step += 1
                    Display.progress_bar(
                        total=total_links,
                        step=progress_bar_step,
                        completed=str(percentage_step_length * progress_bar_step) + '%'
                    )
                    # For testing
                    # sleep(.2)

        Display.progress_bar(total=total_links, step=progress_bar_step + 1, completed='100%')
        print()

    def save(self):
        if self.args.links:
            self.__save_links()
        elif self.args.all:
            self.__save_links()
            #  Add all other apps

    def open(self):
        query_string = 'select * from {0} where session = ?'.format(config.TABLES['links'])
        self.db.query(table=config.TABLES['links'], query_string=query_string, values=[self.name])

        for (name, command, args) in self.db.cursor.fetchall():
            call(command + args, shell=True)

    def __record(self, *, table):
        query_string = 'select * from {0} where session = ?'.format(
            table,
            self.name
        )
        self.db.query(table=table, query_string=query_string, values=[self.name])
        return self.db.cursor.fetchall()

    def view(self, *pargs, **kwargs):
        if self.args.all_sessions:
            sessions = self.__all_sessions(tables=config.TABLES.values())
            Display.dataframe(
                headers=['Table Name', 'List of Session'],
                rows=sessions
            )
        elif self.args.name:
            headers = ['Command', 'Arguments']
            for table in config.TABLES.values():
                Display.title(title='Record for Session : {0} , Table: {1}'.format(self.name, table))
                records = self.__record(table=table)
                Display.dataframe(
                    headers=headers,
                    rows=[(cmd, arg) for (sess, cmd, arg) in records]
                )

    def __display_links_for_edit(self, table, records):
        Display.title(title='Record for Session : {0}, Table: {1}'.format(self.name, table))
        Display.dataframe(
            headers=['Command', 'Arguments'],
            rows=[(cmd, arg) for (sess, cmd, arg) in records]
        )

    def __edit_links(self):

        while True:
            if self.args.add or self.args.delete or self.args.open:
                if self.args.add:
                    key = 'a'
                if self.args.delete:
                    key = 'd'
                if self.args.open:
                    key = 'o'
            else:
                Display.title(title='Edit Options')
                Display.dataframe(
                    headers=['Action', 'keys'],
                    rows=[
                        ('Add', 'a/A'),
                        ('Delete', 'd/D'),
                        ('Open', 'o/O'),
                        ('Quit', 'Any Other keys'),
                    ]
                )
                key = input()

            if key in ['a', 'A']:
                Display.info(what='Adding New Record in table "{0}" '.format(config.TABLES['links']), info=' [ Provide command and link ]')
                while True:
                    command = input('Command?\t')
                    link = input('link?\t')
                    if command and link:
                        print('Got enough information to add link??')
                        break
                    else:
                        while not command or not link:
                            if command:
                                link = input('link?\t')
                            else:
                                command = input('Command?\t')
                        print('Got enough information to add link??')
                        break
                Display.success(what='Adding New Record in table "{0}" '.format(config.TABLES['links']), info=' [ Success ]')
                # continue
            elif key in ['d', 'D']:
                records = self.__record(table=config.TABLES['links'])
                self.__display_links_for_edit(table=config.TABLES['links'], records=records)
                Display.info('Deleting Row ', info='[ Type Row No.]')
                row = input()
                self.delete_row(table=config.TABLES['links'], records=records, row=row)
            elif key in ['o', 'O']:
                Display.info('Opening link/links ', info=' [ Not Implemented Yet]')
            else:
                Display.info(what='Editing ', info=' [ Leaving ]')
                break

            # Redislay records
            records = self.__record(table=config.TABLES['links'])
            self.__display_links_for_edit(table=config.TABLES['links'], records=records)

    def __delete(self, *, table):
        while True:
            records = self.__record(table=table)
            self.__display_links_for_edit(table=table, records=records)
            if not records:
                Display.info(what='No record available to delete for {0} '.format(self.name), info=' [QUITING]')
                break
            Display.info('Type Row no to delete ', info=' [ q/Q to Quit]')
            confirmation = input()
            if confirmation.isdigit():
                # add row deletion logic
                row = int(confirmation)
                self.delete_row(table=config.TABLES['links'], records=records, row=row)
                # Display.title(title='Row {0} Deletion was successfull'.format(confirmation))
                Display.info(what='Row {0} Deletion '.format(confirmation), info=' [ SUCCESS ]')
                print()
            elif confirmation in ['q', 'Q']:
                Display.info(what='You chose to Quit ', info=' [ Leaving]')
                break

    def __add(self, *, table, commands):
        Display.title(title='Adding to table "{0}" for Session "{1}"'.format(table, self.name))
        while True:
            Display.info('INPUT FORMAT: [ "{0}" args1 args2, "{0}" args1 args2 ... ] '.format('|'.join(commands.keys())), info=' [ q/Q to delete ]')
            user_input = input().split(',')
            if user_input[0].strip() in ['q', 'Q']:
                Display.info(what='You have chosen to Quit ', info=' [ QUITING ]')
                break
            else:
                sql_string = 'insert into {0} values(?,?,?)'.format(table)
                for entry in user_input:
                    command_for, *args = [x.strip() for x in entry.split()]
                    if not command_for in commands.keys():
                        Display.info(what='Wrong input : {0}, available are '.format(command_for),
                                     info=' [ {0} ]'.format('|'.join(commands.keys())))
                    else:
                        for arg in args:
                            self.db.update(
                                table=table,
                                sql_string=sql_string,
                                values=(self.name, commands[command_for], arg),
                                commit=True,
                                create_if_required=False
                            )
                            Display.success('Addition of {0} : {1} '.format(command_for, arg), info=' [ Success ]')

    def edit(self):
        self.__opt_flags_check(['links', 'shells'])
        self.__opt_flags_check(['add', 'delete'])
        if self.args.add:
            # Adding
            if self.args.links:
                self.__add(table=config.TABLES['links'], commands=config.SUPPORTED_BROWSERS)
            else:
                pass
        if self.args.delete:
            # deleting
            if self.args.links:
                self.__delete(table=config.TABLES['links'])
            else:
                pass

    def delete_row(self, *, table, records, row):
        sql_string = 'delete from {0} where session = ? and command = ? and links = ?'.format(table)
        for (idx, record) in enumerate(records):
            if idx == row:
                self.db.update(table=config.TABLES['links'], sql_string=sql_string, values=record, commit=True)
                break

    # Optional arguments checking
    def __opt_flags_check(self, attrs):
        if not any(getattr(self.args, attr) for attr in attrs):
            raise self.parser.error(message='Missing one of the optional argument from {0}'.format(['-' + x[0] for x in attrs]))
