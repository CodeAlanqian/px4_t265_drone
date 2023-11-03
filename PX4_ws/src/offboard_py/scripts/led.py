import Jetson.GPIO as GPIO
import time
pin = 22

def main():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(pin, GPIO.OUT)
def led_on():
    GPIO.output(pin, GPIO.HIGH)


def led_off():
    GPIO.output(pin, GPIO.LOW)


def loop():
    while(1):
        led_on()     


if __name__ == '__main__': 
    main()
    try:
        loop()
    except KeyboardInterrupt:
        GPIO.cleanup()


