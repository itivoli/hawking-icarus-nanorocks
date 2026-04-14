import pigpio
import time

HIGH = 1
LOW = 0

testPin = 22
testDur = 10  # in seconds.
toggleFreq = 2 # in Hz.
    
GPIO = pigpio.pi()
GPIO.set_mode(testPin, pigpio.OUTPUT)
#"""
for tick in range(testDur): 
    GPIO.write(testPin, HIGH)
    time.sleep(1/toggleFreq)
    GPIO.write(testPin, LOW)
    time.sleep(1/toggleFreq)
    print(tick)
#"""

"""
# Wait loop.
for tick in range(testDur):
	time.sleep(toggleFreq)
	
"""

# done.
print("done")
