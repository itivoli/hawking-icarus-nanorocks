from Timer import Timer
from NanoRocks import NanoRocks
from mpu6050 import mpu6050
import numpy as np

class Icarus:
    STANDARD_G = 191
    MICRO_G = 119
    HIGH_G = 911

    __MICRO_G_BOUND = 1
    __HIGH_G_BOUND = 10

    __ACCEL_X_OS = 0.5058     # Calibrated accelormeter X-offset.
    __ACCEL_Y_OS = -0.0998    # Calibrated accelormeter Y-offset.
    __ACCEL_Z_OS = 7.1075     # Calibrated accelormeter Z-offset.
    __GYRO_X_OS = -0.3365     # Calibrated gyroscope X-offset.
    __GYRO_Y_OS = -1.1137     # Calibrated gyroscope Y-offset.
    __GYRO_Z_OS = -1.4057     # Calibrated gyroscope Z-offset.

    __BOOST_MEAS_PERIOD = 2 # 2 Seconds.
    __SOLENOID_TRIGGER_PERIOD = 0.5 # 0.5 Seconds.

    __iTimer = None
    __mpu = None 
    __nanoRocks = None

    __logFileName = None
    __logFile = None
    __bufferLength = 10
    __bufferIndex = 0 
    __mpuBuffer = None 
    __gravityState = STANDARD_G

    def __logMPU(self, aData, magnitude, gData):
        entry = f"{self.__iTimer.getCurrTime()}; {aData[0]}; {aData[1]}; {aData[2]}; {magnitude}; {gData[0]}; {gData[1]}; {gData[2]}\n"
        self.__logFile.write(entry)
        return

    def __readMPU(self):
        accel_data = self.__mpu.get_accel_data()
        gyro_data = self.__mpu.get_gyro_data()

        xAccel = accel_data['x'] - self.__ACCEL_X_OS
        yAccel = accel_data['y'] - self.__ACCEL_Y_OS
        zAccel = accel_data['z'] - self.__ACCEL_Z_OS
        xGyro = gyro_data['x'] - self.__GYRO_X_OS
        yGyro = gyro_data['y'] - self.__GYRO_Y_OS
        zGyro = gyro_data['z'] - self.__GYRO_Z_OS
        
        magnitude = (xAccel **2 + yAccel**2 + zAccel**2)**0.5
        self.__logMPU([xAccel, yAccel, zAccel], magnitude, [xGyro, yGyro, zGyro])

        # Store calibrated acceleration, raw gyro, accel magnitude.
        if(self.__bufferIndex == self.__bufferLength) :
            self.__bufferIndex = 0
        self.__mpuBuffer[self.__bufferIndex] = magnitude
        self.__bufferIndex += 1

        # TODO: Add section that logs data to file.

        return
    
    def __averageBuffer(self):
        return np.average(self.__mpuBuffer)
    
    def __updateGravityStatus(self):
        # Read the MPU and store values in the internal buffers.
        self.__readMPU()

        # Take the buffer average and use it to determine Gravity status.
        avgAccelMag = self.__averageBuffer()

        # Set the new Gravity Status.
        if(avgAccelMag >= self.__HIGH_G_BOUND): 
            self.__gravityState = self.HIGH_G
        elif(avgAccelMag <= self.__MICRO_G_BOUND):
            self.__gravityState = self.MICRO_G
        else: 
            self.__gravityState = self.STANDARD_G

        return
    
    def __init__(self, solenoidPin, ledPin, mpuAddress, logFileName, videoSaveName):
        self.__iTimer = Timer()
        self.__mpu = mpu6050(mpuAddress)
        self.__nanoRocks = NanoRocks(solenoidPin, ledPin, videoSaveName)
        self.__mpuBuffer = np.zeros(self.__bufferLength)
        self.__logFileName = logFileName
        return

    def begin(self):
        self.__nanoRocks.begin()

        path = self.__logFileName + ".txt"
        header = "Time (ms); xAccel(m/s^2); yAccel(m/s^2); zAccel(m/s^2); accel Magnitude; xGyro; yGyro; zGyro\n"

        self.__logFile = open(path, 'w')
        self.__logFile.write(header)
        return

    def end(self):
        self.__nanoRocks.end()
        return
    
    def delayMillis(self, dur = 10):
        self.__iTimer.delayMillis(dur)
        return

    def loop(self):
        self.__updateGravityStatus()
        self.delayMillis()
        return
    
    def runExperiment(self):
        self.__nanoRocks.toggleSolenoid()
        delayMS = self.__SOLENOID_TRIGGER_PERIOD * 1000
        self.__iTimer.begin(delayMS)
        return
    
    def getgravityState(self):
        return self.__gravityState

    def getNanoRocks(self):
        return self.__nanoRocks

    def getTimer(self):
        return self.__iTimer