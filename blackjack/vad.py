import sounddevice as sd
import numpy as np
import webrtcvad
import wave
import io
import time as tm
import threading

from pywhispercpp.model import Model, Segment

class WhisperModel():
    model = Model("tiny")
    
    def transcribe(self, audio_file):
        segments = self.model.transcribe(audio_file)
        print(segments)
        
whisper = WhisperModel()

# Initialize VAD and Whisper model
vad = webrtcvad.Vad(1)  # Aggressiveness mode set to 1
sample_rate = 16000  # Supported sample rate for VAD
frame_duration = 30  # Duration of a frame in ms
frame_size = int(sample_rate * frame_duration / 1000)  # Size of a frame in samples

def save_and_transcribe(buffer):
    timestamp = tm.strftime("%Y%m%d-%H%M%S")
    filename = f"speech_segments_{timestamp}.wav"
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # PCM 16-bit
        wf.setframerate(sample_rate)
        wf.writeframes(buffer.getvalue())
    print(f"File saved: {filename}")
    
    # Transcription
    result = whisper.transcribe(filename)
    print(f"Transcription for {filename}: {result}")

# Callback function to process microphone input
def callback(indata, frames, time_info, status):
    global last_speech_time, audio_buffer
    if status:
        print(status)
    if frames == frame_size:
        is_speech = vad.is_speech(indata.tobytes(), sample_rate)
        if is_speech:
            audio_buffer.write(indata.tobytes())
            last_speech_time = tm.time()

# Main recording loop
while True:
    last_speech_time = tm.time()
    audio_buffer = io.BytesIO()
    with sd.InputStream(samplerate=sample_rate, channels=1, dtype='int16', callback=callback, blocksize=frame_size):
        print("Recording started...")
        while True:
            tm.sleep(0.1)
            if (tm.time() - last_speech_time > 2):  # 2 seconds of silence triggers saving
                print("Stopping recording due to silence...")
                break
    # Start a new thread for saving and transcribing
    thread = threading.Thread(target=save_and_transcribe, args=(audio_buffer,))
    thread.start()
