from Timer import Timer
from NanoRocks import NanoRocks
from Icarus import Icarus

SOL = 5
LED = 6
MPU = 0x68

PIC_NAME = "test_pic"
VIDEO_NAME = "test_video"
LOG_NAME = "test_log"

PIC_TEST = 1
VID_TEST = 2
testing = PIC_TEST

ofDaedalus = Icarus(SOL, LED, MPU, LOG_NAME, VIDEO_NAME)
ofDaedalus.begin()

nr = ofDaedalus.getNanoRocks()
sw = ofDaedalus.getTimer()

if(testing == PIC_TEST):
    fileName = PIC_NAME
    print("Taking test picture")
    nr.takePicture(f"{fileName}.jpg")
    print(f"Picture taken and stored @: \"{fileName}.jpg\" ")
    
elif(testing == VID_TEST):
    countdown = 3
    for i in range(countdown):
        print(f"[{countdown - i}] Starting Video Recording Test.")
        ofDaedalus.delayMillis(1000)

        print("-"*30)
        nr.toggleRecording()
        recordingDuration = 5000
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