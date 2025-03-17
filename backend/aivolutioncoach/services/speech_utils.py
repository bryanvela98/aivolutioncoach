from dotenv import load_dotenv
import os
import azure.cognitiveservices.speech as speech_sdk

class SpeechService:
    def __init__(self):
        load_dotenv()
        ai_key = os.getenv('AZURE_SPEECH_KEY')
        ai_region = os.getenv('AZURE_SPEECH_REGION')
        self.speech_config = speech_sdk.SpeechConfig(ai_key, ai_region)
        #print('Ready to use speech service in:', self.speech_config.region)
 
    def transcribe_command(self):
        command = ''
        # Configure speech recognition
        audio_config = speech_sdk.AudioConfig(use_default_microphone=True)
        speech_recognizer = speech_sdk.SpeechRecognizer(self.speech_config, audio_config)
        #print('Speak now...')
        
        # Process speech input
        speech = speech_recognizer.recognize_once_async().get()
        if speech.reason == speech_sdk.ResultReason.RecognizedSpeech:
            command = speech.text
            print(command)
        else:
            print(speech.reason)
            if speech.reason == speech_sdk.ResultReason.Canceled:
                cancellation = speech.cancellation_details
                print(cancellation.reason)
                print(cancellation.error_details)
        return command

    def speak_output(self, text):
        speaked_text = text
        # Configure speech synthesis
        self.speech_config.speech_synthesis_voice_name = "en-GB-RyanNeural"
        speech_synthesizer = speech_sdk.SpeechSynthesizer(self.speech_config)
        
        # Synthesize spoken output
        speak = speech_synthesizer.speak_text_async(speaked_text).get()
        if speak.reason != speech_sdk.ResultReason.SynthesizingAudioCompleted:
            print(speak.reason)