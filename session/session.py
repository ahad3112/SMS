from datetime import date
import os
import sys
from subprocess import (
    Popen, PIPE, call
)
import config
from utilities.display import Display


class Session:

    def __init__(self, *, name=None, subcommand, args, db=None):
        self.name = name if name else '{0}-{1}'.format(os.environ['USER'], str(date.today()))
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
            Display.info('Deleting Row ', info=' [ Type Row No.]')
            confirmation = input()
            if confirmation.isdigit():
                # add row deletion logic
                row = int(confirmation)
                self.delete_row(table=config.TABLES['links'], records=records, row=row)
                Display.info('Row {0} '.format(confirmation), info=' [ DELETED ]')
            else:
                Display.info(what='Wrong Choice ', info=' [ Leaving Editing]')
                break

    def edit(self):
        if self.args.add:
            # Adding
            pass
        if self.args.delete:
            # deleting
            if self.args.links:
                self.__delete(table=config.TABLES['links'])
            else:
                pass
        if self.args.open:
            # open
            pass

    def delete_row(self, *, table, records, row):
        sql_string = 'delete from {0} where session = ? and command = ? and links = ?'.format(table)
        for (idx, record) in enumerate(records):
            if idx == row:
                self.db.update(table=config.TABLES['links'], sql_string=sql_string, values=record, commit=True)
                break
