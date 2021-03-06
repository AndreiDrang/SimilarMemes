import os
import json
import logging
import traceback

from PyQt5.QtWidgets import *


logger = logging.getLogger(__name__)


# Reads the json settings file and returns a needed setting value:
def user_json_read(settingName: str):
    try:
        with open(f"gui{os.sep}user_settings.json", "r") as jsonFile:
            jsonData = json.load(jsonFile)
        return jsonData[settingName]

    except Exception as ex:
        warning_message(ex)
        logger.critical(traceback.format_exc())


# Updates a needed setting and rewrites the json settings file:
def user_json_update(settingName: str, settingNewValue: int):
    try:
        with open(f"gui{os.sep}user_settings.json", "r") as jsonFile:
            jsonData = json.load(jsonFile)

        jsonData[settingName] = int(settingNewValue)

        with open(f"gui{os.sep}user_settings.json", "w") as jsonFile:
            json.dump(jsonData, jsonFile)

    except Exception as ex:
        warning_message(ex)
        logger.critical(traceback.format_exc())


# Reads the json settings file and returns a needed setting value:
def db_json_read(settingName: str):
    try:
        with open(f"database{os.sep}db_config.json", "r") as jsonFile:
            jsonData = json.load(jsonFile)
        return jsonData[settingName]

    except Exception as ex:
        warning_message(ex)
        logger.critical(traceback.format_exc())


# Updates a needed setting and rewrites the json settings file:
def db_json_update(settingName: str, settingNewValue: str):
    try:
        with open(f"database{os.sep}db_config.json", "rt") as jsonFile:
            jsonData = json.load(jsonFile)

        jsonData[settingName] = settingNewValue

        with open(f"database{os.sep}db_config.json", "wt") as jsonFile:
            json.dump(jsonData, jsonFile)

    except Exception as ex:
        warning_message(ex)
        logger.critical(traceback.format_exc())


# Reads the json settings file and returns a needed setting value:
def processing_json_read(settingName: str):
    try:
        with open(f"image_processing{os.sep}settings.json", "r") as jsonFile:
            jsonData = json.load(jsonFile)
        return jsonData[settingName]

    except Exception as ex:
        warning_message(ex)
        logger.critical(traceback.format_exc())


# Updates a needed setting and rewrites the json settings file:
def processing_json_update(settingName: str, settingNewValue: float):
    try:
        with open(f"image_processing{os.sep}settings.json", "rt") as jsonFile:
            jsonData = json.load(jsonFile)

        jsonData[settingName] = settingNewValue

        with open(f"image_processing{os.sep}settings.json", "wt") as jsonFile:
            json.dump(jsonData, jsonFile)

    except Exception as ex:
        warning_message(ex)
        logger.critical(traceback.format_exc())


# Shows a dialog if an error occurs (e.g., if the file is missing):
def warning_message(ex):
    warning = QMessageBox()
    warning.setIcon(QMessageBox.Warning)
    warning.setWindowTitle("Warning!")
    warning.setText("An error has occured!\nMore info in - `logs/errors.log`")
    warning.setInformativeText(str(ex))
    warning.setStandardButtons(QMessageBox.Ok)
    warning.exec()
