'''
For the best experience put a folder 'memes' into the same folder where 'gui.py' is.
Add several files with different extensions (see IMAGE_EXTENSIONS and VIDEO_EXTENSIONS) in it.
Put a file named '2.gif' in folder 'memes' to see the entire program structure.
'''


##TODO:
# Add folder tree (process all images in subfolders) upon folderTreeCheckbox.isChecked()
# Show image upon clicking its name (depending on extension, e.g: jpeg: QPixmap, gif: QMovie)
# "Show similar" checkbox
# Menu settings
# Table sorting
# GUI updates (stretching, scales, fixed sizes, etc.)
# Fix QVector warning


import sys
import os
from   PyQt5.QtWidgets import *
from   PyQt5.QtGui	   import *
from   PyQt5.QtCore	   import *


IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.bmp', '.ico', '.gif')
VIDEO_EXTENSIONS = ('.mp4', '.webm', '.3gp')


class ProcessingThread(QThread):
	progressTrigger = pyqtSignal(float)
	finishedTrigger = pyqtSignal()
	
	def __init__(self, folderField, imageListTable, videoListTable, folderTreeCheckbox):
		QThread.__init__(self)
		self.folderField = folderField
		self.imageListTable = imageListTable
		self.videoListTable = videoListTable
		self.folderTreeCheckbox = folderTreeCheckbox
			
	
	def run(self):
		rowImages, rowVideos = 0, 0
		if self.folderTreeCheckbox.isChecked():
			print('HERE GOES SOME CODE')														# TODO
		
		else:
			files = os.listdir(self.folderField.text())											# list of folder content 
			images = [file for file in files if file.endswith(IMAGE_EXTENSIONS)]				# exclude subfolders and unwanted extensions
			videos = [file for file in files if file.endswith(VIDEO_EXTENSIONS)]
			for image in images:
				self.sleep(1)																	# process simulation (TODO: delete)
				self.imageListTable.setRowCount(rowImages + 1)
				self.imageListTable.setItem(rowImages, 0, QTableWidgetItem(image))
				self.imageListTable.setItem(rowImages, 1, QTableWidgetItem(image.split('.')[-1]))
				rowImages += 1
				value = (rowImages + rowVideos) / len(images + videos) * 100
				self.progressTrigger.emit(value)
				
			for video in videos:
				self.sleep(1)																	# process simulation (TODO: delete)
				self.videoListTable.setRowCount(rowVideos + 1)
				self.videoListTable.setItem(rowVideos, 0, QTableWidgetItem(video))
				self.videoListTable.setItem(rowVideos, 1, QTableWidgetItem(video.split('.')[-1]))
				rowVideos += 1
				value = (rowImages + rowVideos) / len(images + videos) * 100
				self.progressTrigger.emit(value)	
			
		self.finishedTrigger.emit()

	
class MainWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		self.setWindowTitle('T e b y g')
		
		self.statusBar = QStatusBar()
		self.setStatusBar(self.statusBar)
		
		menu = QMenuBar()
		self.setMenuBar(menu)
		
		fileMenu = menu.addMenu('&File')
		fileMenu.addAction('Exit', self.close)
		
		settingsMenu = menu.addMenu('&Settings')
		settingsMenu.addAction('DB settings')
		settingsMenu.addAction('Indexing settings')
		settingsMenu.addAction('Matching settings')
		settingsMenu.addSeparator()
		settingsMenu.addAction('Other')
		
		self.window = Window(self.statusBar)
		self.setCentralWidget(self.window)
		
		

class Window(QWidget):
	def __init__(self, statusBar):
		super().__init__()
		self.statusBar = statusBar																# get that status bar to work with
				
		self.folderField = QLineEdit()
		self.folderButton = QPushButton()
		self.folderTreeCheckbox = QCheckBox('Consider subfolders')
		self.processButton = QPushButton('Start')
		self.progressBar = QProgressBar()
		self.tableTabs = QTabWidget()
		self.imageListTable = QTableWidget()
		self.videoListTable = QTableWidget()
		self.showCheckbox = QCheckBox('Show similar')
		self.imageField = QLabel()
		
		self.folderField.setEnabled(False)
		
		self.folderButton.setIcon(self.style().standardIcon(QStyle.SP_DialogOpenButton))
		self.folderButton.clicked.connect(self.set_folder)
		
		self.processButton.clicked.connect(self.process_images)
		
		self.progressBar.setAlignment(Qt.AlignCenter)
		
		self.imagesTab = self.tableTabs.insertTab(0, self.imageListTable, 'Images')
		self.videosTab = self.tableTabs.insertTab(1, self.videoListTable, 'Videos')
				
		self.imageListTable.setColumnCount(2)
		self.imageListTable.setHorizontalHeaderLabels(['List of images', 'Extension'])
		self.imageListTable.resizeColumnsToContents()
		self.imageListTable.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
		
		self.videoListTable.setColumnCount(2)
		self.videoListTable.setHorizontalHeaderLabels(['List of videos', 'Extension'])
		self.videoListTable.resizeColumnsToContents()
		self.videoListTable.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
		
		
		## Show picture (test):
		#self.imageField.setPixmap(QPixmap(r'memes/1.jpg').scaled(500, 500, Qt.KeepAspectRatio,Qt.SmoothTransformation))
		
		## Show gif (test):
		self.gif = QMovie(r'memes/2.gif')
		self.imageField.setMovie(self.gif)
		self.gif.start()
		
		
		self.showCheckbox.clicked.connect(self.show_similar)
				
		grid = QGridLayout()
		grid.addWidget(self.folderField, 0, 0)
		grid.addWidget(self.folderButton, 0, 1)
		grid.addWidget(self.folderTreeCheckbox, 1, 0)
		grid.addWidget(self.processButton, 2, 0, 2, 2)
		grid.addWidget(self.progressBar, 3, 0, 3, 2)
		grid.addWidget(self.tableTabs, 0, 2, 3, 2)
		grid.addWidget(self.showCheckbox, 4, 2)
		grid.addWidget(self.imageField, 0, 4, 3, 4)
		self.setLayout(grid)
				
		self.thread = ProcessingThread(self.folderField, self.imageListTable, self.videoListTable, self.folderTreeCheckbox)
		self.thread.progressTrigger.connect(self.update_progressbar)
		self.thread.finishedTrigger.connect(self.finished)
		
	
	def set_folder(self):																		# get folder full of images
		folderPath = QFileDialog.getExistingDirectory(self)
		self.folderField.setText(folderPath)
		self.statusBar.clearMessage()
		
		
	def process_images(self):																	# start thread and fill the table with those images
		self.statusBar.clearMessage()
		
		if self.folderField.text() == '':
			self.statusBar.setStyleSheet('color: red')
			self.statusBar.showMessage('Please choose a directory')
			return None
		
		if not self.thread.isRunning():
			self.thread.start()
			self.processButton.setText('Stop')
		
		elif self.thread.isRunning():
			self.thread.terminate()
			self.processButton.setText('Start')
			self.update_progressbar(0)
			
			
	def update_progressbar(self, value):														# update progress bar with values via signal
		self.progressBar.setValue(value)
	
	
	def finished(self):																			# thread done and ded
		self.statusBar.setStyleSheet('color: black')
		self.statusBar.showMessage('Finished!')
		self.processButton.setText('Start')
	
		
	def show_similar(self):																		# TODO
		if self.showCheckbox.isChecked():
			print('SHOW SIMILAR ONLY')
		else:
			print('SHOW ALL IMAGES')
		
		
app = QApplication(sys.argv)
screen = MainWindow()
screen.show()
sys.exit(app.exec_())
