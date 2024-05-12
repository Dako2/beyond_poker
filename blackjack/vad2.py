from flask import Flask, request, jsonify, render_template, send_from_directory
import subprocess

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('whisper.html')

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
    audio_file = request.files['audio']
    audio_file.save("temp_audio.wav")  # Saving to a temporary file

    # Construct the command for the subprocess
    command = [
        './stream',
        '-m', './models/ggml-small.en.bin',
        '-t', '6',
        '--step', '0',
        '--length', '30000',
        '-vth', '0.6',
        'temp_audio.wav'
    ]
    
    result = subprocess.run(command, capture_output=True, text=True)
    
    if result.returncode != 0:
        return jsonify({"error": "Failed to process audio", "message": result.stderr}), 500
    
    return jsonify({"transcription": result.stdout})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)
