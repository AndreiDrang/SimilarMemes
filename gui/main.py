##TODO:
# "Show similar" checkbox
# Menu settings

import os
from PIL import Image
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *

from gui import json_settings
from indexing import index_folder_files


# The global to store image/video paths:
ITEM_PATH_DICT = {}


class ProcessingThread(QThread):
    progressTrigger = pyqtSignal(float)
    finishedTrigger = pyqtSignal()

    def __init__(self, folderField, imageListTable, videoListTable, folderTreeCheckbox):
        QThread.__init__(self)
        self.folderField = folderField
        self.imageListTable = imageListTable
        self.videoListTable = videoListTable
        self.folderTreeCheckbox = folderTreeCheckbox

    # The process to fill the image/video tables with image/video names and ITEM_PATH_DICT with their paths:
    def run(self):
        rowImages, rowVideos = 0, 0

        ## Processes all multimedia in the main folder and its sub-folders as well (depending on depth from settings):
        if self.folderTreeCheckbox.isChecked():
            images, videos = index_folder_files(
                self.folderField.text(),
                max_depth=json_settings.json_read("folderDepth"),
            )

        ## Processes multimedia in the selected folder only:
        else:
            images, videos = index_folder_files(self.folderField.text(), max_depth=0)

        for image in images:
            self.sleep(1)  # process simulation (TODO: delete)
            self.imageListTable.setRowCount(rowImages + 1)
            self.imageListTable.setItem(rowImages, 0, QTableWidgetItem(image[0]))
            self.imageListTable.setItem(
                rowImages, 1, QTableWidgetItem((image[0].split(".")[-1]).lower())
            )
            rowImages += 1
            progress = (rowImages + rowVideos) / len(images + videos) * 100
            self.progressTrigger.emit(progress)
            ITEM_PATH_DICT[image[0]] = os.path.join(image[1], image[0])

        for video in videos:
            self.sleep(1)  # process simulation (TODO: delete)
            self.videoListTable.setRowCount(rowVideos + 1)
            self.videoListTable.setItem(rowVideos, 0, QTableWidgetItem(video[0]))
            self.videoListTable.setItem(
                rowVideos, 1, QTableWidgetItem((video[0].split(".")[-1]).lower())
            )
            rowVideos += 1
            progress = (rowImages + rowVideos) / len(images + videos) * 100
            self.progressTrigger.emit(progress)
            ITEM_PATH_DICT[video[0]] = os.path.join(video[1], video[0])

        self.finishedTrigger.emit()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("T e b y g")

        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        menu = QMenuBar()
        self.setMenuBar(menu)

        fileMenu = menu.addMenu("&File")
        fileMenu.addAction("Exit", self.close)

        settingsMenu = menu.addMenu("&Settings")
        settingsMenu.addAction("DB settings")
        settingsMenu.addAction("Indexing settings", self.show_indexing_settings)
        settingsMenu.addAction("Matching settings")
        settingsMenu.addSeparator()
        settingsMenu.addAction("Other")

        self.window = Window(self.statusBar)
        self.setCentralWidget(self.window)

    def show_indexing_settings(self):
        self.indexingSettings = IndexingSettings()
        self.indexingSettings.show()


