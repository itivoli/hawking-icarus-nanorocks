from Timer import Timer
from NanoRocks import NanoRocks
from Icarus import Icarus

SOL = 5
LED = 6
MPU = 0x68
PATH = "video"

log_file = open("log.txt", "w")

i = Icarus(SOL, LED, MPU, PATH)
nr = NanoRocks(SOL, LED, PATH)
sw = Timer()

nr.begin()
nr.toggleRecording()
active = True
while(active):
    if(sw.getCurrTime() == 10000): active = False 
    else:
        log_file.write(f"log {sw.getCurrTime()}\n")
    sw.delayMillis(100)

