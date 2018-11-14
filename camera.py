""" camera.py - actions with video cameras"""

import csv
from typing import List

import cv2
import numpy as np

from config import cfg


class Camera:
    cam_list: List["Camera"] = []
    cam_list_size: int = 0

    def __init__(self, cam_name: str, access_str: str):
        self.cam_id: int = Camera.cam_list_size
        Camera.cam_list_size += 1
        self.cam_name: str = cam_name
        self._access_str: str = access_str
        self.read_ok: bool = False
        self.image: np.ndarray = None
        self._handle: cv2.VideoCapture = None

    def __str__(self):
        return f"Cam({self.cam_id},{self.cam_name})"

    def __repr__(self):
        return self.__str__()

    def open(self) -> bool:
        self._handle = cv2.VideoCapture(self._access_str)
        return self._handle.isOpened()

    def get_frame(self) -> bool:
        """ read next frame from cam, return True if OK"""
        ret, self.image = self._handle.read()
        self.read_ok = False if ret is False or self._handle.isOpened is False else True
        return self.read_ok

    def close(self):
        self._handle.release()
        self._handle = None

    @classmethod
    def init_cameras(cls):
        """ init list of cameras based on file-stored camera info """
        with open(cfg['camera_info_file'], newline='') as csvfile:
            reader = csv.reader(csvfile)
            _ = reader.__next__()  # skip headers
            for row in reader:
                if row[0].strip() == '+':
                    cls.cam_list.append(Camera(cam_name=row[1], access_str=row[2]))

    @classmethod
    def print_cameras(cls):
        print('Camera list: ')
        for cam in cls.cam_list:
            print(cam)

    @classmethod
    def check_cameras(cls):
        for cam in cls.cam_list:
            cam.open()
            print(f"{cam} - {'OK' if cam._handle.isOpened() else 'BAD'}")
            cam.close()


if __name__ == "__main__":
    Camera.init_cameras()
    Camera.print_cameras()
    # Camera.check_cameras()

