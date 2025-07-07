

#"""
from Timer import Timer
from NanoRocks import NanoRocks
from Icarus import Icarus

SOL = 5
LED = 6
MPU = 0x68
VIDEO_NAME = "cmrlab_inr_video"
LOG_NAME = "cmrlab_inr_log"

ofDaedalus = Icarus(SOL, LED, MPU, LOG_NAME, VIDEO_NAME)
ofDaedalus.begin()
nr = ofDaedalus.getNanoRocks()
sw = ofDaedalus.getTimer()

countdown = 3
for i in range(countdown):
    print(f"[{countdown - i}] Starting.")
    ofDaedalus.delayMillis(1000)

print("-"*30)
nr.toggleRecording()
recordingDuration = 15000
sw.begin(recordingDuration, True)

active = True
printFlag = False
while(active):
    if(sw.timeElapsed() >= recordingDuration): active = False 
    else: 
        if(printFlag == False): 
            print(f"recording in progress...: [{sw.timeElapsed()}]")
            #printFlag = True
        ofDaedalus.loop()

nr.toggleRecording()
print("-"*30)
for i in range(countdown):
    print(f"[{countdown - i}] Stopping.")
    ofDaedalus.delayMillis(100)
#"""


