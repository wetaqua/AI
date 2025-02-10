import os
import google.generativeai as Genai
from google import genai
from google.cloud import texttospeech
import customtkinter
from tkinter import *
from tkinter import scrolledtext
from dotenv import load_dotenv
import json
load_dotenv()

Genai.configure(api_key=os.getenv("GENAI_API_KEY"))

client = genai.Client(api_key=os.getenv("GENAI_API_KEY"))
is_asking = False  # Flag to check if Ask function is already running

# Create the model
generation_config = {
  "temperature": 2,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_NONE",
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
  },
]

model = Genai.GenerativeModel(
  model_name="gemini-2.0-flash-lite-preview-02-05",
  generation_config=generation_config,
  safety_settings=safety_settings,
  system_instruction=
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
9) Odpověď by měla obsahovat pouze hráče jenž je zrovna na tahu
10) text "Hráč" ignoruj
11) odpověď by měla mít minimálně 15 vět

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
2. zdroj: Princezna''',)

chat_session = model.start_chat(
  history=[
  ]
)

def TTS(response_text):
    client = texttospeech.TextToSpeechClient.from_service_account_json("key.json")

    input_text = texttospeech.SynthesisInput(text=response_text)

    voice = texttospeech.VoiceSelectionParams(
        language_code="cs-CZ",
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )

    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

    tts_response = client.synthesize_speech(input=input_text, voice=voice, audio_config=audio_config)

    with open("output.mp3", "wb") as out:
        out.write(tts_response.audio_content)
        print("Audio content written to file 'output.mp3'")

    os.system("start output.mp3")

def Ask():
    global is_asking
    if is_asking:
        return  # If the function is already running, do nothing
    is_asking = True  # Set the flag to indicate the function is running

    user_input = entry.get().strip()  # Získání textu z entry

    if not user_input:
        is_asking = False  # Reset the flag
        return  # Pokud není nic zadáno, nic nedělej

    if user_input.lower() in ["exit", "quit"]:
        root.quit()
    else:
        chat_session.history.append({"role": "user", "parts": [user_input]})

        try:
            response = chat_session.send_message(user_input)

            response_text = response.text.strip()

            model_response = response.text
            chat_session.history.append({"role": "model", "parts": [model_response]})
            print(response_text)

            TTS(response_text)  # Převod odpovědi na hlas

            # Aktualizace GUI odpovědi
            ai_response.config(state=NORMAL)
            ai_response.delete(1.0, END)
            ai_response.insert(END, response_text)
            ai_response.config(state=DISABLED)

        except Exception as e:
            ai_response.config(state=NORMAL)
            ai_response.delete(1.0, END)
            ai_response.insert(END, "Chyba při získávání odpovědi!")
            ai_response.config(state=DISABLED)
            print("Error:", e)
        finally:
            is_asking = False  # Reset the flag after the function completes

import json

def save_history():
    serializable_history = []
    seen_entries = set()  # Množina pro odstranění duplikátů

    for entry in chat_session.history:
        if hasattr(entry, "role") and hasattr(entry, "parts"):
            role = entry.role
            parts = tuple(part.text if hasattr(part, "text") else str(part) for part in entry.parts)
        elif isinstance(entry, dict):
            role = entry.get("role", "unknown")
            parts = tuple(str(part) for part in entry.get("parts", []))
        else:
            continue  # Nepodporovaný formát, přeskočíme ho

        entry_tuple = (role, parts)
        if entry_tuple not in seen_entries:  # Přidáme jen pokud není duplikát
            seen_entries.add(entry_tuple)
            serializable_history.append({"role": role, "parts": list(parts)})

    with open("chat_history.json", "w", encoding="utf-8") as f:
        json.dump(serializable_history, f, ensure_ascii=False, indent=4)

def load_history():
    if os.path.exists("chat_history.json"):
        with open("chat_history.json", "r", encoding="utf-8") as f:
            loaded_history = json.load(f)
            chat_session.history = [{"role": entry["role"], "parts": entry["parts"]} for entry in loaded_history]


root = customtkinter.CTk()
root.geometry("1920x1080")

# Save history when the program exits
root.protocol("WM_DELETE_WINDOW", lambda: [save_history(), root.destroy()])

customtkinter.set_appearance_mode('dark')
customtkinter.set_default_color_theme("dark-blue")

root = customtkinter.CTk()
root.geometry("1080x1920")

labelframe = LabelFrame(root, text="Odpověď")
labelframe.pack(fill="both", expand="yes")

# Use a scrolled text widget for the AI response
ai_response = scrolledtext.ScrolledText(labelframe, font=("Arial", 20), wrap=WORD, width=100, height=20)
ai_response.pack(pady=10, padx=10)
ai_response.config(state=DISABLED)

entry = customtkinter.CTkEntry(master=labelframe, font=("Arial", 20), width=800, height=25)
entry.pack(pady=10, padx=10)

button = customtkinter.CTkButton(master=labelframe, text="Odeslat", command=Ask)
button.pack(pady=10, padx=10)

button2 = customtkinter.CTkButton(master=labelframe, text="Uložit", command=save_history)
button2.pack(pady=10, padx=10)

button3 = customtkinter.CTkButton(master=labelframe, text="Načíst", command=load_history)
button3.pack(pady=10, padx=10)

root.mainloop()