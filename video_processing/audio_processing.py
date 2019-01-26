from moviepy.audio.io.AudioFileClip import AudioFileClip

def audio_processing(audio_clip: AudioFileClip):
    """
    Get audio file processing it and try find same in local DB
    """
    print(audio_clip)
    # create audio fingerprint

