import sqlite3
import os
import sys
import config
from utilities.display import Display


class Database:
    def __init__(self):
        self.__login()

    def __login(self):
        self.connection = sqlite3.connect(config.DB_NAME)
        self.cursor = self.connection.cursor()

    def logout(self, commit=False):
        if commit:
            self.connection.commit()
        self.connection.close()

    def delete(self, *pargs, **kwargs):
        # Taking Conformation from the user interactively if -y flag was not provided
        try:
            args = kwargs['args']
        except KeyError as keyerror:
            msg = 'Keyword argument {0} in class: {1}, function: {2}'.format(keyerror, self.__class__.__name__, self.delete.__name__)
            print(Display.fail(msg, info='[ MISSING ]'))
            return
        else:
            if not args.yes:
                while True:
                    confirmation = input('Confirm to delete database: y/n?\n')
                    if confirmation in ['n', 'N']:
                        return
                    elif confirmation in ['y', 'Y']:
                        break

        # closing the connection
        self.connection.close()
        try:
            os.remove(config.DB_NAME)
        except FileNotFoundError:
            print(Display.fail(config.DB_NAME, info='[ DOES NOT EXIST ]'))
        else:
            Display.success(what='Deleting DB: {0} '.format(config.DB_NAME), info=' [ SUCCESS ]')

    def drop(self, *, args):
        if args.table:
            if self.__table_exists(table=args.table, trace=False):
                if not args.yes:
                    Display.warning(what='Dropping table {0} '.format(args.table), info='[ Confirm y/Y? ]')
                    confirmation = input()
                    if not confirmation in ['y', 'Y']:
                        return
                self.cursor.execute('drop table {0}'.format(args.table))
            else:
                Display.warning(what='Dropping table {0} '.format(args.table), info='[ NOT EXIST ]')

        elif args.all:
            tables = self.get_tables()
            for tables in tables:
                self.cursor.execute('drop table {0}'.format(tables[0]))

    def get_tables(self):
        self.cursor.execute("select all name from sqlite_master")
        return self.cursor.fetchall()

    def tables(self, *args, **kwargs):
        Display.title(title='List of Available Tables')
        all_tables = self.get_tables()
        data = []
        for table in all_tables:
            self.cursor.execute("PRAGMA table_info('{0}')".format(table[0]))
            columns = self.cursor.fetchall()
            data.append(
                (table[0], [col[1] for col in columns])
            )

        Display.list_data(headers=['Table Name', 'Columns'], data=data)
        # Checking
        Display.list_data(data=data)
        Display.list_data(data=data)
        Display.list_data(data=data)
        Display.list_data(data=data)
        Display.list_data(data=data)

        # print(data)

    def __table_exists(self, *, table, trace=False):
        all_tables = self.get_tables()

        if all_tables and table in all_tables[0]:
            if trace:
                Display.info(what='Table {0} in database. '.format(table), info='[ EXIST ]')
            return True
        else:
            return False

    def create_table(self, *, table):
        if table in config.DB_TABLES and not self.__table_exists(table=table, trace=True):
            self.cursor.execute(config.DB_TABLES[table])
            Display.success(what='table {} added to database '.format(table), info='[ SUCCESS ]')
        else:
            raise Exception('No table creation recipe is avaibale in {0} for {1}'.format(
                config.__name__,
                table
            ))

    def update(self, *, table, sql_string, values, commit=False, create_if_required=False):
        if not self.__table_exists(table=table):
            if create_if_required:
                self.create_table(table=table)
            else:
                return
        self.cursor.execute(sql_string, values)

        if commit:
            self.connection.commit()

    def query(self, *, table, query_string, values=None):
        if self.__table_exists(table=table):
            if values:
                self.cursor.execute(query_string, values)
            else:
                self.cursor.execute(query_string)
        else:
            Display.fail(what='Query on table {0} '.format(table), info='[ NOT EXIST ]')
