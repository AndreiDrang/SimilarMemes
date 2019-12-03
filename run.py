import sys
import logging
import traceback

from PyQt5.QtWidgets import QApplication

from logger import prepare_logging

prepare_logging()

from gui import MainWindow
import database


logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        # connect to DB
        database.connection()

        # start GUI
        app = QApplication(sys.argv)
        screen = MainWindow()
        screen.show()

        logger.info("App success starting")

        sys.exit(app.exec_())

    except Exception:
        logger.critical(traceback.format_exc())
