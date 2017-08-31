import argparse
import logging
import os


def configure_logging():
    format = '[%(asctime)s][%(threadName)s:%(module)s:%(funcName)s [%(lineno)d]]'
    format += os.linesep
    format += '[%(levelname)7s] %(message)s'

    logging.basicConfig(format=format, level=logging.DEBUG)
    logging.debug('logging is configured.')


def parse_args():
    parser = argparse.ArgumentParser(description='Auto Tracking CCTV RPi')

    parser.add_argument('-i', '--ip', action='store',
                        help='gateway\'s ip address')
    parser.add_argument('-p', '--port', action='store', type=int,
                        help='gateway\'s port')

    parser.add_argument('--width', action='store', type=int,
                        help='rpi camera width resolution')
    parser.add_argument('--height', action='store', type=int,
                        help='rpi camera height resolution')
    parser.add_argument('--framerate', action='store', type=int,
                        help='rpi camera framerate')

    return parser.parse_args()


def start_from_command_line():
    configure_logging()
