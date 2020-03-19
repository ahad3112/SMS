class Argument:
    def __init__(self, *, name, type=None, help='help',
                 choices=None, action=None, group=None):
        self.name = name
        self.type = type
        self.help = help
        self.action = action
        self.choices = choices
        self.group = group
