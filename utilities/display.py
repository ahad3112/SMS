from colorama import Fore, Back, Style


class Display:
    line_width = 130
    msg_width = 100
    info_width = line_width - msg_width
    header_height = 5

    @staticmethod
    def dataframe(*, headers, rows):
        try:
            # Extra one is required for row number
            min_column_width = self.line_width // (len(headers) + 1)
        except Exception:
            try:
                # Extra one is required for row number
                min_column_width = Display.line_width // (len(rows[0]) + 1)
            except Exception:
                print('No Header of Data was provided for display.....')
        finally:
            print('min_column_width {0}'.format(min_column_width))
            remaining_line_width = Display.line_width - min_column_width
            column_format = '{0!s:{1}<{2}}'
            headers.insert(0, 'No.')
            # headers
            for header in headers:
                print(column_format.format(header, '', min_column_width), end='')
            print()

            # headers underline
            for header in headers:
                print(column_format.format('=' * len(header), '', min_column_width), end='')
            print()

            # printing the row data
            for (index, row) in enumerate(rows):
                print(column_format.format(index, '', min_column_width), end='')
                for column in row:
                    print(column_format.format(column[:min_column_width + 1], '', min_column_width), end='')
                print('\r')

        print('\n** Some column might have been truncated to fit in the column width.')

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
