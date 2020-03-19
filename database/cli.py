from core.commands import Command
from core.arguments import Argument


class DatabaseCLI:
  '''
  This class add the subparser relates to Database (clear db and drop db)
  '''
  # mutually_exclusive_group : good idea to used set to avoid duplicate group name
  sub_commands = {
      Command(name='drop',
              help='This module will drop the database table/tables',
              description='Drop database table/tables',
              args=[Argument(name=('-y', '--yes'),
                             help='Confirm database table/tables to be cleared ',
                             action='store_true'),
                    Argument(name=('-t', '--table'),
                             help='Table name to be drop.',
                             group='one_or_all'),
                    Argument(name=('-a', '--all'),
                             help='Drop all tables',
                             action='store_true',
                             group='one_or_all'),
                    ],
              mutually_exclusive_group={'one_or_all': None, }),
      Command(name='delete',
              help='This module will delete the database',
              description='Delete the whole database',
              args=[Argument(name=('-y', '--yes'),
                             help='Confirm database to be deleted ',
                             action='store_true'),
                    ]),
      Command(name='tables',
              description='Use this to get all database tables. Will add further argument -a(all), -n(--name, matching)',
              help='Return all available tables in the database.',
              args=[]),
  }

  def __init__(self, *, sub_parsers, command='db'):
    self.command = command
    self.parser = sub_parsers.add_parser(self.command,
                                         description='Database management',
                                         help='This is help for Database management command "db"'
                                         )
    self.sub_parsers = self.parser.add_subparsers(title='Database management sub-commands',
                                                  description='''These commands will deal with current database.
                                                  For example: clear db/table, drop db/table.
                                                  '''
                                                  )

    self.__add_parsers()

  def __add_parsers(self):
    for command in self.sub_commands:
      parser = self.sub_parsers.add_parser(command.name,
                                           description=command.description,
                                           help=command.help)

      # adding mutually exclusive group
      command.add_mutually_exclusive_groups(parser)

      for arg in command.args:
        if arg.group and arg.group in command.mutually_exclusive_group:
          parser = command.mutually_exclusive_group.get(arg.group, parser)

        parser.add_argument(*arg.name, help=arg.help, action=arg.action)
