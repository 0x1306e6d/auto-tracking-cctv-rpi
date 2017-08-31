import logging
import socket

logger = logging.getLogger(__name__)


class GatewayConnector(object):
    def __init__(self, address):
        self.address = address
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        self.__socket.setsockopt(socket.SOL_SOCKET, socket.TCP_NODELAY, True)

    def try_connect(self):
        logger.debug('Try to connect gateway at {}'.format(self.address))

        self.__socket.connect(self.address)
        self.address = self.__socket.getsockname()
