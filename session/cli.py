from core.commands import Command
from core.arguments import Argument


class SessionCLI:
    sub_commands = [
        Command(name='open',
                help='open a saved session',
                description='This module will open a saved session',
                args=[
                    Argument(
                        name=('name',),
                        type=str,
                        help='Later',
                    ),
                ]),
        Command(name='view',
                help='view a saved session',
                description='This module display a saved session',
                args=[
                    Argument(
                        name=('name',),
                        type=str,
                        help='Later'
                    ),
                ]),
        Command(name='edit',
                help='edit a saved session',
                description='This module helps edit a saved session',
                args=[
                    Argument(
                        name=('name',),
                        type=str,
                        help='Later'
                    ),
                ]),
        Command(name='save',
                help='saves current session',
                description='This module will save the current session',
                args=[
                    Argument(
                        name=('-n', '--name'),
                        type=str,
                        help='Later'
                    ),
                    Argument(
                        name=('-l', '--links',),
                        type=str,
                        help='Saves links',
                        action='store_true'
                    ),
                ]),
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

            for arg in command.args:
                if arg.action in ['store_true', 'store_false']:
                    parser.add_argument(*arg.name, help=arg.help, action=arg.action)
                else:
                    parser.add_argument(*arg.name, help=arg.help, type=arg.type, choices=arg.choices, action=arg.action)
