# TODO:
# Thread processing duplicates
# Menu settings

import os
from PIL import Image
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *

from gui import json_settings
from indexing import index_folder_files, reindex_image_files, reindex_video_files


# Dict containment -> ID:[FILE_NAME, EXTENSION, FILE_FULL_PATH]
IMAGE_PATH_DICT = {}
VIDEO_PATH_DICT = {}


class ProcessingThread(QThread):
    progressTrigger = pyqtSignal(float)
    finishedTrigger = pyqtSignal()

    def __init__(self, folderField, imageListTable, videoListTable, folderTreeCheckbox):
        QThread.__init__(self)
        self.folderField = folderField
        self.imageListTable = imageListTable
        self.videoListTable = videoListTable
        self.folderTreeCheckbox = folderTreeCheckbox

    # The process to fill the image/video tables with image/video names
    # and ITEM_PATH_DICT with their paths:
    def run(self):
        rowImages, rowVideos = 0, 0

        # Reindex already exist folders and files; Image and Video files
        reindex_image_files()
        reindex_video_files()

        # Processes all multimedia in the main folder and its sub-folders as well
        # (depending on depth from settings):
        if self.folderTreeCheckbox.isChecked():
            images, videos = index_folder_files(
                self.folderField.text(),
                max_depth=json_settings.json_read("folderDepth"),
            )

        # Processes multimedia in the selected folder only:
        else:
            images, videos = index_folder_files(self.folderField.text(), max_depth=0)

        for image in images:
            self.sleep(1)  # process simulation (TODO: delete)

            rowImages += 1
            imageId = str(rowImages)
            IMAGE_PATH_DICT[imageId] = [image[0], (image[0].split(".")[-1]).lower(), os.path.join(image[1], image[0])]
            self.imageListTable.setRowCount(rowImages)
            self.imageListTable.setItem(rowImages-1, 0, QTableWidgetItem(imageId))
            self.imageListTable.setItem(rowImages-1, 1, QTableWidgetItem(image[0]))
            self.imageListTable.setItem(rowImages-1, 2, QTableWidgetItem(IMAGE_PATH_DICT[imageId][1]))

            duplicateIcon = QTableWidgetItem()
            duplicateIcon.setIcon(
                QWidget().style().standardIcon(QStyle.SP_FileDialogContentsView)
            )
            self.imageListTable.setItem(rowImages-1, 3, duplicateIcon)

            progress = (rowImages + rowVideos) / len(images + videos) * 100
            self.progressTrigger.emit(progress)

        for video in videos:
            self.sleep(1)  # process simulation (TODO: delete)

            rowVideos += 1
            videoId = str(rowVideos)
            VIDEO_PATH_DICT[videoId] = [video[0], (video[0].split(".")[-1]).lower(), os.path.join(video[1], video[0])]
            self.videoListTable.setRowCount(rowVideos)
            self.videoListTable.setItem(rowVideos - 1, 0, QTableWidgetItem(videoId))
            self.videoListTable.setItem(rowVideos - 1, 1, QTableWidgetItem(video[0]))
            self.videoListTable.setItem(rowVideos - 1, 2, QTableWidgetItem(VIDEO_PATH_DICT[videoId][1]))

            duplicateIcon = QTableWidgetItem()
            duplicateIcon.setIcon(
                QWidget().style().standardIcon(QStyle.SP_FileDialogContentsView)
            )
            self.videoListTable.setItem(rowVideos, 3, duplicateIcon)

            progress = (rowImages + rowVideos) / len(images + videos) * 100
            self.progressTrigger.emit(progress)

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

        # Saves multiple duplicate windows references:
        self.duplicateRefs = {}

        # Gets status bar from QMainWindow:
        self.statusBar = statusBar

        # Initializes all window elements:
        self.folderField = QLineEdit()
        self.folderButton = QPushButton()
        self.folderTreeCheckbox = QCheckBox("Include sub-folders")
        self.processButton = QPushButton("Process media files")
        self.duplicateButton = QPushButton("Find duplicates")
        self.progressBar = QProgressBar()
        self.tableTabs = QTabWidget()
        # init main images list table
        self.imageListTable = QTableWidget()
        # set main images list table fields unchanged
        self.imageListTable.setEditTriggers(QTableWidget.NoEditTriggers)
        # init main videos list table
        self.videoListTable = QTableWidget()
        # set main videos list table fields unchanged
        self.videoListTable.setEditTriggers(QTableWidget.NoEditTriggers)
        self.imageField = QLabel()
        self.videoField = QVideoWidget()
        self.videoPlayer = QMediaPlayer()

        # Adjusts settings for the window elements:
        self.folderField.setEnabled(False)

        self.folderButton.setIcon(self.style().standardIcon(QStyle.SP_DialogOpenButton))
        self.folderButton.clicked.connect(self.set_folder)

        self.processButton.clicked.connect(self.process_files)
        self.processButton.setFixedWidth(150)

        self.duplicateButton.clicked.connect(self.find_duplicates)
        self.duplicateButton.setFixedWidth(150)

        self.progressBar.setAlignment(Qt.AlignCenter)

        self.imagesTab = self.tableTabs.insertTab(0, self.imageListTable, "Images")
        self.videosTab = self.tableTabs.insertTab(1, self.videoListTable, "Videos")

        self.imageListTable.setColumnCount(4)
        self.imageListTable.setHorizontalHeaderLabels(
            ["ID", "File name", "Extension", ""]
        )
        self.imageListTable.verticalHeader().setVisible(False)

        self.imageListTable.setColumnWidth(0, 25)
        self.imageListTable.setColumnWidth(1, 165)
        self.imageListTable.setColumnWidth(3, 27)
        self.imageListTable.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.imageListTable.setSortingEnabled(True)
        self.imageListTable.cellClicked.connect(self.show_image)

        self.videoListTable.setColumnCount(4)
        self.videoListTable.setHorizontalHeaderLabels(
            ["ID", "File name", "Extension", ""]
        )
        self.videoListTable.verticalHeader().setVisible(False)

        self.videoListTable.setColumnWidth(0, 25)
        self.videoListTable.setColumnWidth(1, 165)
        self.videoListTable.setColumnWidth(3, 27)
        self.videoListTable.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.videoListTable.setSortingEnabled(True)
        self.videoListTable.cellClicked.connect(self.show_video)

        # Places the window elements on the window:
        # Top-left cell of main grid box:
        subGridBox = QWidget()
        subGrid = QGridLayout()
        subGrid.addWidget(self.folderField, 0, 0)
        subGrid.addWidget(self.folderButton, 0, 1)
        subGrid.addWidget(self.folderTreeCheckbox, 1, 0)
        subGrid.addWidget(self.processButton, 2, 0, 1, 2, Qt.AlignCenter)
        subGrid.addWidget(self.duplicateButton, 3, 0, 1, 2, Qt.AlignCenter)
        subGrid.addWidget(self.progressBar, 4, 0, 1, 2)
        subGridBox.setLayout(subGrid)

        # Main grid box:
        self.mainGrid = QGridLayout()
        self.mainGrid.addWidget(subGridBox, 0, 0)
        self.mainGrid.addWidget(self.tableTabs, 1, 0)
        self.mainGrid.addWidget(self.imageField, 0, 1, 2, 1, Qt.AlignCenter)
        self.mainGrid.addWidget(self.videoField, 0, 1, 2, 1)

        self.mainGrid.setColumnMinimumWidth(0, 350)
        self.mainGrid.setRowMinimumHeight(1, 500)
        self.mainGrid.setColumnStretch(1, 1)

        self.setLayout(self.mainGrid)

        # Creates a QThread instance:
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
        self.duplicateButton.setEnabled(False)

        # Clears both tables upon restarting function:
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
            self.duplicateRefs.clear()
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
        self.duplicateButton.setEnabled(True)

    # Start the second thread and remove all unique files from the table
    def find_duplicates(self):
        if IMAGE_PATH_DICT == {}:
            self.statusBar.setStyleSheet("color: red")
            self.statusBar.showMessage("Please process your media files first")
            return None

        self.processButton.setEnabled(False)
        self.statusBar.setStyleSheet("color: black")
        self.statusBar.showMessage("Finding duplicates...")
        # TODO: new thread removing all unique media. Only duplicates remain

    # Show an image upon clicking its name in the table
    def show_image(self, row, column):
        imageItem = self.imageListTable.item(row, column)
        imageId = self.imageListTable.item(row, 0).text()

        # Prevents from KeyError when clicking the second column:
        if imageItem.text() == IMAGE_PATH_DICT[imageId][0]:
            imageItemPath = IMAGE_PATH_DICT[imageId][2]

            # Removes a video from screen if shown:
            self.videoPlayer.stop()
            self.videoField.hide()
            self.imageField.show()

            # Shows animated images:
            if imageItemPath.lower().endswith("gif"):
                gif = QMovie(imageItemPath)
                gifSize = QSize(*self.smooth_gif_resize(imageItemPath, 600, 600))
                gif.setScaledSize(gifSize)
                self.imageField.setMovie(gif)
                gif.start()

            # Shows static images:
            else:
                self.imageField.setPixmap(
                    QPixmap(imageItemPath).scaled(
                        600, 600, Qt.KeepAspectRatio, Qt.SmoothTransformation
                    )
                )

        if column == 3:
            self.duplicateWindow = DuplicateWindow(self.imageListTable.item(row, 0))
            if imageId not in self.duplicateRefs.keys():
                self.duplicateRefs[imageId] = self.duplicateWindow
                self.duplicateWindow.show()
            self.duplicateWindow.deletionTrigger.connect(self.delete_image_row)
            self.duplicateWindow.closeTrigger.connect(self.delete_reference)

    # Show a video upon clicking its name in the table
    def show_video(self, row, column):
        videoItem = self.videoListTable.item(row, column)
        videoId = self.videoListTable.item(row, 0).text()
        self.mainGrid.setColumnMinimumWidth(1, 800)

        # Prevents from KeyError when clicking the second column:
        if videoItem.text() == VIDEO_PATH_DICT[videoId][0]:
            videoItemPath = VIDEO_PATH_DICT[videoId][2]
            videoContent = QMediaContent(QUrl.fromLocalFile(videoItemPath))
            self.videoPlayer.setMedia(videoContent)
            self.videoPlayer.setVideoOutput(self.videoField)

            # Removes an image from screen if shown and starts video:
            self.imageField.clear()
            self.imageField.hide()
            self.videoField.show()
            self.videoPlayer.play()

    # Remove a row of a duplicate image after it was deleted in DuplicateWindow
    def delete_image_row(self, itemId):
        self.imageField.setText("")                 # Rewrite imageField to prevent PermissionError if file was opened
        rows = self.imageListTable.rowCount()
        for row in range(rows):
            if self.imageListTable.item(row, 0).text() == itemId:
                self.imageListTable.removeRow(row)
                break                               # Stop loop after row deletion to prevent AttributeError

    # Remove a previously added reference from a dict if a DuplicateWindow was closed
    # so it can be opened again
    def delete_reference(self, itemId):
        self.duplicateRefs.pop(itemId)

    # An amazing workaround for gif resizing procedure
    # because PyQt's native one doesn't work for some reason:
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

    # Updates the json settings with the new folder depth value:
    def ok_event(self):
        json_settings.json_update("folderDepth", self.folderDepthField.text())
        self.close()


