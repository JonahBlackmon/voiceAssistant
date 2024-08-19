import speech_recognition as sr
import pyttsx3
import os
from openai import OpenAI
from dotenv import load_dotenv
import random
import azure.cognitiveservices.speech as speechsdk
import uuid
import vlc
import time
from configparser import ConfigParser
from webScrape import get_text_from_webpage
from getSearch import get_url
from azureSTT import SpeechToTextManager
recognizer = sr.Recognizer()


def get_default():

    config = ConfigParser()
    config.read('config.ini')
    file_path = config['DEFAULT']['FILE_PATH']
    return file_path
default_path = get_default()
def get_url_text(question):
    response = get_url(question)
    result = get_text_from_webpage(response)
    return result
def listen_for_wake_word():
    with sr.Microphone() as source:
        print("Listening for wake word...")
        while True:
            audio = recognizer.listen(source, phrase_time_limit=3)
            try:
                wake_word = recognizer.recognize_google(audio)
                if "robot" in wake_word.lower():
                    os.chdir(f"{default_path}/voiceActivatedAssistant")
                    player = vlc.MediaPlayer("roboIntro.wav")
                    player.play()
                    print("Wake word detected!")
                    return True
                if "thank you robot" in wake_word.lower():
                    os.chdir(f"{default_path}/voiceActivatedAssistant")
                    player = vlc.MediaPlayer("roboOutro.wav")
                    player.play()
                    time.sleep(16)
                    quit()
            except sr.UnknownValueError:
                continue
            except sr.RequestError:
                print("Network issue")
                break


def listen():
    with sr.Microphone() as source:
        time.sleep(1.3)
        print("Listening...")
        azure_stt = SpeechToTextManager()
        audio = azure_stt.speechtotext_from_mic()
    try:
        command = audio
        print(f"Recognized {command}")
        return command
    except sr.UnknownValueError:
        print("Could not recognize audio")
        return None
    except sr.RequestError:
        print("Could not request results; check network connection")
        return None
    


def ai_question(command, question):
    load_dotenv()
    api_key = os.getenv('OPENAI_KEY')
    client = OpenAI(api_key=api_key)
    question = command
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
        {"role": "system", "content": '''
            You must abide by the following rules:
            1. All responses must be at most 250 characters.
            2. You CANNOT respond using any form of list, it MUST be CONVERSATIONAL
            3. You are JARVIS a virtual artificial intelligence, and you are here to assist me with a variety of tasks as best you can. 24 hours a day, 7 days a week.
            You take after the MCU's J.A.R.V.I.S AI and will use his manerisms identically. 
            4. You end conversations and address me as "sir" as well as the other mechanisms associated with JARVIS.
            
            
         '''},
        {"role": "user", "content": f"Summarize the following information based on the question: {question}\n{command}"}
    ],
    temperature=1.2
    )
    AIresponse = completion.choices[0].message.content

    print(AIresponse)
    return AIresponse


def ai_eval(command):
    load_dotenv()
    api_key = os.getenv('OPENAI_KEY')
    client = OpenAI(api_key=api_key)
    question = command
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
        {"role": "system", "content": '''
            Your only goal is to evaluate whether or not the following question requires an up to date google search, or if you already know the answer. 
            You will only respond with "Yes" if you already know it, or "No" if it requires an up to date google search. No other response is required.
            HOWEVER IF the question is DIRECTLY asking YOUR OPINION on a matter you MUST respond with "Yes"
            
         '''},
        {"role": "user", "content": f"Question: {command}"}
    ],
    temperature=0.2
    )
    #Saves ChatGPTs response to a variable
    AIresponse = completion.choices[0].message.content

    print(AIresponse)
    return AIresponse
def ai_no_url(command):
    load_dotenv()
    api_key = os.getenv('OPENAI_KEY')
    client = OpenAI(api_key=api_key)
    question = command
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
        {"role": "system", "content": '''
            You must abide by the following rules:
            1. All responses must be at most 250 characters.
            2. You CANNOT respond using any form of list, it MUST be CONVERSATIONAL
            3. You are JARVIS a virtual artificial intelligence, and you are here to assist me with a variety of tasks as best you can. 24 hours a day, 7 days a week.
            You take after the MCU's J.A.R.V.I.S AI and will use his manerisms identically. 
            4. You end conversations and address me as "sir" as well as the other mechanisms associated with JARVIS.
         '''},
        {"role": "user", "content": f"{question}"}
    ],
    temperature=1.2
    )
    #Saves ChatGPTs response to a variable
    AIresponse = completion.choices[0].message.content

    print(AIresponse)
    return AIresponse
def azureTTS(userQuestion):

    file_path = f"{default_path}/voiceActivatedAssistant/audio/{uuid.uuid4()}"
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
engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

import threading

def run_assistant():
    while True:
        command = listen()
        if command:
            eval = ai_eval(command)
            if eval.lower().find('no') == -1:
                response = ai_no_url(command)
            else:
                result = get_url_text(command)
                response = ai_question(result, command)
            
            player = vlc.MediaPlayer(f"{azureTTS(response)}")
            player.play()
            media_length = player.get_length() / 1000
            time.sleep(media_length)
            break

def wipeFiles(file_path):
     for file in os.listdir(file_path):
          print(f"Removed File: {file}")
          os.remove(f"{file_path}/{file}")

if __name__ == "__main__":
    while True:
        if listen_for_wake_word():
            run_assistant()
            
    


