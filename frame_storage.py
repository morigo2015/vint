""" provide async put/get storage for video frames
"""
from queue import Queue, Empty, Full

from config import cfg

class Frame:
    cam_id : int
    time : int
    image = None # numpy array

q_max = cfg['frame_storage_size']
frame_storage = Queue(q_max)

def add_frame(frame:Frame):
    pass

def get_frame() -> Frame :
    pass


