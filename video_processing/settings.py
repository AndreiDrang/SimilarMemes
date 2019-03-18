import os
import json

def get_settings()->dict:
    """
    """
    with open(f'video_processing{os.sep}settings.json') as settings_file:
        settings_data = json.load(settings_file)
    
    return settings_data
