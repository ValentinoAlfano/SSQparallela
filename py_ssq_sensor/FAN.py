# coding=utf-8

import RPi.GPIO as GPIO
import time
import datetime

class FAN_Exception(Exception):
    pass


class FAN():

    def __init__(self,pin=21): #pin in BCM
        self.pin=pin

    def turn_on_test(self,secs):
        GPIO.setup(self.pin,GPIO.OUT)
        GPIO.output(self.pin,0)

        time.sleep(secs)

        GPIO.output(self.pin,1)
        GPIO.cleanup(self.pin)


def test():
    GPIO.setmode(GPIO.BCM)
    fan=FAN()

    fan.turn_on_test(10)

if __name__ == '__main__':
    start=datetime.datetime.now()
    test()
    end=datetime.datetime.now()
    delta=end-start
    print(delta.total_seconds())