import os
import traceback
from collections import OrderedDict


from PIL import Image as Pil_Image
from pony.orm import db_session
from pony.orm import flush as db_flush

from PyQt5.QtWidgets import (
    QTableWidgetItem,
    QWidget,
    QMainWindow,
    QStatusBar,
    QMenuBar,
    QLineEdit,
    QPushButton,
    QCheckBox,
    QTabWidget,
    QTableWidget,
    QLabel,
    QGridLayout,
    QMessageBox,
    QComboBox,
    QFileDialog,
    QSpinBox,
)
from PyQt5.QtGui import QIcon, QPixmap, QMovie
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QUrl, QSize
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget

from indexing import index_folder_files, reindex_image_files, reindex_video_files
from image_processing import image_processing, feature_description
from database import Image, save_new_files, get_image_duplicates, save_images_duplicates

from gui import json_settings
from gui.scripts import copy_image, open_path

# Dict containment -> ID:[FILE_NAME, EXTENSION, FILE_FULL_PATH]
IMAGE_PATH_DICT = OrderedDict()
VIDEO_PATH_DICT = OrderedDict()


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
                "additional_attrs": {"height": image.image_height, "width": image.image_width},
                "folder": image.image_path,
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
            duplicateIcon.setIcon(QIcon("gui/static/icon_view_duplicates.png"))
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
        self.setWindowIcon(QIcon("gui/static/icon_logo.png"))
        self.setWindowTitle("T e b y g")
        self.move(300, 50)

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
        self.matching_settings = MatchingSettings()
        self.matching_settings.show()


