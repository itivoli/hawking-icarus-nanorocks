
if __name__ == "__main__":
    print("Icarus.py inccorrectly being used as top level.")
    exit()

from Timer import Timer
from NanoRocks import NanoRocks
from mpu6050 import mpu6050
import numpy as np
import os


class Icarus:

    BOOST_MEAS_PERIOD = 30 * 1000         # Seconds.
    SOLENOID_TRIGGER_PERIOD = 0.5 * 1000  # Seconds.

    STANDARD_G = "Standard_G"
    MICRO_G = "Micro_G"
    HIGH_G = "High_G"

    __MICRO_G_BOUND = 1         # Bound to detect microgravity (m/s^2)
    __HIGH_G_BOUND = 16         # Bound to detect high accleration (m/s^2). +/- 16g is max possible G-force readable from MPU6050.    

    __ACCEL_X_CAL = {"scale": 1, "offset": 0.5058}  # Calibrated accelormeter X params.
    __ACCEL_Y_CAL = {"scale": 1, "offset": -0.0998}  # Calibrated accelormeter Y params.
    __ACCEL_Z_CAL = {"scale": 1, "offset": 7.1075}   # Calibrated accelormeter Z params.

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

    def __calibrateMPUFromFile(self, mpu_config_file, over_write):
       
        # Read file if it exists.
        file_exists = os.path.isfile(mpu_config_file)
        if(file_exists and (not over_write)): 
            print("Specified calibration file exists. Reading now.")

            mpu_config_file = open(mpu_config_file, 'r')
            calib_params = mpu_config_file.read()
            mpu_config_file.close()

            # Sanitize.
            calib_params = calib_params.split()

            # Set parameters.
            params = calib_params[0].split(",")
            self.__ACCEL_X_CAL["scale"] = float(params[0])
            self.__ACCEL_X_CAL["offset"] = float(params[1])

            params = calib_params[1].split(",")
            self.__ACCEL_Y_CAL["scale"] = float(params[0])
            self.__ACCEL_Y_CAL["offset"] = float(params[1])

            params = calib_params[2].split(",")
            self.__ACCEL_Z_CAL["scale"] = float(params[0])
            self.__ACCEL_Z_CAL["offset"] = float(params[1])

            self.__GYRO_X_OS = float(calib_params[3])
            self.__GYRO_Y_OS = float(calib_params[4])
            self.__GYRO_Z_OS = float(calib_params[5])

        # Generate and store if it doesn't.
        else:
            if(not over_write): print("Specifed calibration file doesn't exist. Begin calibration.")
            elif(file_exists and over_write): print("Recalibrating and overwriting specified calibration file.")
            self.__calibrateMPUManually()

            print("Finished. Writing calibration parameters to file.")
            x_accel_params = f"{self.__ACCEL_X_CAL['scale']},{self.__ACCEL_X_CAL['offset']}\n"
            y_accel_params = f"{self.__ACCEL_Y_CAL['scale']},{self.__ACCEL_Y_CAL['offset']}\n"
            z_accel_params = f"{self.__ACCEL_Z_CAL['scale']},{self.__ACCEL_Z_CAL['offset']}\n"
            x_gyro_os = f"{self.__GYRO_X_OS}\n"
            y_gyro_os = f"{self.__GYRO_Y_OS}\n"
            z_gyro_os = f"{self.__GYRO_Z_OS}\n"

            mpu_config_file = open(mpu_config_file, 'w')
            mpu_config_file.write(x_accel_params)
            mpu_config_file.write(y_accel_params)
            mpu_config_file.write(z_accel_params)
            mpu_config_file.write(x_gyro_os)
            mpu_config_file.write(y_gyro_os)
            mpu_config_file.write(z_gyro_os)

            mpu_config_file.close()
            
        return
    
    def __calibrateMPUManually(self):

        # Prompt list.
        positions = [
            ("+X", "Place sensor with +X axis pointing UP (chip's x-axis up)"),
            ("-X", "Place sensor with -X axis UP (flip 180 on X)"),
            ("+Y", "Place sensor with +Y axis pointing UP"),
            ("-Y", "Place sensor with -Y axis UP"),
            ("+Z", "Place sensor with +Z axis pointing UP (face up)"),
            ("-Z", "Place sensor with -Z axis pointing UP (face down)")
        ]

        # Compute accel parameters.
        raw_measurements = {}
        sample_size  = self.__bufferLength * 10
        for half_axis, prompt in positions:
            print(f"\n{prompt}")
            input("Press Enter when ready.")

            axis = half_axis[1].lower()
            axis_accel_data = 0
            for i in range(sample_size):
                accel_data = self.__mpu.get_accel_data()
                axis_accel_data += accel_data[axis]
                self.delayMillis(100)

            raw_measurements[half_axis] = axis_accel_data/sample_size

        # Set accel calibration parameters.
        max_pos = raw_measurements["+X"]
        max_neg = raw_measurements["-X"]
        self.__ACCEL_X_CAL["scale"] = (max_pos - max_neg) / 2.0
        self.__ACCEL_X_CAL["offset"] = (max_pos + max_neg) / 2.0

        max_pos = raw_measurements["+Y"]
        max_neg = raw_measurements["-Y"]
        self.__ACCEL_Y_CAL["scale"] = (max_pos - max_neg) / 2.0
        self.__ACCEL_Y_CAL["offset"] = (max_pos + max_neg) / 2.0

        max_pos = raw_measurements["+Z"]
        max_neg = raw_measurements["-Z"]
        self.__ACCEL_Z_CAL["scale"] = (max_pos - max_neg) / 2.0
        self.__ACCEL_Z_CAL["offset"] = (max_pos + max_neg) / 2.0

        # Compute and set gyro calibration paramters.
        xGyro = yGyro = zGyro = 0
        for i in range(sample_size):
            gyro_data = self.__mpu.get_gyro_data()
            xGyro += gyro_data['x']
            yGyro += gyro_data['y']
            zGyro += gyro_data['z']

            self.delayMillis(100)

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
        # Grab data.
        accel_data = self.__mpu.get_accel_data()
        gyro_data = self.__mpu.get_gyro_data()

        # Sanitize data w/ calibration parameters.
        xAccel = (accel_data['x'] - self.__ACCEL_X_CAL["offset"]) / self.__ACCEL_X_CAL["scale"]
        yAccel = (accel_data['y'] - self.__ACCEL_Y_CAL["offset"]) / self.__ACCEL_Y_CAL["scale"]
        zAccel = (accel_data['z'] - self.__ACCEL_Z_CAL["offset"]) / self.__ACCEL_Z_CAL["scale"]
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
        data_header = f"x_a_os: {self.__ACCEL_X_CAL},\ny_a_os: {self.__ACCEL_Y_CAL},\nz_a_os: {self.__ACCEL_Z_CAL},\nx_g_os: {self.__GYRO_X_OS},\ny_g_os: {self.__GYRO_Y_OS}, \nz_g_os: {self.__GYRO_Z_OS}\n"
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
    
    def calibrateAccelerometer(self, mpu_config_file=None, over_write=False):
        if(mpu_config_file != None): self.__calibrateMPUFromFile(mpu_config_file, over_write)
        else: self.__calibrateMPUManually()

        return
    
    def showIMUData(self):
        self.__printMPU()
        return