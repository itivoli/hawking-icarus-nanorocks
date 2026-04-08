
if __name__ == "__main__":
    print("Icarus.py inccorrectly being used as top level.")
    exit()

from Timer import Timer
from NanoRocks import NanoRocks
from mpu6050 import mpu6050
import numpy as np

class Icarus:

    BOOST_MEAS_PERIOD = 30 * 1000         # Seconds.
    SOLENOID_TRIGGER_PERIOD = 0.5 * 1000  # Seconds.

    STANDARD_G = "Standard_G"
    MICRO_G = "Micro_G"
    HIGH_G = "High_G"

    __MICRO_G_BOUND = 1         # Bound to detect microgravity (m/s^2)
    __HIGH_G_BOUND = 20         # Bound to detect high accleration (m/s^2)      

    __ACCEL_X_OS = 0.5058       # Calibrated accelormeter X-offset.
    __ACCEL_Y_OS = -0.0998      # Calibrated accelormeter Y-offset.
    __ACCEL_Z_OS = 7.1075       # Calibrated accelormeter Z-offset.
    __GYRO_X_OS = -0.3365       # Calibrated gyroscope X-offset.
    __GYRO_Y_OS = -1.1137       # Calibrated gyroscope Y-offset.
    __GYRO_Z_OS = -1.4057       # Calibrated gyroscope Z-offset.

    __iTimer = None
    __mpu = None 
    __nanoRocks = None

    __logFileName = None
    __logFile = None
    __bufferLength = 5
    __bufferIndex = 0 
    __mpuBuffer = None 
    __gravityState = STANDARD_G
    __experimentTimerActive = False

    def __calibrateMPU(self):

        # Initialize.
        self.__ACCEL_X_OS = 0
        self.__ACCEL_Y_OS = 0
        self.__ACCEL_Z_OS = 0
        self.__GYRO_X_OS = 0
        self.__GYRO_Y_OS = 0
        self.__GYRO_Z_OS = 0

        xAccel = 0
        yAccel = 0
        zAccel = 0
        xGyro = 0
        yGyro = 0
        zGyro = 0

        # Take samples.
        sample_size = self.__bufferLength * 10
        for i in range(sample_size):
            accel_data = self.__mpu.get_accel_data()
            gyro_data = self.__mpu.get_gyro_data()

            xAccel += accel_data['x']
            yAccel += accel_data['y']
            zAccel += accel_data['z']
            xGyro += gyro_data['x']
            yGyro += gyro_data['y']
            zGyro += gyro_data['z']

            self.delayMillis(100)

        self.__ACCEL_X_OS = xAccel / sample_size
        self.__ACCEL_Y_OS = yAccel / sample_size
        self.__ACCEL_Z_OS = zAccel / sample_size 
        self.__GYRO_X_OS = xGyro / sample_size
        self.__GYRO_Y_OS = yGyro / sample_size
        self.__GYRO_Z_OS = zGyro / sample_size

        return
    
    def __logMPU(self):

        # Read data.
        data = self.__readMPU()
        aData = data[0]
        gData = data[1]

        # Compute accel magnitude.
        magnitude = (aData[0] **2 + aData[1]**2 + aData[2]**2)**0.5

        # Store calibrated acceleration, raw gyro, accel magnitude.
        if(self.__bufferIndex == self.__bufferLength) :
            self.__bufferIndex = 0
        self.__mpuBuffer[self.__bufferIndex] = magnitude
        self.__bufferIndex += 1

        # Output to log file.
        entry = f"{self.__iTimer.getCurrTime()}; {aData[0]}; {aData[1]}; {aData[2]}; {magnitude}; {gData[0]}; {gData[1]}; {gData[2]}\n"
        self.__logFile.write(entry)
        return
    
    def __printMPU(self):
        # Read data.
        data = self.__readMPU()
        aData = data[0]
        gData = data[1]

        # Output to display.
        magnitude = (aData[0] **2 + aData[1]**2 + aData[2]**2)**0.5
        time = f"{self.__iTimer.getCurrTime()}\n"
        accel = f"\tAccel: {aData[0]}; {aData[1]}; {aData[2]}; {magnitude}\n"
        gyro = f"\tGyro: {gData[0]}; {gData[1]}; {gData[2]}\n"
        print(time, accel, gyro)
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

        return [[xAccel, yAccel, zAccel], [xGyro, yGyro, zGyro]]
    
    def __averageBuffer(self):
        return np.average(self.__mpuBuffer)
    
    def __updateGravityStatus(self):
        # Store MPU data in buffers and output log file.
        self.__logMPU()

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
    
    def __init__(self, solenoidPin, ledPin, mpuAddress, logFileName, videoSaveName, bufferLength = 5, highGBound = 20, testingMpu = False):
        self.__iTimer = Timer()
        self.__mpu = mpu6050(mpuAddress)
        self.__nanoRocks = NanoRocks(solenoidPin, ledPin, videoSaveName)
        self.__mpuBuffer = np.zeros(self.__bufferLength)
        self.__logFileName = logFileName
        self.__bufferLength = bufferLength
        self.__HIGH_G_BOUND = highGBound
        self.activate_camera = False if (testingMpu is True) else True
        return

    def begin(self):
        if(self.activate_camera): self.__nanoRocks.begin()

        path = self.__logFileName + ".txt"
        data_header = f"x_a_os: {self.__ACCEL_X_OS},\ny_a_os: {self.__ACCEL_Y_OS},\nz_a_os: {self.__ACCEL_Z_OS},\nx_g_os: {self.__GYRO_X_OS},\ny_g_os: {self.__GYRO_Y_OS}, \nz_g_os: {self.__GYRO_Z_OS}\n"
        table_header = "Time (ms); xAccel(m/s^2); yAccel(m/s^2); zAccel(m/s^2); accel Magnitude; xGyro; yGyro; zGyro\n"

        self.__logFile = open(path, 'w')
        self.__logFile.write(data_header)
        self.__logFile.write(table_header)
        return

    def end(self):
        self.__logFile.close()
        self.__nanoRocks.end()
        return
    
    def delayMillis(self, dur = 10):
        self.__iTimer.delayMillis(dur)
        return

    def loop(self):
        #self.__nanoRocks.updateTimeStamp(self.__iTimer.getCurrTime())
        self.__updateGravityStatus()
        self.delayMillis(100)
        return
    
    def runExperiment(self):
        # Ensure this is called only in active experiments.
        if(self.__nanoRocks.isActive() == False): 
            print("Invalid attempt to run experiment before NanoRocks was activated.")
            return

        # Setup toggle.
        if(self.__experimentTimerActive == False):
            self.__nanoRocks.toggleSolenoid()
            self.__iTimer.begin(self.SOLENOID_TRIGGER_PERIOD)
            self.__experimentTimerActive = True

        # Main toggle.
        elif(self.__iTimer.getTimerExpired()):
            self.__nanoRocks.toggleSolenoid()
            self.__iTimer.begin(self.SOLENOID_TRIGGER_PERIOD)

        return
    
    def getgravityState(self):
        return self.__gravityState

    def getNanoRocks(self):
        return self.__nanoRocks

    def getTimer(self):
        return self.__iTimer
    
    def getAvgAccelMag(self):
        return self.__averageBuffer()
    
    def calibrateAccelerometer(self):
        self.__calibrateMPU()
        return
    
    def showIMUData(self):
        self.__printMPU()
        return