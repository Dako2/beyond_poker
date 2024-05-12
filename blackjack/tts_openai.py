import os
from time import sleep
import wave
import requests
import pyaudio
import nltk
from nltk.tokenize import sent_tokenize
import threading

url = "https://api.openai.com/v1/audio/speech"
headers = {
    "Authorization": f'Bearer {os.getenv("OPENAI_API_KEY")}',
}
#check if audio folder exists, if not create it
if not os.path.exists("audio"):
    os.makedirs("audio")

# Event for controlling playback
stop_playback = threading.Event()

def stop_audio():
    # Set the event to stop playback
    stop_playback.set()

def start_tts_async(input_text, bypass=False):
    stop_playback.clear()
    # Create a thread that targets your tts_openai_replay function
    tts_thread = threading.Thread(target=tts_openai_replay, args=(input_text, bypass))
    # Start the thread
    tts_thread.start()
    
class AudioPlayer:
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.stream = None

    def play_audio(self, filename):
        """ Play an audio file continuously """
        # Open the wave file outside of any conditional blocks to ensure it is available throughout the method
        with wave.open(filename, 'rb') as wf:
            # Only set up the stream if it hasn't been set up already
            if not self.stream:
                self.stream = self.p.open(format=self.p.get_format_from_width(wf.getsampwidth()),
                                          channels=wf.getnchannels(),
                                          rate=wf.getframerate(),
                                          output=True)
            
            # Read and play the audio data
            data = wf.readframes(1024)
            while data and not stop_playback.is_set():
                self.stream.write(data)
                data = wf.readframes(1024)

    def stop_audio(self):
        """ Stop and close the stream """
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
        self.p.terminate()


def tts_openai_replay(input_text, bypass=False): #this is instaneous tts, no need to save to file
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

def tts_openai_to_wav_files(input_text, callback):
    """ Function to convert text to audio files and trigger a callback """
    sentences = sent_tokenize(input_text)
    for i, sentence in enumerate(sentences, 1):
        data = {
            "model": "tts-1",
            "input": sentence,
            "voice": "shimmer",
            "response_format": "wav",
        }
        headers = {"Authorization": f'Bearer {os.getenv("OPENAI_API_KEY")}'}
        response = requests.post("https://api.openai.com/v1/audio/speech", headers=headers, json=data, stream=True)
        if response.ok:
            wav_file_path = f"audio/Sentence_{i}.wav"
            with open(wav_file_path, 'wb') as out_file:
                out_file.write(response.content)
            if callback:
                callback(wav_file_path)  # Trigger the callback to play the audio
        else:
            print(f"Error processing sentence {i}: {response.text}")

def tts_openai_to_wav_files1111(input_text): #return a list of wav files for inference
    wav_files_for_inference = []
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
                DURATION = 7  # Max Duration of each saved segment in seconds
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

def run_tts_in_thread(input_text, callback):
    """ Run TTS conversion in a separate thread to avoid blocking """
    tts_thread = threading.Thread(target=tts_openai_to_wav_files, args=(input_text, callback))
    tts_thread.start()
    return tts_thread

if __name__ == '__main__':
    # Example usage
    p = AudioPlayer()
    input_text = "Hello, this is a test of the text to speech conversion. This is the first sentence. This is the second sentence."
    tts_thread = run_tts_in_thread(input_text, p.play_audio)
    print("Game logic continues to run while audio is being processed...")

