# TODO:
# Thread processing duplicates
# Menu settings

import os
import traceback

from PIL import Image as Pil_Image
from pony.orm import db_session
from pony.orm import flush as db_flush

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *

from indexing import index_folder_files, reindex_image_files, reindex_video_files
from image_processing import image_processing, feature_description
from database import Image, save_new_files

from gui import json_settings

# Dict containment -> ID:[FILE_NAME, EXTENSION, FILE_FULL_PATH]
IMAGE_PATH_DICT = {}
VIDEO_PATH_DICT = {}


class ProcessingThread(QThread):
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
        # start indexing folder
        images, videos = index_folder_files(
            path=self.folderField.text(),
            max_depth=json_settings.user_json_read("folderDepth")
            if self.folderTreeCheckbox.isChecked()
            else 0,
        )

        # processing new files
        processed_files = image_processing(images)

        # save new files
        with db_session():
            save_new_files(indexed_files=processed_files, file_type="image")
            db_flush()
            # get available images from DB
            images = Image.all()

        for idx, image in enumerate(images):
            str_image_idx = str(idx)

            IMAGE_PATH_DICT[str_image_idx] = {
                "id": image.id,
                "name": image.image_name,
                "type": (image.image_name.split(".")[-1]).lower(),
                "full_path": image.full_path(),
            }
            self.imageListTable.setRowCount(idx)
            self.imageListTable.setItem(idx - 1, 0, QTableWidgetItem(str_image_idx))
            self.imageListTable.setItem(idx - 1, 1, QTableWidgetItem(image.image_name))
            self.imageListTable.setItem(
                idx - 1, 2, QTableWidgetItem(IMAGE_PATH_DICT[str_image_idx]["type"])
            )

            duplicateIcon = QTableWidgetItem()
            duplicateIcon.setIcon(
                QWidget().style().standardIcon(QStyle.SP_FileDialogContentsView)
            )
            self.imageListTable.setItem(idx - 1, 3, duplicateIcon)

        # TODO add video to DB and processing logic
        """
        for video in videos:
            rowVideos += 1
            videoId = str(rowVideos)
            VIDEO_PATH_DICT[videoId] = [
                video[0],
                (video[0].split(".")[-1]).lower(),
                os.path.join(video[1], video[0]),
            ]
            self.videoListTable.setRowCount(rowVideos)
            self.videoListTable.setItem(rowVideos - 1, 0, QTableWidgetItem(videoId))
            self.videoListTable.setItem(rowVideos - 1, 1, QTableWidgetItem(video[0]))
            self.videoListTable.setItem(
                rowVideos - 1, 2, QTableWidgetItem(VIDEO_PATH_DICT[videoId][1])
            )

            duplicateIcon = QTableWidgetItem()
            duplicateIcon.setIcon(
                QWidget().style().standardIcon(QStyle.SP_FileDialogContentsView)
            )
            self.videoListTable.setItem(rowVideos, 3, duplicateIcon)

        """

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
        settingsMenu.addAction("Database settings", self.show_database_settings)
        settingsMenu.addAction("Indexing settings", self.show_indexing_settings)
        settingsMenu.addAction("Matching settings", self.show_matching_settings)
        settingsMenu.addSeparator()
        settingsMenu.addAction("Other")

        self.window = Window(self.statusBar)
        self.setCentralWidget(self.window)

    def show_indexing_settings(self):
        self.indexingSettings = IndexingSettings()
        self.indexingSettings.show()

    def show_database_settings(self):
        self.database_settings = DatabaseSettings()
        self.database_settings.show()

    def show_matching_settings(self):
        self.database_settings = DatabaseSettings()
        self.database_settings.show()


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
        self.reindexButton = QPushButton("Reindex database files")
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
        self.folderField.setDisabled(True)

        self.folderButton.setIcon(self.style().standardIcon(QStyle.SP_DialogOpenButton))
        self.folderButton.clicked.connect(self.set_folder)

        self.processButton.clicked.connect(self.process_files)
        self.processButton.setFixedWidth(160)
        self.processButton.setDisabled(True)

        self.duplicateButton.clicked.connect(self.find_duplicates)
        self.duplicateButton.setFixedWidth(160)

        self.reindexButton.clicked.connect(self.reindex_db_data)
        self.reindexButton.setFixedWidth(160)

        self.imagesTab = self.tableTabs.insertTab(0, self.imageListTable, "Images")
        self.videosTab = self.tableTabs.insertTab(1, self.videoListTable, "Videos")

        self.imageListTable.setColumnCount(4)
        self.imageListTable.setHorizontalHeaderLabels(
            ["ID", "File name", "Format", "Actions"]
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
            ["ID", "File name", "Format", "Actions"]
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
        subGrid.addWidget(self.reindexButton, 4, 0, 1, 2, Qt.AlignCenter)
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

        self.thread.finishedTrigger.connect(self.finish_thread)

        # filling table while first run
        self.reindex_db_data()

    def reindex_db_data(self):
        # Reindex already exist folders and files; Image and Video files
        reindex_image_files()
        reindex_video_files()
        # run table filling after reindexing
        self.table_data_init()

    def table_data_init(self):
        # get available images from DB
        with db_session():
            images = Image.all()

        for idx, image in enumerate(images):
            str_image_idx = str(idx)

            IMAGE_PATH_DICT[str_image_idx] = {
                "id": image.id,
                "name": image.image_name,
                "type": (image.image_name.split(".")[-1]).lower(),
                "full_path": image.full_path(),
            }
            self.imageListTable.setRowCount(idx)
            self.imageListTable.setItem(idx - 1, 0, QTableWidgetItem(str_image_idx))
            self.imageListTable.setItem(idx - 1, 1, QTableWidgetItem(image.image_name))
            self.imageListTable.setItem(
                idx - 1, 2, QTableWidgetItem(IMAGE_PATH_DICT[str_image_idx]["type"])
            )

            duplicateIcon = QTableWidgetItem()
            duplicateIcon.setIcon(
                QWidget().style().standardIcon(QStyle.SP_FileDialogContentsView)
            )
            self.imageListTable.setItem(idx - 1, 3, duplicateIcon)

    # Get a folder full of multimedia files to work with
    def set_folder(self):
        self.folderPath = QFileDialog.getExistingDirectory(self)
        if self.folderPath == "":
            self.folderPath = self.folderField.text()
        self.folderField.setText(self.folderPath)
        self.processButton.setEnabled(True)
        self.statusBar.clearMessage()

    # Start the thread and fill the table with those files
    def process_files(self):
        self.duplicateButton.setDisabled(True)
        self.reindexButton.setDisabled(True)

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
            self.processButton.setText("Process media files")

    # Thread done and ded
    def finish_thread(self):
        self.statusBar.setStyleSheet("color: black")
        self.statusBar.showMessage("Finished!")
        self.processButton.setText("Start")
        self.duplicateButton.setEnabled(True)
        self.reindexButton.setEnabled(True)

    # Start the second thread and remove all unique files from the table
    def find_duplicates(self):
        if IMAGE_PATH_DICT == {}:
            self.statusBar.setStyleSheet("color: red")
            self.statusBar.showMessage("Please process your media files first")
            return None

        self.processButton.setEnabled(False)
        self.statusBar.setStyleSheet("color: black")
        self.statusBar.showMessage("Finding duplicates...")

        QMessageBox.information(
            self,
            "Find duplicates",
            "Similar images search start. Please wait!",
            QMessageBox.Ok,
            QMessageBox.Ok,
        )

        # get all images descriptors
        image_files_query = Image.get_images_descriptors()
        # run function to find duplicates
        feature_description(images_list=image_files_query)

        QMessageBox.information(
            self, "Find duplicates", "Success!", QMessageBox.Ok, QMessageBox.Ok
        )

        # TODO: new thread removing all unique media. Only duplicates remain

    # Show an image upon clicking its name in the table
    def show_image(self, row, column):
        imageItem = self.imageListTable.item(row, column)
        imageId = self.imageListTable.item(row, 0).text()

        # Prevents from KeyError when clicking the second column:
        if imageItem.text() == IMAGE_PATH_DICT[imageId]["name"]:
            imageItemPath = IMAGE_PATH_DICT[imageId]["full_path"]

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
            self.duplicateWindow = DuplicateWindow(image_data=IMAGE_PATH_DICT[imageId], raw_id = imageId)
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
        self.imageField.setText(
            ""
        )  # Rewrite imageField to prevent PermissionError if file was opened
        rows = self.imageListTable.rowCount()
        for row in range(rows):
            if self.imageListTable.item(row, 0).text() == itemId:
                self.imageListTable.removeRow(row)
                break  # Stop loop after row deletion to prevent AttributeError

    # Remove a previously added reference from a dict if a DuplicateWindow was closed
    # so it can be opened again
    def delete_reference(self, itemId):
        self.duplicateRefs.pop(itemId)

    # An amazing workaround for gif resizing procedure
    # because PyQt's native one doesn't work for some reason:
    def smooth_gif_resize(self, gif, frameWidth, frameHeight):
        gif = Pil_Image.open(gif)
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

        self.folderDepthField.setText(str(json_settings.user_json_read("folderDepth")))
        self.okButton.clicked.connect(self.ok_event)

        self.grid = QGridLayout()
        self.grid.addWidget(self.folderDepthLabel, 0, 0)
        self.grid.addWidget(self.folderDepthField, 0, 1)
        self.grid.addWidget(self.okButton, 1, 1)
        self.setLayout(self.grid)

    # Updates the json settings with the new folder depth value:
    def ok_event(self):
        json_settings.user_json_update("folderDepth", self.folderDepthField.text())
        self.close()


# Allows to set a custom folder depth value in the json file:
class DatabaseSettings(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Database settings")
        self.setFixedSize(350, 350)

        self.databaseProviderLabel = QLabel("Database provider:")
        self.databaseProviderField = QLineEdit()
        self.databaseFilenameLabel = QLabel("File name:")
        self.databaseFilenameField = QLineEdit()
        self.databaseUserLabel = QLabel("User:")
        self.databaseUserField = QLineEdit()
        self.databasePasswordLabel = QLabel("Password:")
        self.databasePasswordField = QLineEdit()
        self.databaseHostLabel = QLabel("Host:")
        self.databaseHostField = QLineEdit()
        self.databasePortLabel = QLabel("Port:")
        self.databasePortField = QLineEdit()
        self.databaseNameLabel = QLabel("Database name:")
        self.databaseNameField = QLineEdit()

        # dropdown menu with available DB providers
        self.providersBox = QComboBox(self)
        self.providersBox.addItems(["SQLite", "Postgres", "MySQL"])
        self.providersBox.currentIndexChanged.connect(self.selection_change)

        # buttons
        self.testConnectionButton = QPushButton("Test connection")
        self.testConnectionButton.clicked.connect(self.test_connection_event)
        self.okButton = QPushButton("Ok")
        self.okButton.clicked.connect(self.ok_event)

        # fields filling
        self.databaseProviderField.setText(str(json_settings.db_json_read("provider")))
        self.databaseFilenameField.setText(str(json_settings.db_json_read("filename")))
        self.databaseUserField.setDisabled(True)
        self.databasePasswordField.setDisabled(True)
        self.databaseHostField.setDisabled(True)
        self.databasePortField.setDisabled(True)
        self.databaseNameField.setDisabled(True)

        self.grid = QGridLayout()
        # labels & fields
        self.grid.addWidget(self.databaseProviderLabel, 0, 0)
        self.grid.addWidget(self.providersBox, 0, 1)
        self.grid.addWidget(self.databaseFilenameLabel, 1, 0)
        self.grid.addWidget(self.databaseFilenameField, 1, 1)
        self.grid.addWidget(self.databaseUserLabel, 2, 0)
        self.grid.addWidget(self.databaseUserField, 2, 1)
        self.grid.addWidget(self.databasePasswordLabel, 3, 0)
        self.grid.addWidget(self.databasePasswordField, 3, 1)
        self.grid.addWidget(self.databaseHostLabel, 4, 0)
        self.grid.addWidget(self.databaseHostField, 4, 1)
        self.grid.addWidget(self.databasePortLabel, 5, 0)
        self.grid.addWidget(self.databasePortField, 5, 1)
        self.grid.addWidget(self.databaseNameLabel, 6, 0)
        self.grid.addWidget(self.databaseNameField, 6, 1)
        # buttons
        self.grid.addWidget(self.testConnectionButton, 7, 0)
        self.grid.addWidget(self.okButton, 7, 1)

        self.setLayout(self.grid)

    # Updates the json settings with the new folder depth value:
    def ok_event(self):
        json_settings.db_json_update(
            "provider", self.providersBox.currentText().lower()
        )
        if self.providersBox.currentText() == "SQLite":
            json_settings.db_json_update("filename", self.databaseFilenameField.text())
        else:
            json_settings.db_json_update("user", self.databaseUserField.text())
            json_settings.db_json_update("password", self.databasePasswordField.text())
            json_settings.db_json_update("host", self.databaseHostField.text())
            json_settings.db_json_update("port", self.databasePortField.text())
            json_settings.db_json_update("database", self.databaseNameField.text())
        self.close()

    # Test connection to DB
    def test_connection_event(self):
        try:
            if self.providersBox.currentText() == "SQLite":
                import sqlite3

                conn = sqlite3.connect(self.databaseFilenameField.text())
                conn.close()
                os.remove(self.databaseFilenameField.text())

            elif self.providersBox.currentText() == "Postgres":
                import psycopg2

                conn = psycopg2.connect(
                    dbname=self.databaseNameField.text(),
                    user=self.databaseUserField.text(),
                    password=self.databasePasswordField.text(),
                    host=self.databaseHostField.text(),
                    port=self.databasePortField.text(),
                )
                conn.close()

            elif self.providersBox.currentText() == "MySQL":
                import mysql.connector

                conn = mysql.connector.connect(
                    data=self.databaseNameField.text(),
                    user=self.databaseUserField.text(),
                    passwd=self.databasePasswordField.text(),
                    host=self.databaseHostField.text(),
                    port=self.databasePortField.text(),
                )
                conn.close()

            QMessageBox.information(
                self,
                "Connection test",
                "Success database connection.\nTo connect to the new database - restart the application.",
                QMessageBox.Ok,
                QMessageBox.Ok,
            )
        except Exception:
            QMessageBox.warning(
                self,
                "Connection test",
                f"Error while connection test.\nCheck your fields.\nError:\n{traceback.format_exc()}",
                QMessageBox.Ok,
                QMessageBox.Ok,
            )

    def selection_change(self):
        """
        Method make able or disable database settings fields when user change DB provider dropdown menu
        """
        # if user check SQLite - make other fields disabled
        if self.providersBox.currentText() != "SQLite":
            # make filename disabled
            self.databaseFilenameField.setDisabled(True)
            # make other fields able
            self.databaseUserField.setDisabled(False)
            self.databasePasswordField.setDisabled(False)
            self.databaseHostField.setDisabled(False)
            self.databasePortField.setDisabled(False)
            self.databaseNameField.setDisabled(False)
            # fill data from config
            self.databaseUserField.setText(str(json_settings.db_json_read("user")))
            self.databasePasswordField.setText(
                str(json_settings.db_json_read("password"))
            )
            self.databaseHostField.setText(str(json_settings.db_json_read("host")))
            self.databasePortField.setText(str(json_settings.db_json_read("port")))
            self.databaseNameField.setText(str(json_settings.db_json_read("database")))
        # if select SQLite
        else:
            # make filename able
            self.databaseFilenameField.setDisabled(False)
            # if user check SQLite - make all fields disabled
            self.databaseUserField.setDisabled(True)
            self.databasePasswordField.setDisabled(True)
            self.databaseHostField.setDisabled(True)
            self.databasePortField.setDisabled(True)
            self.databaseNameField.setDisabled(True)


# A separate window to show duplicates of the source image:
class DuplicateWindow(QWidget):
    deletionTrigger = pyqtSignal(str)
    closeTrigger = pyqtSignal(str)

    def __init__(self, image_data: dict, raw_id: str):
        super().__init__()
        self.sourceImage = image_data
        self.sourceImageRawId = raw_id

        self.setWindowTitle("Duplicates")
        self.setFixedSize(500, 500)

        self.imageField = QLabel()
        # init duplicates list table
        self.duplicateTable = QTableWidget()
        # set duplicates list table fields unchanged
        self.duplicateTable.setEditTriggers(QTableWidget.NoEditTriggers)

        self.imageField.setPixmap(
            QPixmap(self.sourceImage['full_path']).scaled(
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
        self.duplicateTable.setItem(0, 0, QTableWidgetItem(self.sourceImageRawId))
        self.duplicateTable.setItem(
            0, 1, QTableWidgetItem(self.sourceImage["name"])
        )

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

        # run duplicates find at first run
        self.table_data_init()

    def table_data_init(self):
        with db_session():
            result = get_image_duplicates(image_id=self.sourceImage['id'], similarity_threshold=150)

    def click_event(self, row, column):
        item = self.duplicateTable.item(row, column)
        if item.text() == self.sourceImage["name"]:
            self.imageField.setPixmap(
                QPixmap(self.sourceImage["full_path"]).scaled(
                    300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
            )
        elif column == 3:
            itemId = self.duplicateTable.item(row, 0).text()
            self.delete_duplicate(itemId, row, self.sourceImage["id"])
        '''
        if column == 2:
            itemId = self.duplicateTable.item(row, 0).text()
            os.startfile(self.sourceImage["full_path"].rsplit(os.sep, 1)[0])
        '''
    def delete_duplicate(self, itemId: str, row: str, image_id: int):
        message = QMessageBox().question(
            self,
            "Confirm deletion",
            "Delete duplicate media file?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if message == QMessageBox.Yes:
            self.duplicateTable.removeRow(row)
            self.deletionTrigger.emit(itemId)
            # run custom delete
            with db_session():
                Image[image_id].custom_delete()

            QMessageBox().information(
                self,
                "File deletion",
                "File success deleted",
                QMessageBox.Ok,
                QMessageBox.Ok,
            )
        elif message == QMessageBox.No:
            pass

    def closeEvent(self, event):
        self.closeTrigger.emit(self.sourceImageRawId)
        self.close()
