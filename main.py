
from Icarus import Icarus

# Icarus Nanorocks constants.
SOL = 5
LED = 6
MPU = 0x68
VIDEO_NAME = "cmrlab_inr_video"
LOG_NAME = "cmrlab_inr_video"

# Setup.
ofDaedalus = Icarus(SOL, LED, MPU, LOG_NAME, VIDEO_NAME)
ofDaedalus.begin()

# Launch Detection Loop.
print("Entering Launch Detection Loop.")
gState = ofDaedalus.getgravityState()
while (gState != Icarus.HIGH_G):
    ofDaedalus.loop()
    gState = ofDaedalus.getgravityState()
    print(f"Current G state: {gState}")
print("Exiting Launch Detection Loop.")

# Boost Stage Wait Loop.
print("Entering Boost Wait Loop.")
gState = ofDaedalus.getgravityState()
ofDaedalus.getNanoRocks().toggleRecording()
ofDaedalus.getTimer().begin(Icarus.BOOST_MEAS_PERIOD)
clkExpired = ofDaedalus.getTimer().getTimerExpired()
while (clkExpired != True):
    ofDaedalus.loop()
    clkExpired = ofDaedalus.getTimer().getTimerExpired()
    print(f"Current Time: {ofDaedalus.getTimer().getCurrTime()}")
print("Exiting Boost Wait Loop.")

# Main Experiment Loop.
print("Entering Main Experiment Loop.")
ofDaedalus.runExperiment()
while (ofDaedalus.getgravityState() != Icarus.HIGH_G):
    ofDaedalus.runExperiment()
    ofDaedalus.loop()
print("Exiting Main Experiment Loop.")

# Conclusion.
print("Ending Experiment.")
ofDaedalus.end()
print("Experiment Ended. Program Done.")

