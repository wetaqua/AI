import os
from google import genai
from gtts import gTTS
import speech_recognition as sr
import keyboard
import time
import threading

# Inicializace API klienta
client = genai.Client(api_key="AIzaSyA05IRfhz8n3phGQaqgB6_LX2GEL2zw-lY")

# Inicializace rozpoznávání hlasu
recognizer = sr.Recognizer()
listening = False
history = []

# Funkce pro poslech hlasu
def listen():
    global listening
    with sr.Microphone() as mic:
        recognizer.adjust_for_ambient_noise(mic, duration=1)  # Adjust for ambient noise with a longer duration
        print("Poslouchání bylo zahájeno.")

        while listening:
            try:
                audio = recognizer.listen(mic, timeout=10)  # Increase timeout and phrase_time_limit
                text = recognizer.recognize_google(audio, language="cs-CZ").lower()
                print(f"{text}")

                if text:
                    send_to_api(text)  # Pošleme text rovnou do API
                
            except sr.UnknownValueError:
                print("Nerozpoznán žádný vstup.")
            except sr.RequestError:
                print("Chyba připojení k rozpoznávání řeči.")
            except sr.WaitTimeoutError:
                print("Čekání na vstup vypršelo.")
            time.sleep(0.1)

# Funkce pro posílání API požadavku
def send_to_api(user_input):
    history.append(f"User: {user_input}")
    response = client.models.generate_content(
        model="gemini-2.0-flash", contents="\n".join(history)
    )
    history.append(f"Gemini: {response.text}")
    
    # Převod odpovědi na řeč a přehrání
    language = 'cs'
    tts = gTTS(text=response.text, lang=language, slow=False)
    
    print(response.text)

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
            time.sleep(0.1)
        
        time.sleep(0.1)

# Spuštění poslechu klávesnice v samostatném vlákně
threading.Thread(target=keyboard_listener, daemon=True).start()

# První API request – startovací příběh
response = client.models.generate_content(
    model="gemini-2.0-flash", contents=
'''
Budeme hrát hru. V této hře budeme společně vytvářet příběh státl každé ovládané jedním hráčem ty budeš příběh vymýšlet. 
Hráči se střídají v tazích. Začíná hráč jedna.

Pravidla pro tebe: 
1) Nepiš rady hráčům co mají dělat. 
2) Buď víc náhodný
3) Nepřidávej další hráče do hry. 
4) Vytvářej pouze příběh (nepiš popis hry, který kolo je atd.) 
5) Hráčské postavy můžeš zabít (neukončí to hru)
6) Dělej příběh zábavný (můžeš psát věci které nemusejí dívat smysl)
7) Nekonči textem kdo další je na tahu
8) Nekonči text "Mezitím se o situaci doslechl"
9) Odpověď by měla mít aspoň 10 vět
10) Odpověď by měla obsahovat pouze hráče jenž je zrovna na tahu
11) texty "Poslouchání bylo ukončeno." a "Stisknutím klávesy 'm' můžete začít mluvit." nejsou součástí příběhu tudíž je ignoruj

Pravidla hry:
1) Hráči se střídají
2) Každý hráč musí napsat co chce udělat v kole, může použít zdroje
3) Hra končí když jeden z hráčů vlastní 6 států
4) Když stát o armádu přijde automaticky se doplní za dvě kola

Hráči:
Hráč 1: Království Severní Korea (území Slovenska), králem je Elon Musk
Hráč 2: Bagetová říše (Francie), císařem je Bagu Ette
Hráč 3: Ugandské království (Estonko), králem je Notpoleon.
Hráč 4: Skibidi Toilet v Robloxu (Kypr), vůdce je Ježíš (oslovení doutník Ježíš)

Příběh:
Po letech budování se v evropě zrodili tři nové státy. Království Severní Koreji pod vládou krále Elona Muska ovládlo Slovensko. 
Císař Bagu Ette sjednotil francouzský lid a prohlásil Bagetevou Říši. 
Třetí, nejnovější stát, Ugandské králoství pod vládou Notpoleona I ovládá Estonsko. 
Ježíš byl znovu seslán na zemi a osvobodil Kypr od vlády Sovětského svazu a vytvořil diktaturu pod svojí vládou.
Začíná nová éra války nebo míru?

Každý hráč má následující začáteční zdroje (další může získat hraním hry)
1. zdroj: Armáda (10 000 vojáků)
2. zdroj: Princezna

První tah: Král Elon Musk vyhlašuje znovu sjednocení federace Česka a Slovenska
'''
)
history.append(response.text)
print(response.text)

# Převod první odpovědi na řeč
tts = gTTS(text=response.text, lang='cs', slow=False)
#tts.save("response.mp3")
#os.system("start response.mp3")

# Program zůstává aktivní
while True:
    time.sleep(1)
