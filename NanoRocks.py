
import datetime
import os.path
import pigpio
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder

class NanoRocks:
    __SOLENOID_DELAY = 500  # 500 ms.
    __PIN_HIGH = 1
    __PIN_LOW = 0

    __gpio = None
    __piCam = None
    __camEncoder = None

    __solenoidPin = 0
    __ledPin = 0
    __solenoidPinState = False
    __ledPinState = False
    __active = False 
    __isRecording = False
    __video_save_path = ""
    
    def __init__(self, solenoidPin, ledPin, videoSavePath):
        # Add the pins and save path.
        self.__solenoidPin = solenoidPin
        self.__ledPin = ledPin
        self.__video_save_path = videoSavePath

        return
    
    def begin(self): 
        # GPIO Setup.
        self.__gpio = pigpio.pi()
        self.__gpio.set_mode(self.__solenoidPin, pigpio.OUTPUT)
        self.__gpio.set_mode(self.__ledPin, pigpio.OUTPUT)

        # Camera Setup.
        self.__piCam = Picamera2()
        config = self.__piCam.create_video_configuration()
        self.__piCam.configure(config)
        self.__camEncoder = H264Encoder(10000000)

        return

    def end(self):
        # Ensure solenoid is off.
        self.__gpio.write( self.__solenoidPin,  self.__PIN_LOW) 
        self.toggleRecording()
        return

    def toggleSolenoid(self):
        self.__solenoidPinState = (self.__PIN_LOW) if (self.__solenoidPinState == self.__PIN_HIGH) else (self.__PIN_LOW)
        self.__gpio.write( self.__solenoidPin,  self.__solenoidPinState)
        return

    def toggleLed(self):
        self.__ledPinState = (self.__PIN_LOW) if (self.__ledPinState == self.__PIN_HIGH) else (self.__PIN_LOW)
        self.__gpio.write( self.__ledPin,  self.__ledPinState)
        return

    def toggleRecording(self):
        # Toggle Led.
        self.toggleLed()

        # Turn on recording.
        if(not self.__isRecording):
            date = datetime.datetime.now().strftime("%H_%M_%S")
            filename = os.path.join(self.__video_save_path + ".h264")
            self.__piCam.start_recording(self.__camEncoder, filename)
            self.__isRecording = True

        # Turn off recording.
        else:
            self.__piCam.stop_recording()
            self.__isRecording = False

        return

