import pigpio
import time

HIGH = 1
LOW = 0
testPin = 17
GPIO = pigpio.pi()
GPIO.set_mode(testPin, pigpio.OUTPUT)
GPIO.write(testPin, HIGH)
time.sleep(2)
GPIO.write(testPin, LOW)
