from flask import Flask, request, jsonify, render_template
import requests
import os
app = Flask(__name__)

from pywhispercpp.model import Model, Segment

class WhisperModel():
    audio_file = 'jfk.wav'
    model = Model("tiny")

    def test_transcribe(self):
        segments = self.model.transcribe(self.audio_file)
        print(segments)
        return self.assertIsInstance(segments, list) and \
               self.assertIsInstance(segments[0], Segment) if len(segments) > 0 else True

model = WhisperModel()
model.test_transcribe()


# Replace 'YOUR_OPENAI_API_KEY' with your actual OpenAI API key
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

@app.route('/')
def index():
    return render_template('whisper.html')

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    # Check if the request contains a file
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    audio_file = request.files['file']

    # Check if the file is empty
    if audio_file.filename == '':
        return jsonify({'error': 'No selected file'})

    # Prepare form data for Whisper API request
    form_data = {
        'model': request.form.get('model', 'whisper-1'),  # Default to 'whisper-1' if model not provided
        'response_format': 'text'
    }
    files = {'file': audio_file}

    # Send request to Whisper API
    headers = {'Authorization': f'Bearer {OPENAI_API_KEY}'}
    try:
        response = requests.post('https://api.openai.com/v1/audio/transcriptions', files=files, data=form_data, headers=headers)
        response.raise_for_status()  # Raise exception for any HTTP error
        data = response.json()
        transcription = data.get('transcription', 'Transcription not available')
        return jsonify({'transcription': transcription})
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Request to Whisper API failed: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True)
