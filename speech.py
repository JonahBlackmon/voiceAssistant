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

WAKE_WORD="Jarvis"
def listen_for_wake_word():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    with microphone as source:
        print("Adjusting for ambient noise...") 
        recognizer.adjust_for_ambient_noise(source)
        print(f"Listening for wake word: '{WAKE_WORD}'")
        while True:
            audio = recognizer.listen(source)
            try:
                # Recognize the speech using Google's speech recognition
                command = recognizer.recognize_google(audio).lower()
                # Check if the wake word is in the recognized command
                if WAKE_WORD.lower() in command:
                    
                    print("Wake word detected!")
                    return True
            except sr.UnknownValueError:
                # If speech is unintelligible
                print("Could not understand the audio")
            except sr.RequestError:
                # If there's an error with the recognizer
                print("Could not request results; check your network connection")


def listen():
    print("Listening...")
    azure_stt = SpeechToTextManager()
    audio = azure_stt.speechtotext_from_mic()
    command = audio
    print(f"Recognized {command}")
    return command

    
def play_intro():
    player = vlc.MediaPlayer(f'{default_path}/voiceActivatedAssistant/roboIntro.wav')
    player.play()
    time.sleep(3)
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
            time.sleep(1)
            player.play()
            
            break

def wipeFiles(file_path):
     for file in os.listdir(file_path):
          print(f"Removed File: {file}")
          os.remove(f"{file_path}/{file}")

if __name__ == "__main__":
    while True:
        if listen_for_wake_word():
            play_intro()
            run_assistant()
            
    


