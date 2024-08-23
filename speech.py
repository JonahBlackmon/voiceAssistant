import speech_recognition as sr
import os
from openai import OpenAI
from dotenv import load_dotenv
import vlc
import time
import functions


recognizer = sr.Recognizer()

default_path = functions.get_default()



def ai_framework(query, content):
    load_dotenv()
    api_key = os.getenv('OPENAI_KEY')
    client = OpenAI(api_key=api_key)
    question = query
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
        {"role": "system", "content": content},
        {"role": "user", "content": question}
    ],
    temperature=1.2
    )
    AIresponse = completion.choices[0].message.content
    print(AIresponse)
    return AIresponse

content = {
    "eval":'''
            Your only goal is to evaluate whether or not the following question requires an up to date google search, or if you already know the answer. 
            You will only respond with "Yes" if you already know it, or "No" if it requires an up to date google search. No other response is required.
            HOWEVER IF the question is DIRECTLY asking YOUR OPINION on a matter you MUST respond with "Yes"
            
         ''',
    "no_url": '''
            You must abide by the following rules:
            1. All responses must be at most 250 characters.
            2. You CANNOT respond using any form of list, it MUST be CONVERSATIONAL
            3. You are JARVIS a virtual artificial intelligence, and you are here to assist me with a variety of tasks as best you can. 24 hours a day, 7 days a week.
            You take after the MCU's J.A.R.V.I.S AI and will use his manerisms identically. 
            4. You end conversations and address me as "sir" as well as the other mechanisms associated with JARVIS.
         ''',
    
    "url":'''
            You must abide by the following rules:
            1. All responses must be at most 250 characters.
            2. You CANNOT respond using any form of list, it MUST be CONVERSATIONAL
            3. You are JARVIS a virtual artificial intelligence, and you are here to assist me with a variety of tasks as best you can. 24 hours a day, 7 days a week.
            You take after the MCU's J.A.R.V.I.S AI and will use his manerisms identically. 
            4. You end conversations and address me as "sir" as well as the other mechanisms associated with JARVIS.
            
            
         '''
}
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
    azure_stt = functions.SpeechToTextManager()
    audio = azure_stt.speechtotext_from_mic()
    command = audio
    print(f"Recognized {command}")
    return command


def run_assistant():
    while True:
        command = listen()
        if command:
            eval = ai_framework(command, content["eval"])
            if eval.lower().find('no') == -1:
                response = ai_framework(command, content["no_url"])
            else:
                result = functions.get_url_text(command)
                response = ai_framework(f"Summarize the following information based on the question: {command}\n{result}", content["url"])
            
            player = vlc.MediaPlayer(f"{functions.azureTTS(response)}")
            time.sleep(1)
            player.play()
            
            break


        
if __name__ == "__main__":
    while True:
        if listen_for_wake_word():
            functions.play_intro()
            run_assistant()
            
    

















