import logging
import struct

from rpi.config import (
    DEFAULT_CAMERA_WIDTH,
    DEFAULT_CAMERA_HEIGHT,
    DEFAULT_CAMERA_FRAMERATE,

    DEFAULT_GATEWAY_IP,
    DEFAULT_GATEWAY_PORT,
)
from rpi.hw.motor import (
    DIRECTION_UP,
    DIRECTION_DOWN,
    DIRECTION_LEFT,
    DIRECTION_RIGHT
)
from rpi.hw.camera import RPiCamera
from rpi.hw.motor import RPiMotor, is_valid_direction
from rpi.net.connector import GatewayConnector
from rpi.net.packet import Opcode, encode_packet

logger = logging.getLogger(__name__)


class RPi(object):
    def __init__(self, args):
        self.__args = args
        self.__camera = None
        self.__connector = None
        self._up_down_motor = RPiMotor(DIRECTION_UP | DIRECTION_DOWN)
        self._left_right_motor = RPiMotor(DIRECTION_LEFT | DIRECTION_RIGHT)

    def _get_motor_by_direction(self, direction):
        if self._up_down_motor.is_my_direction(direction):
            return self._up_down_motor
        if self._left_right_motor.is_my_direction(direction):
            return self._left_right_motor

    def start(self):
        logger.info('Starting auto tracking cctv rpi')
        logger.debug('args = {}'.format(self.__args))

        self.__init_camera()
        self.__init_connector()

        self.try_connect_until_connected()
        self.send_device_info()

    def try_connect_until_connected(self):
        try:
            self.__connector.try_connect()
            logger.info('GatewayConnector is connected. ({} -> {})'.
                        format(self.__connector.local_address,
                               self.__connector.remote_address))
        except:
            self.try_connect_until_connected()

    def send_device_info(self):
        logger.debug('Sending device info...')

        body = struct.pack('!IIH',
                           self.__camera.resolution[0],
                           self.__camera.resolution[1],
                           self.__camera.framerate)
        self.__connector.send(encode_packet(Opcode.SETUP, body))

    def __init_camera(self):
        width = self.__args.width
        height = self.__args.height
        if not width:
            width = DEFAULT_CAMERA_WIDTH
            logger.debug('RPiCamera width is not configured.')
        if not height:
            height = DEFAULT_CAMERA_HEIGHT
            logger.debug('RPiCamera height is not configured.')
        resolution = (int(width), int(height))

        framerate = self.__args.framerate
        if not framerate:
            framerate = DEFAULT_CAMERA_FRAMERATE
            logger.debug('RPiCamera framerate is not configured.')
        framerate = int(framerate)

        self.__camera = RPiCamera(resolution=resolution, framerate=framerate)
        logger.debug('RPiCamera is initialized. camera = {}'.
                     format(self.__camera))

    def __init_connector(self):
        ip = self.__args.ip
        port = self.__args.port
        if not ip:
            ip = DEFAULT_GATEWAY_IP
            logger.debug('GatewayConnector ip is not configured.')
        if not port:
            port = DEFAULT_GATEWAY_PORT
            logger.debug('GatewayConnector port is not configured.')
        address = (ip, int(port))

        self.__connector = GatewayConnector(address=address)
        self.__connector.register_handler(Opcode.RECORD, self.__on_record)
        self.__connector.register_handler(Opcode.PAUSE, self.__on_pause)
        self.__connector.register_handler(Opcode.MOVE, self.__on_move)
        logger.debug('GatewayConnector is initialzed. connector = {}'.
                     format(self.__connector))

    def __on_record(self, body):
        self.__camera.record(self.__connector)

    def __on_pause(self, body):
        self.__camera.pause()

    def __on_move(self, body):
        body = struct.unpack('!H', body)
        direction = body[0]

        if is_valid_direction(direction):
            motor = self._get_motor_by_direction(direction)
            if motor is not None:
                motor.move(direction)

        self.__connector.send(encode_packet(Opcode.MOVED))
