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

    1. `indexed_files` - `dict` with indexed files, from ***index_folder_files***;
    1. `file_type` - `str` with file type param, variants: `image`/`video`;

    Work:

    Function get indexed files and file type, than checks if this Image is already in the DB, if not - insert new file;

    Return:

    *None*

1. Function ***save_images_duplicates***

    Params:

    1. `pairs` - `list` of lists with composet images pairs from ***feature_description*** function. <br>
    List contain: `(image_id: int, image_id: int, similarity_value: float)`;

    Work:

    Function get images pairs, than checks if this `ImageDuplicates` is already exist in the DB, if not - insert new `ImageDuplicates` element;

    Return:

    *None*

1. Function ***get_image_duplicates***

    Params:
    1. `image_id` - `int` ID of the image to search his pairs;
    1. `similarity_threshold` - `float` similarity threshold to images pairs filtering;

    Work:

    Function get image ID and threshold param, than start searching image with same ID in duplicates pairs and finally filter this pairs by `similarity_threshold` param;<br>
    At the end, the function filters the values by similarity, from the smallest to the largest(**smallest == better**).

    Return:

    `List` of lists, which contains similar `Image` object and similarity param;
    <br>
    For example - `[(Image, <float_similarity>), (Image, <float_similarity>)]`;
    <br>
    **IMPORTANT :**<br>
    Function return only unique images ID's, which not equal to `image_id` from sended params;

1. Function ***group_image_files***

    Params:

    *None*

    Work:

    Function get all images paths and then select for each path - files;
    <br>
    Finally is created `dict`, with **keys** - path names, **values** - image filename + image id from the path;

    Return:

    `Dict` which contain image paths and image files(**from this path**);
    <br>
    For example : 
    ```python
    {
        <path name>: 
            [
                (<filename>, <image ID>),
                (<filename>, <image ID>),
            ],
        <path name>: 
            [
                (<filename>, <image ID>),
                (<filename>, <image ID>),
            ],
    } 
    ```

### Folders indexing

### Image processing

### Video processing
