import logging
from logging.config import fileConfig

logging.config.fileConfig('logger/logging.conf')

# create logger for info messages
BackInfoLogger = logging.getLogger('BackInfoLogger')
# create logger for errors messages
BackErrorsLogger = logging.getLogger('BackErrorsLogger')
