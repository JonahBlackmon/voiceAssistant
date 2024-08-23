from .getDefault import get_default
import uuid
import azure.cognitiveservices.speech as speechsdk

default_path = get_default()
def azureTTS(userQuestion):

    file_path = f"{default_path}/voiceActivatedAssistant/audio/{uuid.uuid4()}.wav"
    question = userQuestion
    styles = ['angry', 'cheerful', 'excited', 'friendly', 'hopeful', 'sad', 'shouting', 'terrified', 'unfriendly', 'whispering']

    #os.chdir('C:/Users/Jonah/Downloads/Projects/AIChatbot/audioOutput')
    # Creates an instance of a speech config with specified subscription key and service region.
    speech_key, service_region = "068c54f2cd5b4c4b97be1c327ed8037f", "eastus"
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)


    voice = 'en-GB-RyanNeural'
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)

    ssml_string = f"""
    <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-US'>
            <voice name='{voice}'>
                <prosody rate='0%' pitch='0%'>
                    <s> {question} </s>
                </prosody>
            </voice>
        </speak>
        """
    result = speech_synthesizer.speak_ssml_async(ssml_string).get()

    stream = speechsdk.AudioDataStream(result)
    stream.save_to_wav_file(file_path)
    return file_path
