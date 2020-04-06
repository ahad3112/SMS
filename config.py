import os
import sys

# Working directory
WORKING_DIR = os.getcwd()
HOME_DIR = os.path.split(sys.argv[0])[0]

# database
DB_NAME = os.path.join(HOME_DIR, 'sms.db')

TABLES = {
    'links': 'links',
}
DB_TABLES = {
    TABLES['links']: 'create table {0} (session char(50), command char(50), links char(200))'.format(TABLES['links']),
}


# Supported Browsers
SUPPORTED_BROWSERS = {'Chrome': 'open -a Google\\ Chrome ',
                      'Safari': 'open -a Safari ',
                      }
