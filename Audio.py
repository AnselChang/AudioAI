import pyaudio, math
import wave, sys, SpeakingProcessor, VolumeData
from Logger import *

sys.set_int_max_str_digits(10000)

# Load volume data from files. Return tuple (silentVolume, speakingVolume)
def loadVolumeData():
    with open("Data/SilentVolumeData.txt", "r") as file:
        silentVolume = float(file.readline())
    with open("Data/SpeakingVolumeData.txt", "r") as file:
        speakingVolume = float(file.readline())
    return silentVolume, speakingVolume

# Save audio given as a list of audio frames as a .WAV file. Cannot accept other filename types
def saveAudio(filename, audioFrames: list):
    waveFile = wave.open(filename, 'wb')
    waveFile.setnchannels(VolumeData.CHANNELS)
    waveFile.setsampwidth(audio.get_sample_size(VolumeData.FORMAT))
    waveFile.setframerate(VolumeData.RATE)
    waveFile.writeframes(b''.join(audioFrames))
    waveFile.close()


if __name__ == "__main__":

    log = Logger(DEBUG)

    audio = pyaudio.PyAudio()

    stream = audio.open(format=VolumeData.FORMAT, channels=VolumeData.CHANNELS, rate=VolumeData.RATE,
                        input=True, frames_per_buffer=VolumeData.CHUNK)


    processor = SpeakingProcessor.SpeakingProcesser(log, *loadVolumeData())

    print("Silent volume level:", processor.getSilentRatio())
    print("Speaking volume level: 1\n")
    print("Press any key to start...")
    input()

    while not processor.isDone():

        # Pull current audio data and calculate volume across tick
        audioFrame = stream.read(VolumeData.CHUNK, exception_on_overflow = False)
        volume = max(abs(int.from_bytes(audioFrame, byteorder='little', signed=True)), VolumeData.THRESHOLD)
        volume = math.log(volume)
        
        processor.tick(audioFrame, volume)
        log.log(DEBUG, processor.getCurrentRatio())

    stream.stop_stream()
    stream.close()
    audio.terminate()

    saveAudio("output.wav", processor.getAudio())
    print("Audio saved.")

    