
if __name__ != "__main__":
    print("main.py inccorrectly being used as non top level.")
    exit()

from Icarus import Icarus

# Icarus Nanorocks constants.
SOL = 5
LED = 6
MPU = 0x68
VIDEO_NAME = "cmrlab_inr_video"
LOG_NAME = "cmrlab_inr_log"
ACCEL_BUFFER_LEN = 3
HIGH_ACCEL_BOUND = 9 # m/s^2

# Setup.
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
ofDaedalus.getTimer().begin(Icarus.BOOST_MEAS_PERIOD)
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

