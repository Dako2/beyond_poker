import os
from time import sleep
import wave
import requests
import pyaudio
import nltk
from nltk.tokenize import sent_tokenize

import threading

# Event for controlling playback
stop_playback = threading.Event()

def tts_openai_replay(input_text, bypass=False):
    if bypass:
        return

    url = "https://api.openai.com/v1/audio/speech"
    headers = {"Authorization": f'Bearer {os.getenv("OPENAI_API_KEY")}'}
    data = {"model": "tts-1", "input": input_text, "voice": "shimmer", "response_format": "wav"}

    response = requests.post(url, headers=headers, json=data, stream=True)

    if response.ok:
        with wave.open(response.raw, 'rb') as wf:
            p = pyaudio.PyAudio()
            stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                            channels=wf.getnchannels(),
                            rate=wf.getframerate(),
                            output=True)
            # Chunk size to read
            chunk_size = 1024
            # Loop to play audio
            data = wf.readframes(chunk_size)
            while data and not stop_playback.is_set():  # Check if stop condition is set
                stream.write(data)
                data = wf.readframes(chunk_size)
            stream.stop_stream()
            stream.close()
            p.terminate()
    else:
        response.raise_for_status()

def stop_audio():
    # Set the event to stop playback
    stop_playback.set()

def start_tts_async(input_text, bypass=False):
    stop_playback.clear()
    # Create a thread that targets your tts_openai_replay function
    tts_thread = threading.Thread(target=tts_openai_replay, args=(input_text, bypass))
    # Start the thread
    tts_thread.start()

#check if audio folder exists, if not create it
if not os.path.exists("audio"):
    os.makedirs("audio")

def tts_openai_to_wav_files(input_text): #return a list of wav files for inference
    wav_files_for_inference = []

    url = "https://api.openai.com/v1/audio/speech"
    headers = {
        "Authorization": f'Bearer {os.getenv("OPENAI_API_KEY")}',
    }
    # Tokenize input text into sentences
    sentences = sent_tokenize(input_text)
    # Print the segmented sentences
    for i, sentence in enumerate(sentences, 1):
        print(f"Sentence {i}: {sentence}")

        data = {
            "model": "tts-1",
            "input": sentence,
            "voice": "shimmer",
            "response_format": "wav",
        }

        response = requests.post(url, headers=headers, json=data, stream=True)

        if response.ok:
            with wave.open(response.raw, 'rb') as wf:
                CHUNK_SIZE = 1024
                FRAME_RATE = wf.getframerate()
                DURATION = 5  # Duration of each saved segment in seconds

                frames_per_segment = int(FRAME_RATE * DURATION * wf.getsampwidth() * wf.getnchannels())
                
                segment_index = 1
                while True:
                    frames = wf.readframes(frames_per_segment)
                    if not frames:
                        break

                    output_filename = f"audio/Sentence_{i}_segment_{segment_index}.wav"
                    with wave.open(output_filename, 'wb') as segment_wav:
                        segment_wav.setnchannels(wf.getnchannels())
                        segment_wav.setsampwidth(wf.getsampwidth())
                        segment_wav.setframerate(wf.getframerate())
                        segment_wav.writeframes(frames)

                    wav_files_for_inference.append(output_filename)
                    segment_index += 1
        else:
            response.raise_for_status()

    return wav_files_for_inference

if __name__ == '__main__':
    input_text = "I finally had some time to come back to this and found a pretty simple solution. It’s possible to directly pass the response.raw stream into the wave.open call, which automatically deals with parsing the header and buffering chunks. "
    #tts_openai_replay(input_text)
    tts_openai_to_wav_files(input_text)
