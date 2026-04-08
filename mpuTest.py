from Icarus import Icarus

# Icarus Nanorocks constants.
SOL = 5
LED = 6
MPU = 0x68
VIDEO_NAME = "cmrlab_inr_video"
LOG_NAME = "test_log"

ofDaedalus = Icarus(SOL, LED, MPU, LOG_NAME, VIDEO_NAME, testingMpu = True)
ofDaedalus.calibrateAccelerometer()
ofDaedalus.begin()

print("Begin Shaking (w/ Vigor!)")
ofDaedalus.getTimer().begin(60 * 1000)
while (not ofDaedalus.getTimer().getTimerExpired()):
    ofDaedalus.loop()

    #print(f"Avg. Accel. Mag. = {ofDaedalus.getAvgAccelMag():.3f} m/s^2")
    ofDaedalus.showIMUData()

print("Done")