import threading
import datetime
import time
import logging
import os
from queue import Queue
from typing import Dict

import numpy as np
import cv2

from config import cfg
from camera import Camera

_frames_queue = Queue(cfg['camera_frames_que_size']) # put: frames from CamWorker threads; get: FrameProcessor
_stop_flag = False  # set True to stop all threads

class Frame:
    """ camera frame (image, cam info, timestamp) """
    def __init__(self, cam_id: int, image: np.ndarray, timestamp: str):
        self.cam_id:int = cam_id
        self.cam_name:str = Camera.cam_list[cam_id].cam_name
        self.timestamp:str = timestamp
        self.image:np.ndarray = image

    def __str__(self):
        return f"Frame({self.cam_id},{self.cam_name},{self.timestamp})"


class CamWorker(threading.Thread):
    """ one thread per each cam """
    def __init__(self, cam:Camera):
        super().__init__(name="_worker_" + cam.cam_name)
        self.cam : Camera = cam

    def run(self):
        """ run endless: take image, create frame, put in queue """
        logging.debug(f"{self.cam} is waiting for connect")
        self.cam.open()
        logging.info(f"{self.cam} connected")
        while not _stop_flag:
            if not _frames_queue.full():
                self.cam.get_frame()
                if not self.cam.read_ok:
                    logging.warning(f"Read error in {self.cam}")
                    time.sleep(5)
                    continue
                frame = Frame(self.cam.cam_id,
                              self.cam.image,
                              datetime.datetime.now().strftime("%y-%m-%d_%H:%M:%S:%f"))
                _frames_queue.put(frame)
                logging.debug(f'Put {frame}. Quesize={_frames_queue.qsize()}')


class FrameProcessor(threading.Thread):
    """ process main queue: take frames, call appropriate handlers """
    def __init__(self):
        super().__init__(name='FrameProcessor')
        return

    def run(self):
        while not _stop_flag:
            if not _frames_queue.empty():
                frame: Frame = _frames_queue.get()
                logging.debug(f'Get {frame}. Qsize = {_frames_queue.qsize()}')
                if cfg['show_frames']:
                    show_frame(frame)
                if cfg['write_frames']:
                    FrameWriter.write_frame(frame)


class FrameWriter:
    """ Write frames to videofile

    videofiles are being created when first frame is arrived (to avoid manual configuring of shape info)
    """
    _handles: Dict[int, cv2.VideoWriter] = {}

    @classmethod
    def _create_video_file(cls, frame:Frame) -> cv2.VideoWriter:
        if frame.cam_id in cls._handles.keys():  # is already opened
            return cls._handles[frame.cam_id]
        folder = cfg['write_frames_folder']
        os.makedirs(folder, exist_ok=True)
        file_name = f"{folder}{frame.cam_name}{cfg['write_frames_suffix']}"
        shape = (frame.image.shape[1], frame.image.shape[0])
        fh = cv2.VideoWriter(file_name, cfg['write_frames_four_cc'], cfg['write_frames_fps'], shape)
        cls._handles[frame.cam_id] = fh
        logging.debug(f"Video file {file_name} created: shape={shape}, fps={cfg['write_frames_fps']}")
        return fh

    @classmethod
    def write_frame(cls, frame: Frame):
        try:
            fh = cls._handles[frame.cam_id]
        except KeyError:
            fh = cls._create_video_file(frame)
        fh.write(frame.image)

    @classmethod
    def close_all(cls):
        """ close all opened video files """
        for cam_id in cls._handles.keys():
            cls._handles[cam_id].release()
            logging.debug(f'File for {Camera.cam_list[cam_id]} is closed')

# vserv own functions:

def show_frame(frame: Frame):
    """ show cam frame in opencv window related to this cam """
    cv2.imshow(frame.cam_name, frame.image)
    ch = cv2.waitKey(1) & 0xFF
    if ch in [ord('q'), ord('Q'), 27]:
        logging.warning('Cancelled by user')
        stop_vserv()

def wait_workers_to_stop():
    logging.debug("waiting cam workers to stop:")
    while True:
        time.sleep(1)
        workers_left = len([ t.name for t in threading.enumerate() if t.name.startswith("_worker_")])
        logging.debug(f"{workers_left} workers left ...")
        if not workers_left:
            break
    logging.debug("all workers stopped")

def stop_vserv():
    """ Stop work. Close all threads"""
    global _stop_flag
    _stop_flag = True
    FrameWriter.close_all() # close opened write-streams
    cv2.destroyAllWindows()
    wait_workers_to_stop()


def main():
    logging.basicConfig(level=logging.DEBUG, style='{', format='{threadName:22s}:{message}')

    Camera.init_cameras()

    fp = FrameProcessor()
    fp.start()
    logging.debug('FrameProcessor started')

    for cam in Camera.cam_list:
        CamWorker(cam).start()
        logging.debug(f'CamWorker for {cam} started')
    try:
        fp.join()  # just wait till FrameProcessor will be stopped
    except KeyboardInterrupt:
        logging.debug('Keyboard interrupt')
        stop_vserv()
    logging.debug('Video Server finished')


if __name__ == "__main__":
    main()

