import logging
import queue
import socket
import struct
import threading

from rpi.net.packet import (
    Opcode,
    encode_packet,
    decode_packet,
)

logger = logging.getLogger(__name__)


class GatewayConnector(object):
    def __init__(self, address):
        self.local_address = None
        self.remote_address = address
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        self.__socket.setsockopt(socket.SOL_SOCKET, socket.TCP_NODELAY, True)
        self.__handlers = {}

        self.__receive_thread = threading.Thread(target=self.__receive_forever,
                                                 name='gateway-connector-receive-thread')

        self.__send_queue = queue.Queue()
        self.__send_event = threading.Event()
        self.__send_thread = threading.Thread(target=self.__send_forever,
                                              name='gateway-connector-send-thread')

    def register_handler(self, opcode, handler):
        self.__handlers[opcode] = handler

    def try_connect(self):
        logger.debug('Try to connect gateway at {}'.
                     format(self.remote_address))

        self.__socket.connect(self.remote_address)
        self.__receive_thread.start()
        self.__send_thread.start()
        self.local_address = self.__socket.getsockname()

    def send(self, packet):
        self.__send_queue.put(packet)
        self.__send_event.set()

    def receive(self, n):
        packet = self.__socket.recv(n)
        while len(packet) < n:
            packet += self.__socket.recv(n - len(packet))
        return packet

    def __receive_forever(self):
        while True:
            packet_size = struct.calcsize('!L')
            packet_size = self.receive(packet_size)
            packet_size = struct.unpack('!L', packet_size)[0]
            packet = self.receive(packet_size)

            opcode, body = decode_packet(packet)
            handler = self.__handlers.get(opcode)

            if handler:
                handler(body)
            else:
                logger.error('Invalid opcode: {}, body: {}'.
                             format(opcode, body))

    def __send_forever(self):
        while True:
            self.__send_event.wait()
            try:
                while not self.__send_queue.empty():
                    packet = self.__send_queue.get()
                    if packet:
                        self.__socket.send(packet)
            finally:
                self.__send_event.clear()
