import os
import logging
from logging.config import fileConfig

os.makedirs("logs", exist_ok=True)

logging.config.fileConfig("logger/logging.conf")

# create logger for info messages
BackInfoLogger = logging.getLogger("BackInfoLogger")
# create logger for errors messages
BackErrorsLogger = logging.getLogger("BackErrorsLogger")
