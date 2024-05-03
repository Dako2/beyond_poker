import asyncio
import websockets
import numpy as np
import sounddevice as sd  # You may need to install this library for audio capture
from io import BytesIO
import base64

# Assuming your Avatar class is defined here

async def audio_stream(websocket):
    # Define a callback function to capture audio chunks
    def callback(indata, frames, time, status):
        if status:
            print(status)
        websocket.send(base64.b64encode(indata).decode())

    # Open a connection to the default audio input device
    with sd.InputStream(callback=callback):
        await asyncio.Future()  # Keep the audio stream running indefinitely

async def inference_with_audio_stream(audio_path, out_vid_name, fps, skip_save_images):
    async with websockets.connect('ws://your_server_address') as websocket:  # Replace 'your_server_address' with the actual server address
        await asyncio.gather(
            audio_stream(websocket),
            avatar.inference(audio_path, out_vid_name, fps, skip_save_images)
        )

# Usage example:
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(inference_with_audio_stream(audio_path="path_to_audio_file", out_vid_name="output_video", fps=25, skip_save_images=False))

