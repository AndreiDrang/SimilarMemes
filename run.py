import sys

from gui.main import QApplication, MainWindow
import database


if __name__=='__main__':

    # connect to DB
    database.connection()

    # start GUI
    app = QApplication(sys.argv)
    screen = MainWindow()
    screen.show()
    sys.exit(app.exec_())
