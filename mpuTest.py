from Icarus import Icarus

# Icarus Nanorocks constants.
SOL = 5
LED = 6
MPU = 0x68
VIDEO_NAME = "cmrlab_inr_video"
LOG_NAME = "test_log"

ofDaedalus = Icarus(SOL, LED, MPU, LOG_NAME, VIDEO_NAME)
ofDaedalus.getTimer().begin(15 * 1000)
ofDaedalus.begin()

print("Begin Shaking (w/ Vigor!)")
while (not ofDaedalus.getTimer().getTimerExpired()):
    ofDaedalus.loop()
    ofDaedalus.delayMillis()

print("Done")