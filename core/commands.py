import argparse


class Command:
    def __init__(self, *, name, help, description, args, mutually_exclusive_group={}):
        self.name = name
        self.help = help
        self.description = description
        self.args = args
        self.mutually_exclusive_group = mutually_exclusive_group

    def add_mutually_exclusive_groups(self, parser=None):
        if parser and self.mutually_exclusive_group:
            for group in self.mutually_exclusive_group:
                self.mutually_exclusive_group[group] = parser.add_mutually_exclusive_group()
