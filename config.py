import os

# Debug option
DEBUG = False

# Working directory
WORKING_DIR = os.getcwd()

# database
DB_NAME = os.path.join(WORKING_DIR, 'sms.db')

TABLES = {
    'links': 'links',
}
DB_TABLES = {
    TABLES['links']: 'create table {0} (session char(50), command char(50), links char(200))'.format(TABLES['links']),
}


# Supported Browsers
SUPPORTED_BROWSERS = {'Google Chrome': 'open -a Google\\ Chrome ',
                      'Safari': 'open -a Safari ',
                      }

# For testing
# SUPPORTED_BROWSERS = {
#     'Safari': b'open -a Safari ',
# }

# session's action
# SESSION_ACTIONS = ('save', 'open', 'view', 'edit')
