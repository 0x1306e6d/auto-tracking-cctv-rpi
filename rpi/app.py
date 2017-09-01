import logging

from rpi.config import (
    DEFAULT_CAMERA_WIDTH,
    DEFAULT_CAMERA_HEIGHT,
    DEFAULT_CAMERA_FRAMERATE,

    DEFAULT_GATEWAY_IP,
    DEFAULT_GATEWAY_PORT,
)
from rpi.hw.camera import RPiCamera
from rpi.net.connector import GatewayConnector

logger = logging.getLogger(__name__)


class RPi(object):
    def __init__(self, args):
        self.__args = args
        self.__camera = None
        self.__connector = None

    def start(self):
        logger.info('Starting auto tracking cctv rpi')
        logger.debug('args = {}'.format(self.__args))

        self.__init_camera()
        self.__init_connector()

        self.try_connect_until_connected()

    def try_connect_until_connected(self):
        try:
            self.__connector.try_connect()
            logger.info('GatewayConnector is connected. ({} -> {})'.
                        format(self.__connector.local_address,
                               self.__connector.remote_address))
        except:
            self.try_connect_until_connected()

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
        logger.debug('GatewayConnector is initialzed. connector = {}'.
                     format(self.__connector))
