import json


def get_settings()->dict:
    """
    Function open settings.json file and read data.

    :return: Dict with params from file
    """
    with open('image_processing/settings.json', 'r') as settings_file:
        settings_data = json.loads(settings_file.read())
    
    return settings_data