# A separate window to show duplicates of the source image:
class DuplicateWindow(QWidget):
    deletionTrigger = pyqtSignal(str)
    closeTrigger = pyqtSignal(str)

    def __init__(self, sourceImageId):
        super().__init__()
        self.sourceImageId = sourceImageId.text()
        self.sourceImage = IMAGE_PATH_DICT[self.sourceImageId][2]

        self.setWindowTitle("Duplicates")
        self.setFixedSize(500, 500)

        self.imageField = QLabel()
        # init duplicates list table
        self.duplicateTable = QTableWidget()
        # set duplicates list table fields unchanged
        self.duplicateTable.setEditTriggers(QTableWidget.NoEditTriggers)

        self.imageField.setPixmap(
            QPixmap(self.sourceImage).scaled(
                300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
        )

        self.duplicateTable.setColumnCount(4)
        self.duplicateTable.setHorizontalHeaderLabels(["ID", "File name", "", ""])
        self.duplicateTable.verticalHeader().setVisible(False)
        self.duplicateTable.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.duplicateTable.setSortingEnabled(True)

        self.duplicateTable.setColumnWidth(0, 25)
        self.duplicateTable.setColumnWidth(1, 345)
        self.duplicateTable.setColumnWidth(2, 25)
        self.duplicateTable.setColumnWidth(3, 25)

        self.duplicateTable.setRowCount(1)
        self.duplicateTable.setItem(0, 0, QTableWidgetItem(self.sourceImageId))
        self.duplicateTable.setItem(0, 1, QTableWidgetItem(IMAGE_PATH_DICT[self.sourceImageId][0]))

        openFolderIcon = QTableWidgetItem()
        openFolderIcon.setIcon(self.style().standardIcon(QStyle.SP_DirIcon))
        deleteItemIcon = QTableWidgetItem()
        deleteItemIcon.setIcon(self.style().standardIcon(QStyle.SP_MessageBoxCritical))

        self.duplicateTable.setItem(0, 2, openFolderIcon)
        self.duplicateTable.setItem(0, 3, deleteItemIcon)

        self.duplicateTable.cellClicked.connect(self.click_event)

        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.imageField, Qt.AlignCenter)
        self.vbox.addWidget(self.duplicateTable)
        self.setLayout(self.vbox)

    def click_event(self, row, column):
        item = self.duplicateTable.item(row, column)
        if item.text() == IMAGE_PATH_DICT[self.sourceImageId][0]:
            self.imageField.setPixmap(
                QPixmap(IMAGE_PATH_DICT[self.sourceImageId][2]).scaled(
                    300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
            )

        if column == 2:
            itemId = self.duplicateTable.item(row, 0).text()
            os.startfile(IMAGE_PATH_DICT[itemId][2].rsplit(os.sep, 1)[0])

        if column == 3:
            itemId = self.duplicateTable.item(row, 0).text()
            self.delete_duplicate(itemId, row)

    def delete_duplicate(self, itemId, row):
        message = QMessageBox().question(
            self,
            "Confirm deletion",
            "Delete duplicate media file?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if message == QMessageBox.Yes:
            self.duplicateTable.removeRow(row)
            self.deletionTrigger.emit(itemId)
            os.remove(IMAGE_PATH_DICT[self.sourceImageId][2])

        elif message == QMessageBox.No:
            pass

    def closeEvent(self, event):
        self.closeTrigger.emit(self.sourceImageId)
        self.close()
