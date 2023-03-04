import sys, time, os, math
from decimal import Decimal
sys.set_int_max_str_digits(10000)

import pyaudio, VolumeData

class VolumeNormalizer:

    def __init__(self, numSamples: int):
        self.maxSamples = numSamples
        self.samples = 0
        self.sum = 0

        self.average = None

    def add(self, volume):
        if self.samples < self.maxSamples:
            self.samples += 1
            self.sum += volume
        
        
        if self.samples == self.maxSamples and self.average is None:
            self.average = math.log(self.sum // self.samples)

    def get(self):
        return self.average
    
    def isReady(self):
        return self.samples == self.maxSamples

# returns the average volume
def calibrateAverageVolume():

    audio = pyaudio.PyAudio()

    stream = audio.open(format=VolumeData.FORMAT, channels=VolumeData.CHANNELS, rate=VolumeData.RATE,
                        input=True, frames_per_buffer=VolumeData.CHUNK)

    norm = VolumeNormalizer(50)

    try:
        while not norm.isReady():

            data = stream.read(VolumeData.CHUNK)
            volume = max(abs(int.from_bytes(data, byteorder='little', signed=True)), VolumeData.THRESHOLD)
            norm.add(volume)

        return norm.get()

    except Exception as e:
        print(e)
        
    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()

def countdown():
    print("3...")
    time.sleep(1)
    print("2...")
    time.sleep(1)
    print("1...")
    time.sleep(1)

def getScientific(largeInt):
    s = str(largeInt)

    return "{}.{}{}E+{}".format(*s[0:3], len(s) - 1)


if __name__ == "__main__":

    if not os.path.exists("Data"):
        os.makedirs("Data")

    print("Calibrating silence in...")
    countdown()
    print("Calibrating silence.")

    silentVolume = calibrateAverageVolume()
    print("Silent volume set to: {} | {}".format(silentVolume, getScientific(silentVolume)))
    with open("Data/SilentVolumeData.txt", 'w') as file:
        file.write(str(silentVolume))
    print("Silent volume level saved to Data/SilentVolumeData.txt")

    print("Calibrating speaking volume in...")
    countdown()
    print("Calibrating speaking volume.")

    speakingVolume = calibrateAverageVolume()
    print("Speaking volume set to: {} | {}".format(speakingVolume, getScientific(speakingVolume)))
    with open("Data/SpeakingVolumeData.txt", 'w') as file:
        file.write(str(speakingVolume))
    print("Speaking volume level saved to Data/SpeakingVolumeData.txt")

    print("Calibration finished.")
