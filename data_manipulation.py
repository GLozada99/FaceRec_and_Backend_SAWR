import io,os
import numpy as np
import face_recognition as fr
import crud
from PIL import Image
from classes import Picture


def process_picture(path: str, large: bool=False) -> tuple[str, bytes, bytes]:
    '''
    Given path of image, takes the face, and encodes it into bytes for storing. Returns name of image, raw picture in bytes, face enconding of numpy array in bytes
    '''
    data = None
    mod = 'large' if large else 'small'
    name = path.split('/')[-1].split('.')[0].split('_')[0]
    pic = fr.load_image_file(path)
    face_encodings = fr.face_encodings(pic,model=mod)
    if face_encodings:
        face_encoding = face_encodings[0].tobytes()
        with open(path, 'rb') as fil:
            raw_bin_pic = fil.read()
            data = (name, raw_bin_pic, face_encoding)
    
    return data  

def _byte_decode(face_bytes: bytes) -> np.ndarray:
    '''
    Decodes bytes into numpy array that represents a face. Returns decoded numpy array
    '''
    face_encoding = np.frombuffer(face_bytes)
    return face_encoding

def _unprocess_picture(name, raw_bin_pic, face_encoding):
    '''
    Takes processed picture data and returns name, picture in bytes and numpy array of faces 
    '''
    picture = Image.open(io.BytesIO(raw_bin_pic))
    face = _byte_decode(face_encoding)
    return name, picture, face

def insert_picture_directory(path: str):
    '''
    Loops through directory of pictures and inserts them into the database
    '''
    for root,_,files in os.walk(path,topdown=True):
        for name in files:
            pic_address = os.path.join(root, name)
            name, picture_bytes, face_bytes = process_picture(pic_address,True)
            newPicture = Picture(name=name,picture_bytes=picture_bytes,face_bytes=face_bytes)
            crud.add_entry(newPicture)

def insert_picture_file(path: str):
    '''
    Inserts single picture into database, given it's path
    '''
    pic_address = path
    name, picture_bytes, face_bytes = process_picture(pic_address,True)
    newPicture = Picture(name=name,picture_bytes=picture_bytes,face_bytes=face_bytes)
    crud.add_entry(newPicture)

def insert_picture_discovered(name, picture_frame, face_encoding):
    '''
    Inserts single picture into database. Used for frames taken live.
    '''
    picture_bytes = picture_frame.tobytes()
    face_bytes = face_encoding.tobytes()
    newPicture = Picture(name=name,picture_bytes=picture_bytes,face_bytes=face_bytes)
    crud.add_entry(newPicture)

def get_work_data():
    '''
    Returns list of pictures in the format (name, picture, face_encoding)
    '''
    pic_list = []
    for pic in crud.get_entries(Picture):
        name = pic.name
        byte_picture = pic.picture_bytes
        face_encoding = pic.face_bytes
        pic_list.append(_unprocess_picture(name,byte_picture,face_encoding))
    return pic_list


