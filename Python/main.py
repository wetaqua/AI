import os
from google import genai
from gtts import gTTS
from pathlib import Path
from openai import OpenAI

history = []  # Seznam pro uchování konverzace

client = genai.Client(api_key="")

response = client.models.generate_content(
    model="gemini-2.0-flash", contents=
'''Budeme hrát hru. V této hře budeme společně vytvářet příběh státl každé ovládané jedním hráčem ty budeš příběh vymýšlet. 
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

První tah: Král Elon Musk vyhlašuje znovu sjednocení federace Česka a Slovenska'''
)

language = 'cs'
myobj = gTTS(text=response.text, lang=language, slow=False)
myobj.save("tts.mp3")
os.system("start tts.mp3")

history.append(response.text)
print(response.text)

while True:
    user_input = input("Zadejte svůj dotaz: ")
    if user_input.lower() in ["exit", "quit"]:
        break
    history.append(f"User: {user_input}")
    response = client.models.generate_content(
        model="gemini-2.0-flash", contents="\n".join(history)
    )
    history.append(f"Gemini: {response.text}")

    language = 'cs'
    myobj = gTTS(text=response.text, lang=language, slow=False)
    myobj.save("tts.mp3")
    os.system("start tts.mp3")
    print(response.text)

   


