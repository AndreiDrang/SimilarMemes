import sys
import traceback

from gui import QApplication, MainWindow
from logger import BackInfoLogger, BackErrorsLogger

import database


if __name__ == "__main__":
    try:
        # connect to DB
        database.connection()

        # start GUI
        app = QApplication(sys.argv)
        screen = MainWindow()
        screen.show()

        BackInfoLogger.info("App success starting")

        sys.exit(app.exec_())

    except Exception:
        BackErrorsLogger.critical(traceback.format_exc())
