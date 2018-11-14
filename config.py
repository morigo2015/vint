# config.py

import os
import cv2

work_dir = os.environ['HOME'] + '/' + 'mypy/vint/'
os.chdir(work_dir)

_folders = {
    'src'   : work_dir + 'src/' ,
    'data'  : work_dir + 'data/',
    'video' : work_dir + 'videos/',
}

cfg = {
    'camera_info_file' : _folders['data'] + 'cameras_info.csv',
    'camera_frames_que_size' : 10, # frames queue size for each cam
    'show_frames' : False, # display input frames from cameras
    'write_frames' : True, # write input frames to video files (separated by cam)
    'write_frames_folder' : _folders['video'],
    'write_frames_fps' : 3.0, # fps for videofiles that save cam frame stream
    'write_frames_four_cc' :cv2.VideoWriter_fourcc( *'XVID'), # four_cc for videofiles
    'write_frames_suffix' : '.avi',
    # 'max_reread_attempt' : 1000, # how many times to reread frame from cam (interval=1 sec) if stream is broken
    # 'frame_storage_size' : 30,
}

