from Timer import Timer
from NanoRocks import NanoRocks
from Icarus import Icarus

SOL = 5
LED = 6
MPU = 0x68
VIDEO_NAME = "video"
LOG_NAME = "log"

ofDaedalus = Icarus(SOL, LED, MPU, LOG_NAME, VIDEO_NAME)
ofDaedalus.begin()
nr = ofDaedalus.getNanoRocks()
sw = ofDaedalus.getTimer()

for i in range(5):
    print(f"[{5 - i}] Starting.")
    ofDaedalus.delayMillis(1000)

print("-"*30)
nr.toggleRecording()
active = True
printFlag = False
sw.begin(15000)
while(active):
    if(sw.timeElapsed() >= 15000): active = False 
    else: 
        if(printFlag == False): 
            print("recording in progress...")
            printFlag = True
        ofDaedalus.loop()

nr.toggleRecording()
print("-"*30)
for i in range(5):
    print(f"[{5 - i}] Stopping.")
    ofDaedalus.delayMillis(100)