class Window(QWidget):
    def __init__(self, statusBar):
        super().__init__()

        ## Gets status bar from QMainWindow:
        self.statusBar = statusBar

        ## Initializes all window elements:
        self.folderField = QLineEdit()
        self.folderButton = QPushButton()
        self.folderTreeCheckbox = QCheckBox("Include sub-folders")
        self.processButton = QPushButton("Start")
        self.progressBar = QProgressBar()
        self.tableTabs = QTabWidget()
        self.imageListTable = QTableWidget()
        self.videoListTable = QTableWidget()
        self.showCheckbox = QCheckBox("Show similar")
        self.imageField = QLabel()
        self.videoField = QVideoWidget()
        self.videoPlayer = QMediaPlayer()

        ## Adjusts settings for the window elements:
        self.folderField.setEnabled(False)

        self.folderButton.setIcon(self.style().standardIcon(QStyle.SP_DialogOpenButton))
        self.folderButton.clicked.connect(self.set_folder)

        self.processButton.clicked.connect(self.process_files)
        self.processButton.setFixedWidth(100)

        self.progressBar.setAlignment(Qt.AlignCenter)

        self.imagesTab = self.tableTabs.insertTab(0, self.imageListTable, "Images")
        self.videosTab = self.tableTabs.insertTab(1, self.videoListTable, "Videos")

        self.imageListTable.setColumnCount(2)
        self.imageListTable.setHorizontalHeaderLabels(["List of images", "Extension"])
        self.imageListTable.setColumnWidth(0, 227)
        self.imageListTable.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.imageListTable.setSortingEnabled(True)

        self.imageListTable.cellClicked.connect(self.show_image)

        self.videoListTable.setColumnCount(2)
        self.videoListTable.setHorizontalHeaderLabels(["List of videos", "Extension"])
        self.videoListTable.setColumnWidth(0, 227)
        self.videoListTable.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.videoListTable.setSortingEnabled(True)
        self.videoListTable.cellClicked.connect(self.show_video)

        self.showCheckbox.clicked.connect(self.show_similar)

        ## Places the window elements on the window:
        ### Top-left cell of main grid box:
        subGridBox = QWidget()
        subGrid = QGridLayout()
        subGrid.addWidget(self.folderField, 0, 0)
        subGrid.addWidget(self.folderButton, 0, 1)
        subGrid.addWidget(self.folderTreeCheckbox, 1, 0)
        subGrid.addWidget(self.processButton, 2, 0, 1, 2, Qt.AlignCenter)
        subGrid.addWidget(self.progressBar, 3, 0, 1, 2)
        subGridBox.setLayout(subGrid)

        ### Main grid box:
        self.mainGrid = QGridLayout()
        self.mainGrid.addWidget(subGridBox, 0, 0)
        self.mainGrid.addWidget(self.tableTabs, 1, 0)
        self.mainGrid.addWidget(self.showCheckbox, 2, 0)
        self.mainGrid.addWidget(self.imageField, 0, 1, 2, 1, Qt.AlignCenter)
        self.mainGrid.addWidget(self.videoField, 0, 1, 2, 1)

        self.mainGrid.setColumnMinimumWidth(0, 350)
        self.mainGrid.setRowMinimumHeight(1, 500)
        self.mainGrid.setColumnStretch(1, 1)

        self.setLayout(self.mainGrid)

        ## Creates a QThread instance:
        self.thread = ProcessingThread(
            self.folderField,
            self.imageListTable,
            self.videoListTable,
            self.folderTreeCheckbox,
        )
        self.thread.progressTrigger.connect(self.update_progressbar)
        self.thread.finishedTrigger.connect(self.finish_thread)

    # Get a folder full of multimedia files to work with
    def set_folder(self):
        self.folderPath = QFileDialog.getExistingDirectory(self)
        if self.folderPath == "":
            self.folderPath = self.folderField.text()
        self.folderField.setText(self.folderPath)
        self.statusBar.clearMessage()

    # Start the thread and fill the table with those files
    def process_files(self):
        ## Clears both tables upon restarting function:
        self.imageListTable.clearContents()
        self.imageListTable.setRowCount(0)
        self.videoListTable.clearContents()
        self.videoListTable.setRowCount(0)

        self.statusBar.setStyleSheet("color: black")
        self.statusBar.showMessage("Processing...")

        if self.folderField.text() == "":
            self.statusBar.setStyleSheet("color: red")
            self.statusBar.showMessage("Please choose a directory")
            return None

        if not self.thread.isRunning():
            self.thread.start()
            self.processButton.setText("Stop")

        elif self.thread.isRunning():
            self.thread.terminate()
            self.processButton.setText("Start")
            self.update_progressbar(0)

    # Update the progress bar with values via pyqtSignal
    def update_progressbar(self, progress):
        self.progressBar.setValue(progress)

    # Thread done and ded
    def finish_thread(self):
        self.statusBar.setStyleSheet("color: black")
        self.statusBar.showMessage("Finished!")
        self.processButton.setText("Start")

    # Show an image upon clicking its name in the table
    def show_image(self, row, column):
        imageItem = self.imageListTable.item(row, column)

        ## Prevents from KeyError when clicking the second column:
        if imageItem.text() in ITEM_PATH_DICT:
            imageItemPath = ITEM_PATH_DICT[imageItem.text()]

            ## Removes a video from screen if shown:
            self.videoPlayer.stop()
            self.videoField.hide()
            self.imageField.show()

            ## Shows animated images:
            if imageItemPath.lower().endswith("gif"):
                gif = QMovie(imageItemPath)
                gifSize = QSize(*self.smooth_gif_resize(imageItemPath, 600, 600))
                gif.setScaledSize(gifSize)
                self.imageField.setMovie(gif)
                gif.start()

            ## Shows static images:
            else:
                self.imageField.setPixmap(
                    QPixmap(imageItemPath).scaled(
                        600, 600, Qt.KeepAspectRatio, Qt.SmoothTransformation
                    )
                )

    # Show a video upon clicking its name in the table
    def show_video(self, row, column):
        videoItem = self.videoListTable.item(row, column)
        self.mainGrid.setColumnMinimumWidth(1, 800)

        ## Prevents from KeyError when clicking the second column:
        if videoItem.text() in ITEM_PATH_DICT:
            videoItemPath = ITEM_PATH_DICT[videoItem.text()]
            videoContent = QMediaContent(QUrl.fromLocalFile(videoItemPath))
            self.videoPlayer.setMedia(videoContent)
            self.videoPlayer.setVideoOutput(self.videoField)

            ## Removes an image from screen if shown and starts video:
            self.imageField.clear()
            self.imageField.hide()
            self.videoField.show()
            self.videoPlayer.play()

    # Show similar multimedia when checkbox is set
    def show_similar(self):  # TODO
        if self.showCheckbox.isChecked():
            print("SHOW SIMILAR ONLY")
        else:
            print("SHOW ALL IMAGES")

    # An amazing workaround for gif resizing procedure because PyQt's native one doesn't work for some reason:
    def smooth_gif_resize(self, gif, frameWidth, frameHeight):
        gif = Image.open(gif)
        gifWidth0, gifHeight0 = gif.size

        widthRatio = frameWidth / gifWidth0
        heightRatio = frameHeight / gifHeight0

        if widthRatio >= heightRatio:
            gifWidth1 = gifWidth0 * heightRatio
            gifHeight1 = frameHeight
            return gifWidth1, gifHeight1

        gifWidth1 = frameWidth
        gifHeight1 = gifHeight0 * widthRatio
        return gifWidth1, gifHeight1


# Allows to set a custom folder depth value in the json file:
class IndexingSettings(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Indexing settings")
        self.setFixedSize(250, 100)

        self.folderDepthLabel = QLabel("Folder depth:")
        self.folderDepthField = QLineEdit()
        self.okButton = QPushButton("Ok")

        self.folderDepthField.setText(str(json_settings.json_read("folderDepth")))
        self.okButton.clicked.connect(self.ok_event)

        self.grid = QGridLayout()
        self.grid.addWidget(self.folderDepthLabel, 0, 0)
        self.grid.addWidget(self.folderDepthField, 0, 1)
        self.grid.addWidget(self.okButton, 1, 1)
        self.setLayout(self.grid)

    ## Updates the json settings with the new folder depth value:
    def ok_event(self):
        json_settings.json_update("folderDepth", self.folderDepthField.text())
        self.close()
