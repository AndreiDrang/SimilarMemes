# SimilarMemes

Script for searching similar image/video files in folder.


## ATTENTION!

1) When using raw code you need to have the latest version of PyQt5 in order to prevent bugs the older versions provide. Don't forget to

`pip install pyqt5 --upgrade`
    
2) If you have problems playing video files please install [**K-Lite Codec Pack**](http://www.codecguide.com/download_kl.htm) on your computer.


## GUI description


## Backend description

**Before using any DB model/method u must connect to DB - from `models` import `connection` and start it.**

### Models

### DB-methods

File - **database/db_methods.py**

1. Function ***save_new_files***;

    Params:

    1. `indexed_files` - dict with indexed files, from ***index_folder_files***;
    1. `file_type` - string with file type param, variants: `image`/`video`;

    Work:

    Function get indexed files and file type, than checks if this Image is already in the DB, if not - insert new file;

1. Function ***save_images_duplicates***

    Params:

    Work:
1. Function ***get_image_duplicates***

    Params:

    Work:


### Folders indexing

### Image processing

### Video processing
