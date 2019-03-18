import os, sys, json
from   PyQt5.QtWidgets  import *


# Reads the json settings file and returns a needed setting value:
def json_read(settingName: str):
	try:
		with open('user_settings.json', 'r') as jsonFile:
			jsonData = json.load(jsonFile)
		return jsonData[settingName]
	
	except Exception as ex:
		warning_message(ex)


# Updates a needed setting and rewrites the json settings file:
def json_update(settingName: str, settingNewValue: int):
	try:
		with open('user_settings.json', 'r') as jsonFile:
			jsonData = json.load(jsonFile)
			
		jsonData[settingName] = int(settingNewValue)
		
		with open('user_settings.json', 'w') as jsonFile:
			json.dump(jsonData, jsonFile)
	
	except Exception as ex:
		warning_message(ex)


# Shows a dialog if an error occurs (e.g., if the file is missing):
def warning_message(ex):
	warning = QMessageBox()
	warning.setIcon(QMessageBox.Warning)
	warning.setWindowTitle('Warning!')
	warning.setText('An error has occured!')
	warning.setInformativeText(str(ex))
	warning.setStandardButtons(QMessageBox.Ok)
	warning.exec()
