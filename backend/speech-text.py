from dotenv import load_dotenv
from datetime import datetime
import os

# Import namaespaces
import azure.cognitiveservices.speech as speech_sdk

def main():
    try:
        global speech_config
        
        #Get Config Settings
        load_dotenv()
        ai_key = os.getenv('AZURE_SPEECH_KEY')
        ai_region = os.getenv('AZURE_SPEECH_REGION')
        print(ai_key,ai_region)
        #Configuring speech service
        speech_config = speech_sdk.SpeechConfig(ai_key, ai_region)
        print('Ready to use speech service in:', speech_config.region)

        #Get spoken input and do what you want to do with this
        command = TranscribeCommand()
        print(command)
        speakOutput(command)
        
    except Exception as ex:
        print(ex)

def TranscribeCommand():
    command =''
    
    #Configure speech recognition
    audio_config = speech_sdk.AudioConfig(use_default_microphone=True)
    speech_recognizer = speech_sdk.SpeechRecognizer(speech_config, audio_config)
    print('Speak now...')
    
    #Process speech input
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

def speakOutput(text):
    speaked_text = 'Did you said: ' + text
    # Configure speech synthesis
    speech_config.speech_synthesis_voice_name = "en-GB-RyanNeural"
    speech_synthesizer = speech_sdk.SpeechSynthesizer(speech_config)
    
    # Synthesize spoken output
    speak = speech_synthesizer.speak_text_async(speaked_text).get()
    if speak.reason != speech_sdk.ResultReason.SynthesizingAudioCompleted:
        print(speak.reason)
        
        
if __name__ == '__main__':
    main()