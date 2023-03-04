from enum import Enum
from Logger import Logger, DEBUG, RELEASE

class State(Enum):
    BEFORE_SPEAK = 1,
    DURING_SPEAK = 2
    AFTER_SPEAK = 3

# Determine whether user is speaking or not.
class SpeakingProcesser:

    def __init__(self, log: Logger, silentVolume: float, speakingVolume: float):
        self.log = log
        self.SILENT_VOLUME = silentVolume
        self.SPEAKING_VOLUME = speakingVolume

        self.frames = []

        self.state: State = State.BEFORE_SPEAK

        self.MIN_SPEAKING_FRAMES_NEEDED_TO_START = 10
        self.MIN_SILENCE_FRAMES_NEEDED_TO_END = 10

        self._currentNumSilentFrames = 0

    # Clear recording and reset internal state
    def reset(self):
        self.frames = []
        self.state = State.BEFORE_SPEAK

    def isDone(self):
        return self.state == State.AFTER_SPEAK and len(self.frames) > 0

    # Recieve more volume data.
    # audioFrame is the actual audio data this tick. We want to store a list of the relevant data
    # volume is scaled from 0 (true silence), 1 (recorded silence), and above
    # return True if finished recording
    def tick(self, audioFrame, volume):

        self.currentVolume = volume

        if self.state == State.BEFORE_SPEAK:

            # We keep recording data as soon as we hear something
            if volume > self.SILENT_VOLUME:
                self.frames.append(audioFrame)
            else:
                self.frames.clear()

            self.log.log(DEBUG, "BEFORE: {}".format(len(self.frames)))

            # We've been speaking for long enough to confirm it's not just a momentary disturbance.
            # We officially transition into continuing recording until silence is reached again
            if len(self.frames) >= self.MIN_SPEAKING_FRAMES_NEEDED_TO_START:
                self.state = State.DURING_SPEAK
                self.log.log(DEBUG, "DURING_SPEAK")

        elif self.state == State.DURING_SPEAK:

            self.frames.append(audioFrame)

            # We keep track of how many silent audio frames happened in a row
            if volume > self.SILENT_VOLUME:
                self._currentNumSilentFrames = 0
            else:
                self._currentNumSilentFrames += 1

            # We've officially reached the end of the recording
            if self._currentNumSilentFrames >= self.MIN_SILENCE_FRAMES_NEEDED_TO_END:
                
                # at this point, no recording will happen even if you call tick(), unless you call reset()
                self.state = State.AFTER_SPEAK
                self.log.log(DEBUG, "AFTER_SPEAK")
                return True # finished recording

        else: # self.state == State.AFTER_SPEAK
            pass # nothing to do for now

        return False # has not finished recording

    def getSilentRatio(self):
        return self.SILENT_VOLUME / self.SPEAKING_VOLUME
    
    def getCurrentRatio(self):
        return self.currentVolume / self.SPEAKING_VOLUME

    # get the audio stream.
    def getAudio(self):
        return self.frames