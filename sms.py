#!/usr/bin/env python

import sys
import os

import argparse

from session.cli import SessionCLI
from session.session import Session
from database.cli import DatabaseCLI
from database.database import Database

'''
This script will use as shortcut to open terminal with mostly used directories
And other useful applicaiton.
This will be customize to save session with name so that I can open required application with one command
'''

version = 1.0
prog = os.path.split(sys.argv[0])[1][:-3]


def cli():
    parser = argparse.ArgumentParser(
        prog=prog,
        description='''
        Command Line Interface to do some job in shortcut. for example:
        saving sessions, open a saved session, view/edit session,
        redirect to a named folder  within terminal etc
        '''
    )

    #  adding the version
    parser.add_argument('-v', '--version', action='version', version='{0} {1}'.format(prog, version))

    sub_parsers = parser.add_subparsers(
        title='sub-commands',
        description='This is the description for the sub-commands',
    )

    DatabaseCLI(sub_parsers=sub_parsers)
    SessionCLI(sub_parsers=sub_parsers)
    return parser.parse_args()


def action(*, args, db):
    if len(sys.argv) >= 3:
        if sys.argv[1] == 'session':
            Session(name=args.name, subcommand=sys.argv[2], args=args, db=db)
        elif sys.argv[1] == 'db':
            getattr(db, sys.argv[2])(args=args)


if __name__ == '__main__':
    # Database instance object
    db = Database()
    args = cli()
    action(args=args, db=db)
