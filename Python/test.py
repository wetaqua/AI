import os
from gtts import gTTS
import speech_recognition as sr
import keyboard
import time
import threading

# Inicializace rozpoznávání hlasu
recognizer = sr.Recognizer()
listening = False
history = []

# Funkce pro poslech hlasu
def listen():
    global listening
    with sr.Microphone() as mic:
        recognizer.adjust_for_ambient_noise(mic)
        print("Poslouchání bylo zahájeno.")

        while listening:
            try:
                recognizer.energy_threshold = 4000
                recognizer.pause_threshold = 1.5
                audio = recognizer.listen(mic, timeout=None, phrase_time_limit=None)
                text = recognizer.recognize_google(audio, language="cs-CZ, eng-ENG", ).lower()
                print(f"Rozpoznáno: {text}")

                if text:
                    history.append(f"User: {text}")
            except sr.UnknownValueError:
                print("Nerozpoznán žádný vstup.")
            except sr.RequestError:
                print("Chyba připojení k rozpoznávání řeči.")
            time.sleep(0.1)

# Funkce pro poslech klávesnice
def keyboard_listener():
    global listening
    while True:
        if keyboard.is_pressed("m") and not listening:
            listening = True
            threading.Thread(target=listen, daemon=True).start()
            time.sleep(0.3)  # Zabraňuje vícenásobnému spuštění
        
        if keyboard.is_pressed("n") and listening:
            print("Poslouchání bylo ukončeno.")
            listening = False
            time.sleep(0.3)
        
        time.sleep(0.1)

# Spuštění poslechu klávesnice v samostatném vlákně
threading.Thread(target=keyboard_listener, daemon=True).start()

# Program zůstává aktivní
while True:
    time.sleep(1)
