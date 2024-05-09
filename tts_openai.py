import os
from time import sleep
import wave
import requests
import pyaudio
import nltk
from nltk.tokenize import sent_tokenize
import time 
from openai import OpenAI


def tts_openai_replay(input_text, bypass=False):
    if bypass:
        return 0

    url = "https://api.openai.com/v1/audio/speech"
    headers = {
        "Authorization": f'Bearer {os.getenv("OPENAI_API_KEY")}',
    }
    data = {
        "model": "tts-1-hd", # tts-1-hd, tts-1 (for real-time, lower quality and lower latency)
        "input": input_text,
        "voice": "alloy",
        "response_format": "wav",
    }

    response = requests.post(url, headers=headers, json=data, stream=True)

    CHUNK_SIZE = 1024

    if response.ok:
        with wave.open(response.raw, 'rb') as wf:
            p = pyaudio.PyAudio()
            stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                            channels=wf.getnchannels(),
                            rate=wf.getframerate(),
                            output=True)

            while len(data := wf.readframes(CHUNK_SIZE)): 
                stream.write(data)

            # Sleep to make sure playback has finished before closing
            sleep(1)
            stream.close()
            p.terminate()
    else:
        response.raise_for_status()

    return 1

#check if audio folder exists, if not create it
if not os.path.exists("audio"):
    os.makedirs("audio")

def tts_openai_to_wav_files(input_text, segementation_bypass = True): #return a list of wav files for inference
    wav_files_for_inference = []

    url = "https://api.openai.com/v1/audio/speech"
    headers = {
        "Authorization": f'Bearer {os.getenv("OPENAI_API_KEY")}',
    }
    # Tokenize input text into sentences
    if not segementation_bypass:
        sentences = sent_tokenize(input_text)
    else:
        sentences = [input_text]
    # Print the segmented sentences
    for i, sentence in enumerate(sentences, 1):
        print(f"Sentence {i}: {sentence}")

        data = {
            "model": "tts-1",
            "input": sentence,
            "voice": "alloy",#nova
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

                    output_filename = f"audio/Sentence_{i}_segment_{segment_index}_{str(int(time.time()))}.wav"
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

def tts_openai_to_wav_files_simple(input_text, i):
    client = OpenAI()
    speech_file_path = f"audio/{i}.wav"
    
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=input_text
        )

    response.stream_to_file(speech_file_path)

if __name__ == '__main__':
    # input_text = "I finally had some time to come back to this and found a pretty simple solution. It’s possible to directly pass the response.raw stream into the wave.open call, which automatically deals with parsing the header and buffering chunks. "
    # tts_openai_replay(input_text)
    # tts_openai_to_wav_files(input_text)

    # Open the file for reading
    with open('tts_inputs/tts_inputs.txt', 'r') as file:
        i = 0
        for line in file:
            i=i+1
            tts_openai_to_wav_files_simple(line, i)

