from speech_utils import SpeechService

def main():
    endcall=True
    while endcall:
        try:
            speechSer = SpeechService()
            

            command = speechSer.transcribe_command()
            print(command)
            """ speechSer.speak_output('My name is pedro') """
            
        except Exception as ex:
            print(ex)
        if command == 'End conversation.':
            endcall=False

if __name__ == '__main__':
    main()