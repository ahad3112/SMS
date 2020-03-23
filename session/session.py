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

    def save(self):
        # get all opened tabs
        cmd = "/usr/bin/osascript -e 'tell application \"{0}\"' -e 'get URL of every tab of every window' -e 'end tell'"
        links = {}

        # TODO : Remove This methods from here ...
        for browser in config.SUPPORTED_BROWSERS:
            pipe = Popen(cmd.format(browser), stdout=PIPE, shell=True)
            links[browser] = pipe.communicate()[0].strip().split(b',')

        # saving all opened tabs along with session name, open command
        sql_string = 'insert into {0} values(?,?,?)'.format(config.TABLES['links'])

        # Pringint progress bar
        from time import sleep
        print('{0:^{1}}'.format(' Saving Links ', 130))
        # step = 100 // len(links)
        step = 4
        current = step
        progress_bar = '[{0:<{1}}]{2:>{3}}%'

        for browser in config.SUPPORTED_BROWSERS:
            for link in links[browser]:
                if link:
                    # Checking whether there is any record for the session, command and args
                    query_string = 'select * from {0} where session=? and command=? and links=?'.format(config.TABLES['links'])
                    self.db.query(table=config.TABLES['links'], query_string=query_string, values=(self.name, config.SUPPORTED_BROWSERS[browser], link))
                    query_length = len(self.db.cursor.fetchall())
                    if query_length == 1:
                        break
                    elif query_length > 1:
                        raise AssertionError('Multiple same entry for the Session: "{0}"'.format(self.name))

                    # save unique entry
                    self.db.update(table=config.TABLES['links'], sql_string=sql_string, values=(self.name, config.SUPPORTED_BROWSERS[browser], link.strip()), commit=True)

                    # Pringint progress bar
                    progress = progress_bar.format('=' * (current - 1) + '>', 124, current, 4)
                    Display.success(what=progress, info='{}%'.format(current), end='')
                    # sys.stdout.write(progress)
                    sys.stdout.flush()
                    sys.stdout.write('\r')
                    current += step

        progress = progress_bar.format('=' * 124, 124, 100, 4)
        Display.success(what=progress, info='{}%'.format(100), end='')
        # sys.stdout.write(progress)
        sys.stdout.write('\n')
        sys.stdout.flush()

    def open(self):
        query_string = 'select * from {0} where session = ?'.format(config.TABLES['links'])
        self.db.query(table=config.TABLES['links'], query_string=query_string, values=[self.name])

        for (name, command, args) in self.db.cursor.fetchall():
            # ?????????? Space within the command is not working
            call(command + args, shell=True)

    def view_old(self, *, return_result=False):
        # Tesing view to view the entries in apps table
        # Later will show only specially requested entries: eg  links, shell
        query_string = 'select * from {0} where session = ?'.format(config.TABLES['links'])
        self.db.query(table=config.TABLES['links'], query_string=query_string, values=[self.name])

        query_result = list(enumerate(self.db.cursor.fetchall()))
        if not query_result:
            return

        Display.header(head=' Record for {0} '.format(self.name))
        print('{0:<10}{1:<40}{2:<70}'.format('No.', 'Command', 'Arguments'))
        print('{0:<10}{1:<40}{2:<70}'.format('', '-' * len('Command'), '-' * len('Arguments')))
        for (index, (session, command, args)) in query_result:
            print('{0!s:<10}{1!s:<40}{2!s:<80}'.format(index, command.decode().strip(), args.decode().strip()))

        if return_result:
            return query_result

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
            print('Record for a single session')
            headers = ['Session Name', 'Command', 'Arguments']
            for table in config.TABLES.values():
                records = self.__record(table=table)
                Display.dataframe(
                    headers=headers,
                    rows=records
                )

    def edit(self):
        #  We will update this module later along with the view_old method
        records = self.view_old(return_result=True)
        if records:
            while True:
                action = input('Press A/a to add or D/d to delete. ')
                if action in ['D', 'd']:
                    no = input('Choose number from the list to delete? ')
                    print('Deleting {0!s}'.format(no))
                    self.delete_row(records=records, index=int(no))
                    break
                elif action in ['A', 'a']:
                    print('Add action has been choosen..')
                    break
                else:
                    print('Wrong choice. Try Again.')
        else:
            Display.warning(what='Edit not possible for {0} '.format(self.name), info='[ NO RECORDS ]')

    def delete_row(self, *, records, index):
        sql_string = 'delete from {0} where session = ? and command = ? and links = ?'.format(config.TABLES['links'])
        for (idx, record) in records:
            if idx == index:
                self.db.update(table=config.TABLES['links'], sql_string=sql_string, values=record, commit=True)
                break