class Window(QWidget):
    COLUMNS_DICT = {
        # "Column label": {'index': column_ID, 'width': column_width}
        "ID": {"index": 0, "width": 25},
        "File name": {"index": 1, "width": 165},
        "Format": {"index": 2, "width": 50},
        "Dup": {"index": 3, "width": 5},
    }

    def __init__(self, statusBar):
        super().__init__()

        # store active image ID
        self.active_image_id = str()

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

        # set up image fields and elements
        self.imageField = QLabel()
        self.imageNameField = QLabel()
        self.imageParamsField = QLabel()

        self.imageCopyButton = QPushButton("Copy image")
        self.imageCopyButton.setIcon(QIcon("gui/static/icon_copy.png"))
        self.imageCopyButton.clicked.connect(self.copy_image_path)
        self.imageViewButton = QPushButton("View image")
        self.imageViewButton.setIcon(QIcon("gui/static/icon_open_image.svg"))
        self.imageViewButton.clicked.connect(self.open_image_file)
        self.imageOpenDirButton = QPushButton("Open dir")
        self.imageOpenDirButton.setIcon(QIcon("gui/static/icon_open_folder.svg"))
        self.imageOpenDirButton.clicked.connect(self.open_image_path)
        self.imageDeleteButton = QPushButton("Delete")
        self.imageDeleteButton.setIcon(QIcon("gui/static/icon_delete_file.png"))
        self.imageDeleteButton.clicked.connect(self.delete_image)

        self.videoField = QVideoWidget()
        self.videoPlayer = QMediaPlayer()

        # Adjusts settings for the window elements:
        self.folderField.setDisabled(True)

        self.folderButton.setIcon(QIcon("gui/static/icon_process_folder.png"))
        self.folderButton.clicked.connect(self.set_folder)

        self.processButton.clicked.connect(self.process_files)
        self.processButton.setFixedWidth(160)
        self.processButton.setDisabled(True)

        self.duplicateButton.clicked.connect(self.find_duplicates)
        self.duplicateButton.setFixedWidth(160)

        self.reindexButton.clicked.connect(self.reindex_db_data)
        self.reindexButton.setFixedWidth(160)

        # prepare tables for images and videos
        self.imagesTab = self.tableTabs.insertTab(0, self.imageListTable, "Images")
        self.videosTab = self.tableTabs.insertTab(1, self.videoListTable, "Videos")

        # images list table setup
        self.imageListTable.setColumnCount(len(self.COLUMNS_DICT.keys()))
        self.imageListTable.setHorizontalHeaderLabels(self.COLUMNS_DICT.keys())
        self.imageListTable.verticalHeader().setVisible(False)
        self.imageListTable.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.imageListTable.setSortingEnabled(True)
        self.imageListTable.cellClicked.connect(self.show_image)

        # videos list table setup
        self.videoListTable.setColumnCount(len(self.COLUMNS_DICT.keys()))
        self.videoListTable.setHorizontalHeaderLabels(self.COLUMNS_DICT.keys())
        self.videoListTable.verticalHeader().setVisible(False)
        self.videoListTable.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.videoListTable.setSortingEnabled(True)
        self.videoListTable.cellClicked.connect(self.show_video)

        # set images and videos duplicates columns width
        self.set_columns_width()

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

        # image data grid box
        imageGridBox = QWidget()
        imageGrid = QGridLayout()
        imageGrid.addWidget(self.imageField, 0, 0, 1, 4, Qt.AlignCenter)
        # add image buttons
        imageGrid.addWidget(self.imageCopyButton, 1, 0, 1, 1)
        imageGrid.addWidget(self.imageViewButton, 1, 1, 1, 1)
        imageGrid.addWidget(self.imageOpenDirButton, 1, 2, 1, 1)
        imageGrid.addWidget(self.imageDeleteButton, 1, 3, 1, 1)

        imageGrid.addWidget(self.imageNameField, 2, 0, 1, 1)
        imageGrid.addWidget(self.imageParamsField, 2, 3, 1, 1)
        imageGridBox.setLayout(imageGrid)

        # Main grid box:
        self.mainGrid = QGridLayout()
        self.mainGrid.addWidget(subGridBox, 0, 0)
        self.mainGrid.addWidget(self.tableTabs, 1, 0)
        self.mainGrid.addWidget(imageGridBox, 1, 1)
        self.mainGrid.addWidget(self.videoField, 0, 1, 2, 1)
        self.mainGrid.setColumnMinimumWidth(0, 400)
        self.mainGrid.setRowMinimumHeight(1, 600)
        self.mainGrid.setColumnStretch(1, 1)

        self.setLayout(self.mainGrid)

        # Creates a QThread instance:
        self.thread = ProcessingThread(
            self.folderField, self.imageListTable, self.videoListTable, self.folderTreeCheckbox
        )

        self.thread.finishedTrigger.connect(self.finish_thread)

        # filling table while first run
        self.reindex_db_data()
        # hide image interface
        self.hide_active_image()

    def set_columns_width(self):
        # looping all columns and set with
        for value in self.COLUMNS_DICT.values():
            self.imageListTable.setColumnWidth(value["index"], value["width"])
            self.videoListTable.setColumnWidth(value["index"], value["width"])

    def reindex_db_data(self):
        self.duplicateButton.setDisabled(True)
        self.processButton.setDisabled(True)
        self.reindexButton.setDisabled(True)
        # Reindex already exist folders and files; Image and Video files
        reindex_image_files()
        reindex_video_files()
        # run table filling after reindexing
        self.table_data_init()
        self.duplicateButton.setEnabled(True)
        self.processButton.setEnabled(True)
        self.reindexButton.setEnabled(True)

    def center_widget_item(self, text: str) -> QTableWidgetItem:
        # create the item
        center_align_item = QTableWidgetItem(text)
        # change the alignment
        center_align_item.setTextAlignment(Qt.AlignCenter)
        return center_align_item

    def table_data_init(self):
        # get available images from DB
        with db_session():
            images = Image.all()

        for idx, image in enumerate(images):
            numRows = self.imageListTable.rowCount()
            self.imageListTable.insertRow(numRows)

            str_image_idx = str(idx)

            IMAGE_PATH_DICT[str_image_idx] = {
                "id": image.id,
                "name": image.image_name,
                "additional_attrs": {"height": image.image_height, "width": image.image_width},
                "folder": image.image_path,
                "type": (image.image_name.split(".")[-1]).lower(),
                "full_path": image.full_path(),
            }

            self.imageListTable.setItem(
                idx, self.COLUMNS_DICT["ID"]["index"], self.center_widget_item(str_image_idx)
            )
            self.imageListTable.setItem(
                idx,
                self.COLUMNS_DICT["File name"]["index"],
                self.center_widget_item(image.image_name),
            )
            self.imageListTable.setItem(
                idx,
                self.COLUMNS_DICT["Format"]["index"],
                self.center_widget_item(IMAGE_PATH_DICT[str_image_idx]["type"]),
            )

            duplicateIcon = QTableWidgetItem()
            duplicateIcon.setIcon(QIcon("gui/static/icon_view_duplicates.png"))
            self.imageListTable.setItem(idx, self.COLUMNS_DICT["Dup"]["index"], duplicateIcon)

    def hide_active_image(self):
        self.imageField.hide()
        self.imageCopyButton.hide()
        self.imageViewButton.hide()
        self.imageOpenDirButton.hide()
        self.imageDeleteButton.hide()
        self.imageNameField.hide()
        self.imageParamsField.hide()

    def show_active_image(self):
        self.imageField.show()
        self.imageCopyButton.show()
        self.imageViewButton.show()
        self.imageOpenDirButton.show()
        self.imageDeleteButton.show()
        self.imageNameField.show()
        self.imageParamsField.show()

    def open_image_file(self):
        open_path(path=IMAGE_PATH_DICT[self.active_image_id]["full_path"])

    def open_image_path(self):
        open_path(path=IMAGE_PATH_DICT[self.active_image_id]["folder"])

    def delete_image(self):
        # count image table position
        image_table_position = list(IMAGE_PATH_DICT.keys()).index(self.active_image_id)

        message = QMessageBox().question(
            self,
            "Confirm deletion",
            "Delete duplicate media file?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if message == QMessageBox.Yes:
            self.imageListTable.removeRow(image_table_position)
            image_id = IMAGE_PATH_DICT[self.active_image_id]["id"]
            # run custom delete
            with db_session():
                Image[image_id].custom_delete()

            # delete image key from dict
            del IMAGE_PATH_DICT[self.active_image_id]

            self.hide_active_image()
            QMessageBox().information(
                self, "File deletion", "File success deleted", QMessageBox.Ok, QMessageBox.Ok
            )
        elif message == QMessageBox.No:
            pass

    def copy_image_path(self):
        try:
            result = copy_image(IMAGE_PATH_DICT[self.active_image_id]["full_path"])
            if result:
                QMessageBox.information(
                    self,
                    "Copy path",
                    "Success!\nFile copied to clipboard!",
                    QMessageBox.Ok,
                    QMessageBox.Ok,
                )
            else:
                QMessageBox.warning(
                    self,
                    "Copy path",
                    "Error!\nSorry, i can`t copy image to clipboard.",
                    QMessageBox.Ok,
                    QMessageBox.Ok,
                )

        except Exception:
            print(traceback.format_exc())
            QMessageBox.warning(
                self,
                "Copy path",
                f"Error!\n{traceback.format_exc()}",
                QMessageBox.Ok,
                QMessageBox.Ok,
            )

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
        # set other buttons disabled
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
            self.duplicateButton.setEnabled(True)
            self.reindexButton.setEnabled(True)
            return None

        if not self.thread.isRunning():
            self.duplicateRefs.clear()
            self.thread.start()
            self.processButton.setText("Stop")

        elif self.thread.isRunning():
            self.thread.terminate()
            self.processButton.setText("Process media files")
            self.duplicateButton.setEnabled(True)
            self.reindexButton.setEnabled(True)

    # Thread done and ded
    def finish_thread(self):
        self.statusBar.setStyleSheet("color: black")
        self.statusBar.showMessage("Finished!")
        self.processButton.setText("Process media files")
        # set all buttons able
        self.duplicateButton.setEnabled(True)
        self.reindexButton.setEnabled(True)

    # Start the second thread and remove all unique files from the table
    def find_duplicates(self):
        if IMAGE_PATH_DICT == {}:
            self.statusBar.setStyleSheet("color: red")
            self.statusBar.showMessage("Please process your media files first")
            return None

        self.duplicateButton.setDisabled(True)
        self.processButton.setDisabled(True)
        self.reindexButton.setDisabled(True)
        self.statusBar.setStyleSheet("color: black")
        self.statusBar.showMessage("Finding duplicates...")

        with db_session():
            # get all images descriptors
            image_files_query = Image.get_descriptors()

        pairs_amount = int(len(image_files_query) * (len(image_files_query) - 1) / 2)

        QMessageBox.information(
            self,
            "Find duplicates",
            f"""
            Similar images search start. Please wait!\n
            You have ~{pairs_amount} images pairs;
            Work will get ~{round(pairs_amount*0.00006, 2)} sec.
            """,
            QMessageBox.Ok,
            QMessageBox.Ok,
        )

        # run function to find duplicates
        result = feature_description(images_list=image_files_query)
        with db_session():
            # save duplicates to DB
            save_images_duplicates(result)

        QMessageBox.information(
            self, "Find duplicates", "Success!", QMessageBox.Ok, QMessageBox.Ok
        )
        # set all buttons able
        self.duplicateButton.setEnabled(True)
        self.reindexButton.setEnabled(True)
        self.processButton.setEnabled(True)

        # TODO: new thread removing all unique media. Only duplicates remain

    # Show an image upon clicking its name in the table
    def show_image(self, row, column):
        imageId = self.imageListTable.item(row, 0).text()

        # set new active image id
        self.active_image_id = imageId

        # Removes a video from screen if shown:
        self.videoPlayer.stop()
        self.videoField.hide()
        # show active image
        self.show_active_image()

        # show image and additional data
        self.imageNameField.setText(f"{IMAGE_PATH_DICT[imageId]['name']}")
        self.imageParamsField.setText(
            f"HxW: {IMAGE_PATH_DICT[imageId]['additional_attrs']['height']}px"
            + f" x {IMAGE_PATH_DICT[imageId]['additional_attrs']['width']}px"
        )

        # Shows animated images
        if IMAGE_PATH_DICT[imageId]["name"].lower().endswith("gif"):
            gif = QMovie(IMAGE_PATH_DICT[imageId]["full_path"])
            gifSize = QSize(
                *self.smooth_gif_resize(IMAGE_PATH_DICT[imageId]["full_path"], 600, 600)
            )
            gif.setScaledSize(gifSize)
            self.imageField.setMovie(gif)
            gif.start()

        # Shows static images
        else:
            self.imageField.setPixmap(
                QPixmap(IMAGE_PATH_DICT[imageId]["full_path"]).scaled(
                    600, 600, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
            )

        if column == self.COLUMNS_DICT["Dup"]["index"]:
            self.duplicateWindow = DuplicateWindow(
                image_data=IMAGE_PATH_DICT[imageId], raw_id=imageId
            )
            if imageId not in self.duplicateRefs.keys():
                self.duplicateRefs[imageId] = self.duplicateWindow
                self.duplicateWindow.show()
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
        self.folderDepthField = QSpinBox()
        self.okButton = QPushButton("Ok")

        # set depth min and max value
        self.folderDepthField.setRange(1, 10)
        self.folderDepthField.setSingleStep(1)

        self.folderDepthField.setValue(json_settings.user_json_read("folderDepth"))
        self.okButton.clicked.connect(self.ok_event)

        self.grid = QGridLayout()
        self.grid.addWidget(self.folderDepthLabel, 0, 0)
        self.grid.addWidget(self.folderDepthField, 0, 1)
        self.grid.addWidget(self.okButton, 1, 1)
        self.setLayout(self.grid)

    # Updates the json settings with the new folder depth value:
    def ok_event(self):
        json_settings.user_json_update("folderDepth", self.folderDepthField.value())
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
        json_settings.db_json_update("provider", self.providersBox.currentText().lower())
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
            self.databasePasswordField.setText(str(json_settings.db_json_read("password")))
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


# Allows to set matching settings in the json file:
class MatchingSettings(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Matching settings")
        self.setFixedSize(350, 100)

        self.matchingIndexLabel = QLabel("Matching threshold, %:")
        self.matchingIndexSpinBox = QSpinBox()
        self.matchingTypeLabel = QLabel("Matching type:")
        self.matchingTypeComboBox = QComboBox()
        self.okButton = QPushButton("Ok")

        self.matchingIndexSpinBox.setRange(30, 90)
        self.matchingIndexSpinBox.setSingleStep(5)

        self.matchingIndexSpinBox.setValue(
            json_settings.processing_json_read("similarity_threshold") * 100
        )
        self.matchingTypeComboBox.addItems(["Histogram"])
        self.okButton.clicked.connect(self.ok_event)

        self.grid = QGridLayout()
        self.grid.addWidget(self.matchingIndexLabel, 0, 0)
        self.grid.addWidget(self.matchingIndexSpinBox, 0, 1)
        self.grid.addWidget(self.matchingTypeLabel, 1, 0)
        self.grid.addWidget(self.matchingTypeComboBox, 1, 1)
        self.grid.addWidget(self.okButton, 2, 1)
        self.setLayout(self.grid)

    # Updates the json settings with the new values:
    def ok_event(self):
        json_settings.processing_json_update(
            "similarity_threshold", self.matchingIndexSpinBox.value() / 100
        )
        self.close()


# A separate window to show duplicates of the source image:
class DuplicateWindow(QWidget):
    closeTrigger = pyqtSignal(str)

    COLUMNS_DICT = {
        # "Column label": {'index': column_ID, 'width': column_width}
        "ID": {"index": 0, "width": 50},
        "File name": {"index": 1, "width": 350},
        "Similarity": {"index": 2, "width": 70},
        "Directory": {"index": 3, "width": 75},
        "View": {"index": 4, "width": 50},
        "Copy": {"index": 5, "width": 50},
        "Delete": {"index": 6, "width": 50},
    }

    def __init__(self, image_data: dict, raw_id: str):
        super().__init__()
        # image model from DB
        self.sourceImage = image_data
        # image row ID from main window table
        self.sourceImageRawId = raw_id
        # local images storage
        self.local_IMAGE_PATH_DICT = {}

        self.setWindowTitle("Duplicates")
        self.setFixedSize(700, 500)

        self.mainImageField = QLabel()
        self.mainImageNameField = QLabel()
        self.mainImageParamsField = QLabel()

        self.duplicateImageField = QLabel()
        self.duplicateImageNameField = QLabel()
        self.duplicateImageParamsField = QLabel()
        # set images grid(left - main image, right - duplicate)
        self.imagesGrid = QGridLayout()
        self.imagesGrid.addWidget(self.mainImageField, 0, 0)
        self.imagesGrid.addWidget(self.mainImageNameField, 1, 0)
        self.imagesGrid.addWidget(self.mainImageParamsField, 2, 0)

        self.imagesGrid.addWidget(self.duplicateImageField, 0, 1)
        self.imagesGrid.addWidget(self.duplicateImageNameField, 1, 1)
        self.imagesGrid.addWidget(self.duplicateImageParamsField, 2, 1)

        self.subGridBox = QWidget()
        self.subGridBox.setLayout(self.imagesGrid)

        # init duplicates list table
        self.duplicateTable = QTableWidget()
        # set duplicates list table fields unchanged
        self.duplicateTable.setEditTriggers(QTableWidget.NoEditTriggers)
        self.duplicateTable.setColumnCount(len(self.COLUMNS_DICT.keys()))
        self.duplicateTable.setHorizontalHeaderLabels(self.COLUMNS_DICT.keys())
        self.duplicateTable.verticalHeader().setVisible(False)
        self.duplicateTable.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.duplicateTable.setSortingEnabled(True)
        # set columns width
        self.set_columns_width()
        self.duplicateTable.cellClicked.connect(self.table_click_event)

        # set grid system
        self.mainGrid = QGridLayout()
        self.mainGrid.addWidget(self.subGridBox, 0, 0)
        self.mainGrid.addWidget(self.duplicateTable, 1, 0)
        self.setLayout(self.mainGrid)

        # set main image
        self.main_image_init()
        # run duplicates find at first run
        self.table_data_init()

    def set_columns_width(self):
        # looping all columns and set with
        for value in self.COLUMNS_DICT.values():
            self.duplicateTable.setColumnWidth(value["index"], value["width"])

    def open_image_icon(self) -> QTableWidgetItem:
        # create open-image icon
        openImageIcon = QTableWidgetItem()
        openImageIcon.setIcon(QIcon("gui/static/icon_open_image.svg"))
        return openImageIcon

    def open_folder_icon(self) -> QTableWidgetItem:
        # create open-fodler icon
        openFolderIcon = QTableWidgetItem()
        openFolderIcon.setIcon(QIcon("gui/static/icon_open_folder.svg"))
        return openFolderIcon

    def copy_path_icon(self) -> QTableWidgetItem:
        # create open-image icon
        openImageIcon = QTableWidgetItem()
        openImageIcon.setIcon(QIcon("gui/static/icon_copy.png"))
        return openImageIcon

    def delete_image_icon(self) -> QTableWidgetItem:
        # create delete-icon in table
        deleteItemIcon = QTableWidgetItem()
        deleteItemIcon.setIcon(QIcon("gui/static/icon_delete_file.png"))
        return deleteItemIcon

    def main_image_init(self):
        # write main image name
        self.mainImageNameField.setText(self.sourceImage["name"])
        # write main image params
        self.mainImageParamsField.setText(
            f"{self.sourceImage['additional_attrs']['height']}px"
            + f" x {self.sourceImage['additional_attrs']['width']}px"
        )

        self.mainImageField.setPixmap(
            QPixmap(self.sourceImage["full_path"]).scaled(
                300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
        )
        self.local_IMAGE_PATH_DICT["1"] = {
            "id": self.sourceImage["id"],
            "name": self.sourceImage["name"],
            "additional_attrs": {
                "height": self.sourceImage["additional_attrs"]["height"],
                "width": self.sourceImage["additional_attrs"]["width"],
            },
            "folder": self.sourceImage["folder"],
            "full_path": self.sourceImage["full_path"],
        }
        self.duplicateTable.setRowCount(1)

        str_image_idx = str(1)

        self.duplicateTable.setItem(
            0, self.COLUMNS_DICT["ID"]["index"], QTableWidgetItem(str_image_idx)
        )
        self.duplicateTable.setItem(
            0, self.COLUMNS_DICT["File name"]["index"], QTableWidgetItem(self.sourceImage["name"])
        )
        self.duplicateTable.setItem(
            0, self.COLUMNS_DICT["Similarity"]["index"], QTableWidgetItem("src")
        )
        self.duplicateTable.setItem(
            0, self.COLUMNS_DICT["Directory"]["index"], self.open_folder_icon()
        )
        self.duplicateTable.setItem(0, self.COLUMNS_DICT["View"]["index"], self.open_image_icon())
        self.duplicateTable.setItem(0, self.COLUMNS_DICT["Copy"]["index"], self.copy_path_icon())

    def table_data_init(self):
        with db_session():
            result = get_image_duplicates(
                image_id=self.sourceImage["id"], similarity_threshold=0.5
            )

            if result:
                for idx, duplicate_data in enumerate(result, 2):
                    self.duplicateTable.setRowCount(idx)
                    # parse duplicate data
                    image, similarity_param = duplicate_data[0], str(duplicate_data[1])

                    str_image_idx = str(idx)

                    self.local_IMAGE_PATH_DICT[str_image_idx] = {
                        "id": image.id,
                        "name": image.image_name,
                        "additional_attrs": {
                            "height": image.image_height,
                            "width": image.image_width,
                        },
                        "folder": image.image_path,
                        "full_path": image.full_path(),
                    }

                    self.duplicateTable.setItem(
                        idx - 1, self.COLUMNS_DICT["ID"]["index"], QTableWidgetItem(str_image_idx)
                    )
                    self.duplicateTable.setItem(
                        idx - 1,
                        self.COLUMNS_DICT["File name"]["index"],
                        QTableWidgetItem(image.image_name),
                    )
                    self.duplicateTable.setItem(
                        idx - 1,
                        self.COLUMNS_DICT["Similarity"]["index"],
                        QTableWidgetItem(similarity_param),
                    )

                    self.duplicateTable.setItem(
                        idx - 1, self.COLUMNS_DICT["Directory"]["index"], self.open_folder_icon()
                    )
                    self.duplicateTable.setItem(
                        idx - 1, self.COLUMNS_DICT["View"]["index"], self.open_image_icon()
                    )
                    self.duplicateTable.setItem(
                        idx - 1, self.COLUMNS_DICT["Copy"]["index"], self.copy_path_icon()
                    )
                    self.duplicateTable.setItem(
                        idx - 1, self.COLUMNS_DICT["Delete"]["index"], self.delete_image_icon()
                    )

    def table_click_event(self, row, column):
        image_id = self.duplicateTable.item(row, 0).text()

        # show selected image info
        self.duplicateImageNameField.setText(self.local_IMAGE_PATH_DICT[image_id]["name"])

        # show selected image name
        self.duplicateImageParamsField.setText(
            f"{self.local_IMAGE_PATH_DICT[image_id]['additional_attrs']['height']}px"
            + f" x {self.local_IMAGE_PATH_DICT[image_id]['additional_attrs']['width']}px"
        )

        # show selected image in right column
        self.duplicateImageField.setPixmap(
            QPixmap(self.local_IMAGE_PATH_DICT[image_id]["full_path"]).scaled(
                300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
        )
        # check if user click and try delete not src image
        if int(image_id) > 1 and column == self.COLUMNS_DICT["Delete"]["index"]:
            self.delete_duplicate(self.local_IMAGE_PATH_DICT[image_id]["id"], row)

        # if try open image source directory
        elif column == self.COLUMNS_DICT["Directory"]["index"]:
            open_path(path=self.local_IMAGE_PATH_DICT[image_id]["folder"])

        # if try open image file
        elif column == self.COLUMNS_DICT["View"]["index"]:
            open_path(path=self.local_IMAGE_PATH_DICT[image_id]["full_path"])

        # if try copy image file
        elif column == self.COLUMNS_DICT["Copy"]["index"]:
            try:
                result = copy_image(self.local_IMAGE_PATH_DICT[image_id]["full_path"])
                if result:
                    QMessageBox.information(
                        self,
                        "Copy path",
                        "Success!\nFile copied to clipboard!",
                        QMessageBox.Ok,
                        QMessageBox.Ok,
                    )
                else:
                    QMessageBox.warning(
                        self,
                        "Copy path",
                        "Error!\nSorry, i can`t copy image to clipboard.",
                        QMessageBox.Ok,
                        QMessageBox.Ok,
                    )

            except Exception:
                print(traceback.format_exc())
                QMessageBox.warning(
                    self,
                    "Copy path",
                    f"Error!\n{traceback.format_exc()}",
                    QMessageBox.Ok,
                    QMessageBox.Ok,
                )

    def delete_duplicate(self, image_id: str, row: str):
        message = QMessageBox().question(
            self,
            "Confirm deletion",
            "Delete duplicate media file?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if message == QMessageBox.Yes:
            self.duplicateTable.removeRow(row)
            # run custom delete
            with db_session():
                Image[int(image_id)].custom_delete()

            QMessageBox().information(
                self, "File deletion", "File success deleted", QMessageBox.Ok, QMessageBox.Ok
            )
        elif message == QMessageBox.No:
            pass

    def closeEvent(self, event):
        self.closeTrigger.emit(self.sourceImageRawId)
        self.close()
