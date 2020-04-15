import sys


class Display:
    line_width = 161
    msg_width = 120
    info_width = line_width - msg_width
    header_height = 5

    @staticmethod
    def dataframe(*, headers, rows):
        try:
            # Extra one is required for row number
            min_column_width = Display.line_width // (len(rows[0]) + 1)
        except Exception:
            Display.info(what='No record available to display', info=' [RETURNING]')
            return
        else:
            # Leave the remaining_line_width
            remaining_line_width = Display.line_width - min_column_width * (len(rows[0]) + 1)
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

        print('\n*** Some column might have been truncated to fit in the column width.')

    @staticmethod
    def input(*, keys, actions):
        Display.title(title='Edit option')

    @staticmethod
    def title(*, title):
        print('-' * Display.line_width)
        title = '{0!s:^{1}}'.format(' '.join(x.upper() for x in title), Display.line_width)
        print(title)
        print('-' * Display.line_width)

    @staticmethod
    def progress_bar(*, total, step, completed):
        step_length = (Display.msg_width - 2) // total
        progress_bar_format = '[{0:<{1}}]{2:>{3}}'
        sys.stdout.write('\r')
        if completed.startswith('100'):
            sys.stdout.write(progress_bar_format.format(
                '=' * (Display.msg_width - 2),
                Display.msg_width - 2,
                completed,
                Display.info_width)
            )
        else:
            sys.stdout.write(progress_bar_format.format(
                '=' * (step_length * step - 1) + '>',
                Display.msg_width - 2,
                completed,
                Display.info_width)
            )

    @staticmethod
    def info(what='', info='W', end='\n'):
        print('{0:-<{1}}{2:->{3}}'.format(what, Display.msg_width, info, Display.info_width), end=end)

    @staticmethod
    def success(what='', info='✓', end='\n'):
        print('{0:-<{1}}{2:->{3}}'.format(what, Display.msg_width, info, Display.info_width), end=end)

    @staticmethod
    def warning(what='', info='W', end='\n'):
        print('{0:-<{1}}{2:->{3}}'.format(what, Display.msg_width, info, Display.info_width), end=end)

    @staticmethod
    def fail(what='', info='X'):
        print('{0:><{1}}{2:>>{3}}'.format(what, Display.msg_width, info, Display.info_width))
