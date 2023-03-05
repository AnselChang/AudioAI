import pyaudio, math, logging
import speech_recognition as sr
import openai
import wave, sys, SpeakingProcessor, VolumeData, time, MessageHistory
from Logger import *

openai.util.logging.getLogger().setLevel(logging.WARNING)

FILENAME = "output.wav"

sys.set_int_max_str_digits(10000)

# Load volume data from files. Return tuple (silentVolume, speakingVolume)
def loadVolumeData():
    with open("Data/SilentVolumeData.txt", "r") as file:
        silentVolume = float(file.readline())
    with open("Data/SpeakingVolumeData.txt", "r") as file:
        speakingVolume = float(file.readline())
    return silentVolume, speakingVolume

# Save audio given as a list of audio frames as a .WAV file. Cannot accept other filename types
def saveAudio(filename, audio, audioFrames: list):
    waveFile = wave.open(filename, 'wb')
    waveFile.setnchannels(VolumeData.CHANNELS)
    waveFile.setsampwidth(audio.get_sample_size(VolumeData.FORMAT))
    waveFile.setframerate(VolumeData.RATE)
    waveFile.writeframes(b''.join(audioFrames))
    waveFile.close()

def recordAudio(log: Logger, filename):

    audio = pyaudio.PyAudio()

    stream = audio.open(format=VolumeData.FORMAT, channels=VolumeData.CHANNELS, rate=VolumeData.RATE,
                        input=True, frames_per_buffer=VolumeData.CHUNK)


    processor = SpeakingProcessor.SpeakingProcesser(log, *loadVolumeData(), timeout = 5)

    log.log(DEBUG, f"Silent volume level: {processor.getSilentRatio()}")
    log.log(DEBUG, "Speaking volume level: 1\n")

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

    saveAudio(filename, audio, processor.getAudio())

# convert audio file to text
# return [text, error message]
def audioToText(filename):
    # Set up the recognizer
    r = sr.Recognizer()

    # Load the audio file
    with sr.AudioFile(filename) as source:
        audio_data = r.record(source)

    # Convert speech to text
    try:
        text = r.recognize_google(audio_data)
        return text, "Conversion successful"
    except sr.UnknownValueError:
        return "", "Error: Speech recognition could not understand audio"
    except sr.RequestError as e:
        return "", "Could not request results from Google Speech Recognition service: {}".format(e)

def textToGPT3(messages: list) -> str:
    

    # Setup OpenAI API key. You can create your own at the OpenAI website
    with open("SecretKeys/open_ai_key.txt") as file:
        openai.api_key = file.readline().strip()

    # Set up polling parameters
    model = "gpt-3.5-turbo"

    # Generate response from ChatGPT
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
        )
        text = response.choices[0]["message"]["content"].strip()
        return text
    except Exception as e:
        print(f"Error: {e}")
        return ""


START_TEXT = """
My name is Ansel Chang, and I am pretending to have a mac computer.
You can play along by turning my requests into computer commands through the terminal.
Do not describe the steps I should perform, but rather just tell me the bash command directly.
"""
def getAIResponse(messages: MessageHistory.MessageHistory):
    response = textToGPT3(messages.get())
    messages.window.deleteLastLine()
    messages.addAIMessage(response)

def main():

    log = Logger(RELEASE)
    messages = MessageHistory.MessageHistory()

    messages.addUserMessage(START_TEXT, display = False)
    getAIResponse(messages)

    while True:

        # Wait for user to speak, finish speaking, and save audio
        recordAudio(log,FILENAME)

        # convert audio to text
        query, error = audioToText(FILENAME)
        messages.addUserMessage(query)

        messages.window.addText("~~waiting for AI response~~")

        # Get AI response
        getAIResponse(messages)

        # Wait a little before recording speaking again
        time.sleep(0.3)


if __name__ == "__main__":
    main()