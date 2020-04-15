'''
Author :
    * Muhammed Ahad  <ahad3112@yahoo.com, maaahad@gmail.com>
'''

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
        self.__opt_flags_check(['links', 'shells'])
        if self.args.links:
            query_string = 'select * from {0} where session = ?'.format(config.TABLES['links'])
            self.db.query(table=config.TABLES['links'], query_string=query_string, values=[self.name])

            for (name, command, args) in self.db.cursor.fetchall():
                call(command + args, shell=True)
        else:
            Display.info(what='Opening all saved shell process ', info=' [ NOT IMPLEMENTED YET ]')

    def __record(self, *, table):
        query_string = 'select * from {0} where session = ?'.format(
            table,
            self.name
        )
        self.db.query(table=table, query_string=query_string, values=[self.name])
        return self.db.cursor.fetchall()

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

    def view(self, *pargs, **kwargs):
        if self.args.name:
            self.__opt_flags_check(['links', 'shells', 'all'])
            if self.args.links:
                headers = ['Command', 'Arguments']
                Display.title(title='Record for Session : {0} , Table: {1}'.format(self.name, config.TABLES['links']))
                records = self.__record(table=config.TABLES['links'])
                Display.dataframe(
                    headers=headers,
                    rows=[(cmd, arg) for (sess, cmd, arg) in records]
                )
            elif self.args.shells:
                Display.info(what='Viewing all saved shell process ', info=' [ NOT IMPLEMENTED YET ]')
            else:
                Display.info(what='Viewing all processes ', info=' [ NOT IMPLEMENTED YET ]')

        elif self.args.sessions:
            self.__opt_flags_check(['links', 'shells', 'all'])
            if self.args.links:
                tables = ['links']
            elif self.args.shells:
                Display.info(what='Viewing all session name under table : "shells" ', info=' [ NOT IMPLEMENTED YET ]')
                return
            else:
                tables = config.TABLES.values()

            sessions = self.__all_sessions(tables=tables)

            Display.dataframe(
                headers=['Table Name', 'List of Session'],
                rows=sessions
            )
        else:
            self.parser.error(message='Missing argument from [{0}, {1}]'.format('-n/name', '--sessions'))

    def __display_links_for_edit(self, table, records):
        Display.title(title='Record for Session : {0}, Table: {1}'.format(self.name, table))
        Display.dataframe(
            headers=['Command', 'Arguments'],
            rows=[(cmd, arg) for (sess, cmd, arg) in records]
        )

    def __delete(self, *, table):
        while True:
            records = self.__record(table=table)
            self.__display_links_for_edit(table=table, records=records)
            if not records:
                Display.info(what='No record available to delete for {0} '.format(self.name), info=' [QUITING]')
                break
            Display.info('Type Comma or space separated row no to delete ', info=' [ q/Q to Quit]')

            confirmation = input()
            if confirmation in ['q', 'Q']:
                Display.info(what='You chose to Quit ', info=' [ Leaving]')
                break
            else:
                # extracting all row no from confirmation
                rows = []
                for element in confirmation.split():
                    rows.extend(element.split(','))
                # Now deleting one row at a time
                for row in rows:
                    if row.isdigit() and int(row) < len(records):
                        # add row deletion logic
                        row = int(row)
                        self.delete_row(table=config.TABLES['links'], records=records, row=row)
                        Display.info(what='Row "{0}"" Deletion '.format(row), info=' [ SUCCESS ]')
                        print()
                    else:
                        Display.warning(what='Row "{0}" deletion : Not Digit or beyond the record length '.format(row), info=' [ FAILED ]')

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
                            Display.success('Addition of {0} : {1} '.format(command_for, arg), info=' [ SUCCESS ]')

    def edit(self):
        self.__opt_flags_check(['links', 'shells'])
        self.__opt_flags_check(['add', 'delete', 'delete_all'])
        if self.args.add:
            # Adding
            if self.args.links:
                self.__add(table=config.TABLES['links'], commands=config.SUPPORTED_BROWSERS)
            else:
                pass
        elif self.args.delete:
            # deleting
            if self.args.links:
                self.__delete(table=config.TABLES['links'])
            else:
                pass
        elif self.args.delete_all:
            # deleting all entry of link/shell apps for session name
            if self.args.links:
                Display.title(title='Deleting entries from table "{0}" for Session "{1}"'.format(config.TABLES['links'], self.name))
                sql_string = 'delete from {table} where session = ?'.format(table=config.TABLES['links'])
                self.db.update(table=config.TABLES['links'], sql_string=sql_string, values=(self.name, ), commit=True)
            else:
                pass

            Display.success('Deleting All ', info=' [ SUCCESS ]')

    def delete_row(self, *, table, records, row):
        sql_string = 'delete from {0} where session = ? and command = ? and links = ?'.format(table)
        for (idx, record) in enumerate(records):
            if idx == row:
                self.db.update(table=config.TABLES['links'], sql_string=sql_string, values=record, commit=True)
                break

    # Optional arguments checking
    def __opt_flags_check(self, attrs):
        if not any(getattr(self.args, attr) for attr in attrs):
            raise self.parser.error(message='Missing one of the optional argument from {0}'.format(['--' + x.replace('_', '-') for x in attrs]))
