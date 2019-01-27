import json

def get_settings()->dict:
    """
    """
    with open('video_processing/settings.json') as settings_file:
        settings_data = json.load(settings_file)
    
    return settings_data
