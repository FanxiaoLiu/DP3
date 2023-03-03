from gpiozero import Servo
from gpiozero import Button as gpioButton
from gpiozero import LED
import gpiozero
import sys
from gpiozero.pins.pigpio import PiGPIOFactory
import time

class Actuator:

    def __init__(self, gpioid):
        # Setting up the pin factory
        gpiozero.Device.pin_factory = PiGPIOFactory('127.0.0.1')
        self.id = gpioid
        self.servo = Servo(gpioid)
    
    def min(self):
        # Moving the actuator to minimum position
        self.servo.min()
        time.sleep(1)
    
    def max(self):
        # Moving the actuator to maximum position
        self.servo.max()
        time.sleep(1)

    def mid(self):
        # Moving the actuator to maximum position
        self.servo.mid()
        time.sleep(1)

led = LED(5)

led.on()
time.sleep(5)