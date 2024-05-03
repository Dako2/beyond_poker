import os
import json
from datetime import datetime
import azure.cognitiveservices.speech as speechsdk
from playsound import playsound

class TextToSpeech:
    def __init__(self, api_key_env_var='MICROSOFT_TTS_API_KEY', region='westus', output_dir='tts'):
        self.speech_key = os.getenv(api_key_env_var)
        self.service_region = region
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def synthesize_text(self, text, language="en-US"):
        self._set_voice(language)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        audio_filename = f"{self.output_dir}/output_{timestamp}.wav"
        text_filename = f"{self.output_dir}/input_text_{timestamp}.txt"
        json_filename = f"{self.output_dir}/metadata.json"

        audio_config = speechsdk.audio.AudioOutputConfig(filename=audio_filename)
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config, audio_config=audio_config)
        result = speech_synthesizer.speak_text_async(text).get()

        metadata_entry = {
            "timestamp": timestamp,
            "text": text,
            "audio_path": audio_filename,
            "language": language
        }

        self._update_metadata(json_filename, metadata_entry)

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print(f"Speech synthesized and saved to '{audio_filename}'. Metadata updated.")
            playsound(audio_filename)
        elif result.reason == speechsdk.ResultReason.Canceled:
            self._handle_cancellation(result.cancellation_details)

    def _set_voice(self, language):
        voice_map = {
            "en-US": "en-US-AvaMultilingualNeural",
            "zh-HK": "zh-HK-HiuGaaiNeural", #"zh-HK-HiuMaanNeural"
            "yue-CN": "zh-HK-HiuMaanNeural", #"zh-HK-HiuMaanNeural"
            "zh-CN": "en-US-AvaMultilingualNeural", #"zh-HK-HiuMaanNeural"
            "ja-JP": "ja-JP-NanamiNeural",
            "ko-KR": "ko-KR-InJoonNeural",
        }
        voice_name = voice_map.get(language, "en-US-EmmaMultilingualNeural")
        self.speech_config = speechsdk.SpeechConfig(subscription=self.speech_key, region=self.service_region)
        self.speech_config.speech_synthesis_voice_name = voice_name

    def _update_metadata(self, json_filename, metadata_entry):
        try:
            with open(json_filename, "r") as json_file:
                data = json.load(json_file)
        except FileNotFoundError:
            data = []

        data.append(metadata_entry)
        with open(json_filename, "w") as json_file:
            json.dump(data, json_file, indent=4)

    def _handle_cancellation(self, cancellation_details):
        print("Speech synthesis canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))

# Usage example:
if __name__ == "__main__":
    tts = TextToSpeech()
    tts.synthesize_text("你好，欢迎来到Closeby-AI展台.", language="zh-HK")
