
if __name__ != "__main__":
    print("main.py inccorrectly being used as non top level.")
    exit(1)

shortVidDurTest = True
shortVidDur = 5 * 1000

# Set project working directory.
import os
PROJ_DIR = "/home/cmrlab/Documents/Github/hawking"
os.chdir(PROJ_DIR) 

# Icarus Nanorocks constants.
SOL = 17
LED = 6
MPU = 0x68
VIDEO_NAME = "cmrlab_inr_video"
LOG_NAME = "cmrlab_inr_log"
ACCEL_BUFFER_LEN = 3
HIGH_ACCEL_BOUND = 9 # m/s^2

# Check for Experiment completion.
cron_log = None
if(os.path.isfile(VIDEO_NAME + ".mp4")): 
    cron_log = open("cron_log.txt", 'w')
    cron_log.write(os.path.abspath(VIDEO_NAME + ".mp4"))
    cron_log.write("\n")
    cron_log.write("cmrlab_inr_video file already exists, experiment has run already.")
    cron_log.close()
    exit(2)
else:
    cron_log = open("cron_log.txt", 'w')
    cron_log.write(os.path.abspath(VIDEO_NAME + ".mp4"))
    cron_log.write("\n")
    cron_log.write("cmrlab_inr_video file doesn't exist, running experiment now.")
    cron_log.close()

# Setup.
from Icarus import Icarus
ofDaedalus = Icarus(
    SOL, 
    LED, 
    MPU, 
    LOG_NAME, 
    VIDEO_NAME, 
    ACCEL_BUFFER_LEN, 
    HIGH_ACCEL_BOUND
    )
ofDaedalus.begin()

# Launch Detection Loop.
print("\n\n\nEntering Launch Detection Loop.")
gState = ofDaedalus.getgravityState()
while (gState != Icarus.HIGH_G):
    ofDaedalus.loop()
    gState = ofDaedalus.getgravityState()
    print(f"Current G state: {gState} [a = {ofDaedalus.getAvgAccelMag():.3f} m\s^2]")
print("Exiting Launch Detection Loop.")

# Boost Stage Wait Loop.
print(f"Entering Boost Wait Loop @ {ofDaedalus.getTimer().getCurrTime()} ms.")
gState = ofDaedalus.getgravityState()
ofDaedalus.getNanoRocks().toggleRecording()
if(shortVidDurTest): ofDaedalus.getTimer().begin(shortVidDur)
else: ofDaedalus.getTimer().begin(Icarus.BOOST_MEAS_PERIOD)
clkExpired = ofDaedalus.getTimer().getTimerExpired()
while (clkExpired != True):
    ofDaedalus.loop()
    clkExpired = ofDaedalus.getTimer().getTimerExpired()
    print(f"Current Time: {ofDaedalus.getTimer().getCurrTime()}")
print(f"Exiting Boost Wait Loop @ {ofDaedalus.getTimer().getCurrTime()} ms.")

# Main Experiment Loop.
print("Entering Main Experiment Loop.")
ofDaedalus.runExperiment()
gState = ofDaedalus.getgravityState()
while (gState != Icarus.HIGH_G):
    ofDaedalus.runExperiment()
    ofDaedalus.loop()
    gState = ofDaedalus.getgravityState()
print("Exiting Main Experiment Loop.")

# Conclusion.
print("Ending Experiment.")
ofDaedalus.end()
print("Experiment Ended. Program Done.")

