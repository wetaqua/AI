import whisper

model = whisper.load_model("base")
result = model.transcribe("C:/Users/Uzivatel/Documents/Projekty/DND/video_sound.mp3")

with open("transcription.txt", "w") as f:
    f.write(result["text"])