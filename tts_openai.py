import os
from time import sleep
import wave
import requests
import pyaudio

url = "https://api.openai.com/v1/audio/speech"
headers = {
    "Authorization": f'Bearer {os.getenv("OPENAI_API_KEY")}',
}

data = {
    "model": "tts-1",
    "input": "I finally had some time to come back to this and found a pretty simple solution. It’s possible to directly pass the response.raw stream into the wave.open call, which automatically deals with parsing the header and buffering chunks. ",
    "voice": "shimmer",
    "response_format": "wav",
}

response = requests.post('https://api.openai.com/v1/audio/speech', headers=headers, json=data, stream=True)

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
