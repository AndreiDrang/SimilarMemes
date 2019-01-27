import json

def get_settings()->dict:
    """
    """
    with open('image_processing/settings.json', 'r') as settings_file:
        settings_data = json.loads(settings_file.read())
    
    return settings_data
