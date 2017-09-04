import logging
import threading

from picamera import PiCamera

from rpi.config import (
    DEFAULT_CAMERA_WIDTH,
    DEFAULT_CAMERA_HEIGHT,
    DEFAULT_CAMERA_FRAMERATE,
)
from rpi.net.packet import Opcode, encode_packet

logger = logging.getLogger(__name__)


class RPiCamera(object):
    def __init__(self,
                 resolution=(DEFAULT_CAMERA_WIDTH, DEFAULT_CAMERA_HEIGHT),
                 framerate=DEFAULT_CAMERA_FRAMERATE):
        self.resolution = resolution
        self.framerate = framerate
        self.recording = False
        self.__connector = None
        self.__camera = PiCamera(resolution=resolution, framerate=framerate)
        self.__camera_thread = threading.Thread(target=self.__wait_recording,
                                                name='rpi-camera-thread',
                                                daemon=True)
        self.__camera_lock = threading.Lock()

    def write(self, buf):
        if self.__connector is not None:
            self.__connector.send(encode_packet(Opcode.FRAME, buf))

    def record(self, connector, format='mjpeg'):
        if not self.recording:
            with self.__camera_lock:
                if not self.recording:
                    logger.info('Start recording. format={}'.format(format))

                    self.recording = True
                    self.__connector = connector
                    self.__camera.start_recording(output=self, format=format)
                    self.__camera_thread.start()

    def pause(self):
        if self.recording:
            with self.__camera_lock:
                if self.recording:
                    logger.info('Stop recording. format={}'.format(format))

                    self.__camera.stop_recording()
                    self.recording = False

    def __wait_recording(self):
        while self.recording:
            self.__camera.wait_recording(1)
