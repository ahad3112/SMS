from colorama import Fore, Back, Style


class Display:
    line_width = 130
    msg_width = 100
    info_width = line_width - msg_width
    header_height = 5

    @staticmethod
    def list_data(*, headers=None, data):
        column_format = '{0: ^{1}}'
        if data and headers:
            column_len = Display.line_width // len(headers)
            for header in headers:
                head = Style.BRIGHT + Fore.RED + header + Style.RESET_ALL
                print(column_format.format(head, column_len), end='')
            print()

            # adding underline to the header
            for header in headers:
                underline = Style.BRIGHT + Fore.BLUE + '=' * (column_len // 2) + Style.RESET_ALL
                print(column_format.format(underline, column_len), end='')
            print()
        elif data:
            column_len = Display.line_width // len(data[0])
        else:
            Display.warning(what='Nothing to display ', info='[ No Table Exists ]')

        # list the all available
        for columns in data:
            if headers and len(headers) != len(columns):
                raise ValueError('Length of headers did not match with the length of columns in {0}.'.format(
                    Display.list_data.__name__
                ))
            for column in columns:
                column = Style.BRIGHT + Fore.BLUE + str(column) + Style.RESET_ALL
                print(column_format.format(str(column), column_len), end='')
            print()

    @staticmethod
    def header(*, head):
        return Fore.CYAN + head + Style.RESET_ALL

    @staticmethod
    def title(*, title):
        title = Style.BRIGHT + Fore.BLUE + title + Style.RESET_ALL
        title = '{0: ^{1}}'.format(title, Display.line_width)
        print('-' * Display.line_width)
        print(title)
        print('-' * Display.line_width)
        print()

    @staticmethod
    def info(what='', info='W'):
        info = Style.BRIGHT + Fore.BLUE + info + Style.RESET_ALL
        print('{0:-<{1}} : {2:>{3}}'.format(what, Display.msg_width, info, Display.info_width))

    @staticmethod
    def success(what='', info='✓', end='\n'):
        info = Style.BRIGHT + Fore.YELLOW + info + Style.RESET_ALL
        print('{0:><{1}} : {2:>{3}}'.format(what, Display.msg_width, info, Display.info_width), end=end)

    @staticmethod
    def warning(what='', info='W'):
        info = Style.BRIGHT + Fore.YELLOW + info + Style.RESET_ALL
        print('{0:-<{1}} : {2:>{3}}'.format(what, Display.msg_width, info, Display.info_width))

    @staticmethod
    def fail(what='', info='X'):
        info = Style.BRIGHT + Fore.YELLOW + info + Style.RESET_ALL
        print('{0:><{1}} : {2:>{3}}'.format(what, Display.msg_width, info, Display.info_width))
