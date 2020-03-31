from core.commands import Command
from core.arguments import Argument


class SessionCLI:
    sub_commands = [
        Command(name='open',
                help='open a saved session',
                description='This module will open a saved session',
                args=[
                    Argument(
                        name=('-n', '--name',),
                        type=str,
                        help='Later',
                        required=True
                    ),
                ]),
        Command(name='view',
                help='view a saved session',
                description='This module display saved session using the session name',
                args=[
                    Argument(
                        name=('-n', '--name',),
                        type=str,
                        help='Display all records for this session name.',
                        group='view_option',
                        required=False
                    ),
                    Argument(
                        name=('-as', '--all-sessions',),
                        help='Display all sessions from the database.',
                        action='store_true',
                        group='view_option',
                        required=False
                    ),
                ],
                mutually_exclusive_group={'view_option': None}),
        Command(name='edit',
                help='edit a saved session',
                description='This module helps edit a saved session',
                args=[
                    Argument(
                        name=('-n', '--name',),
                        type=str,
                        help='Later',
                        required=True
                    ),
                    Argument(
                        name=('-l', '--links',),
                        help='Choose links list to be Edited.',
                        action='store_true',
                        group='apps'
                    ),
                    Argument(
                        name=('-s', '--shell',),
                        help='Choose Shell list to be Edited.',
                        action='store_true',
                        group='apps'
                    ),
                    Argument(
                        name=('-a', '--add',),
                        help='add link/links',
                        action='store_true',
                        group='edit_option'
                    ),
                    Argument(
                        name=('-d', '--delete',),
                        help='Delete link/links',
                        action='store_true',
                        group='edit_option'
                    ),
                    Argument(
                        name=('-o', '--open',),
                        help='Open link/links',
                        action='store_true',
                        group='edit_option'
                    ),
                ],
                mutually_exclusive_group={
                    'edit_option': None,
                    'apps': None,
                }),
        Command(name='save',
                help='saves current session',
                description='This module will save the current session',
                args=[
                    Argument(
                        name=('-n', '--name'),
                        type=str,
                        help='Later',
                        required=True
                    ),
                    Argument(
                        name=('-l', '--links',),
                        type=str,
                        help='Saves links',
                        action='store_true',
                        group='save_option'
                    ),
                    Argument(
                        name=('-s', '--shell',),
                        type=str,
                        help='Saves all opening shell process',
                        action='store_true',
                        group='save_option'
                    ),
                ],
                mutually_exclusive_group={'save_option': None}
                ),
    ]

    def __init__(self, *, sub_parsers, name='session'):
        self.parser = sub_parsers.add_parser(name,
                                             description='This is the description for the {0} command'.format(name),
                                             help='{0} module'.format(name),
                                             )

        self.sub_parsers = self.parser.add_subparsers(title='sub-commands for {0} module'.format(name),
                                                      description='Specify what to do with {0} module'.format(name),
                                                      help='open/view/edit/save'
                                                      )

        self.add_subparsers()

    def add_subparsers(self):
        for command in self.sub_commands:
            parser = self.sub_parsers.add_parser(command.name,
                                                 description=command.description,
                                                 help=command.help
                                                 )
            # adding mutually exclusive group
            if command.mutually_exclusive_group:
                command.add_mutually_exclusive_groups(parser)

            for arg in command.args:
                if arg.group and arg.group in command.mutually_exclusive_group:
                    parser = command.mutually_exclusive_group[arg.group]

                if arg.action in ['store_true', 'store_false']:
                    parser.add_argument(
                        *arg.name,
                        help=arg.help,
                        action=arg.action
                    )
                else:
                    parser.add_argument(
                        *arg.name,
                        help=arg.help,
                        type=arg.type,
                        choices=arg.choices,
                        action=arg.action,
                        required=arg.required
                    )
