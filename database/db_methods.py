import collections

from database import Image, ImageTag, Video, ImageDuplicates, db_session

@db_session(retry=3)
def save_new_files(indexed_files: collections.defaultdict, file_type: str):
    """
    Function get files dict and files type and save it to DB

    :param indexed_files: Dict with all indexed files

    :param file_type: Files type - `image` or `video`
    """
    if file_type=='image':
        for _, image_data in indexed_files.items():
            # if current image+path not exist
            if not Image.get(image_path=image_data['namepath'][1]):
                Image(image_name=image_data['namepath'][0],
                      image_path=image_data['namepath'][1],
                      image_dhash=image_data['dhash'],
                      image_md5_hash=image_data['md5_hash'])

    elif file_type=='video':
        for _, video_data in indexed_files.items():
            # if current video+path not exist
            if not Video.get(video_path=video_data['namepath'][1]):
                Video(video_name=video_data['namepath'][0],
                      video_path=video_data['namepath'][1])

        
@db_session(retry=3)
def save_images_duplicates(hamming_pairs: collections.deque):
    """
    Function get image files list and save them to DB

    :param hamming_pairs: List like:
                            (
                                (image_dhash, image_id),
                                (image_dhash, image_id),
                                hamming_distance                                            
                            )

    """
    for pair in hamming_pairs:
        Image[pair[0][0][1]].image_duplicates.create(image_hamming_id=pair[0][1][1],
                                                     images_hamming_distance=pair[1])

        