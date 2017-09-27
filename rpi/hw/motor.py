import logging
import time

from RPi import GPIO

logger = logging.getLogger(__name__)

DIRECTION_UP = 0x01
DIRECTION_DOWN = 0x02
DIRECTION_LEFT = 0x04
DIRECTION_RIGHT = 0x08

INITIAL_DUTY_CYCLE = 7.5
MINIMUM_DUTY_CYCLE = 3.0
MAXIMUM_DUTY_CYCLE = 12.0

MOVEMENT_TIME = 0.3
MOVEMENT_FREQUENCY = 10


def is_valid_direction(direction):
    return direction == DIRECTION_UP or \
        direction == DIRECTION_DOWN or \
        direction == DIRECTION_LEFT or \
        direction == DIRECTION_RIGHT


def _get_motor_gpio_number(direction):
    if direction == DIRECTION_UP or \
            direction == DIRECTION_DOWN:
        return 13
    elif direction == DIRECTION_LEFT or \
            direction == DIRECTION_RIGHT:
        return 11


def _get_delta(direction):
    if direction == DIRECTION_UP or \
            direction == DIRECTION_RIGHT:
        return 0.25
    elif direction == DIRECTION_DOWN or \
            direction == DIRECTION_LEFT:
        return -0.25


class RPiMotor(object):
    def __init__(self, direction, initial_duty_cycle=INITIAL_DUTY_CYCLE):
        self._direction = direction
        self._duty_cycle = initial_duty_cycle

    def is_my_direction(self, direction):
        return self._direction & direction

    def move(self, to):
        if self.is_my_direction(to):
            logger.debug('Move RPiMotor from {} to {}'.format(self._duty_cycle, to))
            gpio_number = _get_motor_gpio_number(to)

            GPIO.setmode(GPIO.BOARD)
            GPIO.setup(gpio_number, GPIO.OUT)
            pwm = GPIO.PWM(gpio_number, 50)
            pwm.start(self._duty_cycle)

            try:
                delta = _get_delta(to)
                if delta < 0 and self._duty_cycle <= MINIMUM_DUTY_CYCLE:
                    logger.info('minimum')
                    return
                if delta > 0 and self._duty_cycle >= MAXIMUM_DUTY_CYCLE:
                    logger.info('maximum')
                    return

                self._duty_cycle += delta
                pwm.ChangeDutyCycle(self._duty_cycle)
                time.sleep(0.04)

#                for _ in range(MOVEMENT_FREQUENCY):
#                    if delta < 0 and self._duty_cycle <= MINIMUM_DUTY_CYCLE:
#                        logger.info('DutyCycle is not minimum value.')
#                        break
#                    if delta > 0 and self._duty_cycle >= MAXIMUM_DUTY_CYCLE:
#                        logger.info('DutyCycle is not maximum value.')
#                        break
#
#                    self._duty_cycle += delta
#                    pwm.ChangeDutyCycle(self._duty_cycle)
#                    time.sleep(sleep_time)

            finally:
                pwm.stop()
                GPIO.cleanup()
