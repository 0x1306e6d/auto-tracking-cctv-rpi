import logging
import queue
import socket
import threading

logger = logging.getLogger(__name__)


class GatewayConnector(object):
    def __init__(self, address):
        self.local_address = None
        self.remote_address = address
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        self.__socket.setsockopt(socket.SOL_SOCKET, socket.TCP_NODELAY, True)

        self.__send_queue = queue.Queue()
        self.__send_event = threading.Event()
        self.__send_thread = threading.Thread(target=self.__run_send_thread,
                                              name='GatewayConnector-SendThread',
                                              daemon=True)
        self.__send_thread.start()

    def try_connect(self):
        logger.debug('Try to connect gateway at {}'.
                     format(self.remote_address))

        self.__socket.connect(self.remote_address)
        self.local_address = self.__socket.getsockname()

    def send(self, packet):
        self.__send_queue.put(packet)
        self.__send_event.set()

    def receive(self, n):
        packet = self.__socket.recv(n)
        while len(packet) < n:
            packet += self.__socket.recv(n - len(packet))
        return packet

    def __run_send_thread(self):
        while True:
            self.__send_event.wait()
            try:
                while not self.__send_queue.empty():
                    packet = self.__send_queue.get()
                    if packet:
                        self.__socket.send(packet)
            finally:
                self.__send_event.clear()
