import sys

from gui.main import QApplication, MainWindow
from database import connection

connection(provider="sqlite", settings={"filename": "db.sqlite", "create_db": True})

app = QApplication(sys.argv)
screen = MainWindow()
screen.show()
sys.exit(app.exec_())
