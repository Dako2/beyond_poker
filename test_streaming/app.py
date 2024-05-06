import asyncio
import websockets
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

def check_video_availability():
    import os
    return os.path.exists('primary.mp4')  # Check if primary video exists

async def stream_video(websocket, path):
    videoPath = 'dealer.mp4' if check_video_availability() else 'dealer.mp4'
    #command = ['ffmpeg', '-re', '-i', videoPath, '-c:v', 'libx264', '-preset', 'veryfast', '-f', 'mpegts', '-']
    command = ['ffmpeg', '-re', '-i', videoPath, '-c:v', 'libx264', '-preset', 'veryfast', '-f', 'mp4', '-movflags', 'frag_keyframe+empty_moov', '-']

    ffmpeg_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    try:
        while True:
            data = ffmpeg_process.stdout.read(1024)
            if not data:
                break
            await websocket.send(data)
    finally:
        ffmpeg_process.kill()
        try:
            await websocket.close()
        except Exception as e:
            logging.error(f"Error closing WebSocket: {e}")

async def main():
    # Enable asyncio debug mode
    loop = asyncio.get_running_loop()
    loop.set_debug(True)
    async with websockets.serve(stream_video, "localhost", 8765):
        await asyncio.Future()  # Run indefinitely

if __name__ == '__main__':
    asyncio.run(main())
