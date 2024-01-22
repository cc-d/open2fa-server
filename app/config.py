import os
from pyshared import typed_evar

TESTING = typed_evar("TESTING", False)
DIR_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SQLITE_DB_PATH = os.path.join(DIR_ROOT, 'test.db' if TESTING else 'sqlite.db')

DB_URI = f'sqlite:///{SQLITE_DB_PATH}'
