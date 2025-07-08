import time as time

class Timer:
    __currTime = 0
    __startTime = 0
    __duration = 0
    __timerOn = False
    __timerExpired = False

    def __tick(self, interval): self.__currTime += interval

    def begin(self, duration, reset = False): 
        # Reset if needed.
        if (reset):
            self.__startTime = 0
            self.__currTime = 0
        else: 
            self.__startTime = self.__currTime 

        self.__duration = duration
        self.__timerOn = True
        return
    
    def timeElapsed(self): 
        tElapsed = self.__currTime - self.__startTime
        return tElapsed
    
    def delayMillis(self, delay):
        self.__tick(delay)
        if(self.__timerOn and self.timeElapsed() > self.__duration):
            self.__timerExpired = True
            self.__timerOn = False

        time.sleep(delay/1000)
        return
        
    def getCurrTime(self): 
        return self.__currTime
    
    def getStartTime(self):
        return self.__startTime

    def getTimerExpired(self):
        return self.__timerExpired