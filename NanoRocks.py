
import subprocess
import os
import time as time
import cv2
import numpy as np
import pigpio
from picamera2 import Picamera2
from libcamera import controls
from picamera2.encoders import H264Encoder

class NanoRocks:
    __RECORDING_START_DELAY = 0
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
    __video_file_name = ""
    __outputFile = ""
    
    def __init__(self, solenoidPin, ledPin, videoFileName):
        # Add the pins and save path.
        self.__solenoidPin = solenoidPin
        self.__ledPin = ledPin
        self.__video_file_name = videoFileName

        return
    
    def begin(self): 
        # GPIO Setup.
        self.__gpio = pigpio.pi()
        self.__gpio.set_mode(self.__solenoidPin, pigpio.OUTPUT)
        self.__gpio.set_mode(self.__ledPin, pigpio.OUTPUT)

        # Camera Setup.
        self.__piCam = Picamera2()
        config = self.__piCam.create_video_configuration(main={"size":(1920,1080)})
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
            self.__outputFile = self.__video_file_name + ".h264"
            self.__piCam.start_recording(self.__camEncoder, self.__outputFile)
            self.__piCam.set_controls({"AfMode": controls.AfModeEnum.Continuous})
            if(self.__RECORDING_START_DELAY > 0): time.sleep(self.__RECORDING_START_DELAY)
            self.__isRecording = True

        # Turn off recording.
        else:
            self.__piCam.stop_recording()
            subprocess.run([
                "ffmpeg",
                "-framerate", "30",  
                "-i", self.__outputFile,
                "-c", "copy",
                self.__video_file_name + ".mp4"
            ], check=True)
            os.remove(self.__outputFile)
            self.__isRecording = False

        return

    def updateTimeStamp(self, time):
        colour = (0, 255, 0, 255)
        origin = (0, 30)
        font = cv2.FONT_HERSHEY_COMPLEX_SMALL  
        scale = 1
        thickness = 2
        overlay = np.zeros((640, 480, 4), dtype=np.uint8)
        cv2.putText(overlay, str(time), origin, font, scale, colour, thickness)
        self.__piCam.set_overlay(overlay)
        return
