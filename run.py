import sys

from gui.main import QApplication, MainWindow

app = QApplication(sys.argv)
screen = MainWindow()
screen.show()
sys.exit(app.exec_())
