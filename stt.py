from faster_whisper import WhisperModel

model = WhisperModel("small")

def speech_to_text(audio_path: str):
    segments, info = model.transcribe(audio_path, language="zh")

    full_text = ""
    for segment in segments:
        full_text += segment.text.strip() + " "

    return full_text.strip()