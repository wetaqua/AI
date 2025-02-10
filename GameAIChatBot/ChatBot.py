import os
import google.generativeai as Genai
from google import genai
from google.cloud import texttospeech
import customtkinter
import tkinter as tk
from tkinter import *
from tkinter import scrolledtext
from dotenv import load_dotenv
import json
load_dotenv()

Genai.configure(api_key=os.getenv("GENAI_API_KEY")) #API key in .env file

client = genai.Client(api_key=os.getenv("GENAI_API_KEY"))#API key in .env file

is_asking = False  # Flag to check if Ask function is already running

# Create the model
generation_config = { #Settings for the model
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

safety_settings = [ #Safety settings for the model
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

model = Genai.GenerativeModel( #Creating the model
  model_name="gemini-2.0-flash-lite-preview-02-05",
  generation_config=generation_config,
  safety_settings=safety_settings,
  system_instruction="You are british peasant in 15th century",) #identity of your chatbot - nessesery for the model

chat_session = model.start_chat( #history of the chat
  history=[
  ]
)

def TTS(response_text): #Google Could text to speech
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

def Ask(): #Function for sending request to the model
    global is_asking
    if is_asking:
        return  # If the function is already running, do nothing
    is_asking = True  # Set the flag to indicate the function is running

    user_input = entry.get().strip()  # Get the user input and remove leading/trailing whitespace

    if not user_input:
        is_asking = False  # Reset the flag
        return  # If the input is empty, do nothing

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
            ai_response.insert(END, "Error while geting answer!")
            ai_response.config(state=DISABLED)
            print("Error:", e)
        finally:
            is_asking = False  # Reset the flag after the function completes

import json

def save_history():     # Save chat history to a JSON file
    serializable_history = []
    seen_entries = set()  # Set for unique entries

    for entry in chat_session.history:
        if hasattr(entry, "role") and hasattr(entry, "parts"):
            role = entry.role
            parts = tuple(part.text if hasattr(part, "text") else str(part) for part in entry.parts)
        elif isinstance(entry, dict):
            role = entry.get("role", "unknown")
            parts = tuple(str(part) for part in entry.get("parts", []))
        else:
            continue  # Unsupported entry format

        entry_tuple = (role, parts)
        if entry_tuple not in seen_entries:  # add only unique entries
            seen_entries.add(entry_tuple)
            serializable_history.append({"role": role, "parts": list(parts)})

    with open("chat_history.json", "w", encoding="utf-8") as f:
        json.dump(serializable_history, f, ensure_ascii=False, indent=4)

def load_history(): #load chat history from a JSON file
    if os.path.exists("chat_history.json"):
        with open("chat_history.json", "r", encoding="utf-8") as f:
            loaded_history = json.load(f)
            chat_session.history = [{"role": entry["role"], "parts": entry["parts"]} for entry in loaded_history]

#GUI settings
root = tk.Tk()
 
#getting screen width and height of display
width= root.winfo_screenwidth() 
height= root.winfo_screenheight()
#setting tkinter window size
root.geometry("%dx%d" % (width, height))
root.title("Ai Game Chat Bot")

# Save history when the program exits
root.protocol("WM_DELETE_WINDOW", lambda: [save_history(), root.destroy()])

customtkinter.set_appearance_mode('dark')
customtkinter.set_default_color_theme("dark-blue")

labelframe = LabelFrame(root, text="Answer")
labelframe.pack(fill="both", expand="yes")

# Use a scrolled text widget for the AI response
ai_response = scrolledtext.ScrolledText(labelframe, font=("Arial", 20), wrap=WORD, width=100, height=20)
ai_response.pack(pady=10, padx=10)
ai_response.config(state=DISABLED)

entry = customtkinter.CTkEntry(master=labelframe, font=("Arial", 20), width=800, height=25)
entry.pack(pady=10, padx=10)

button = customtkinter.CTkButton(master=labelframe, text="Sent request", command=Ask)
button.pack(pady=10, padx=10)

button2 = customtkinter.CTkButton(master=labelframe, text="Save", command=save_history)
button2.pack(pady=10, padx=10)

button3 = customtkinter.CTkButton(master=labelframe, text="Load", command=load_history)
button3.pack(pady=10, padx=10)

root.mainloop()