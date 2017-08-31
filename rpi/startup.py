import argparse


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
    pass
