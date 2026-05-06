from stt import speech_to_text
from text_utils import split_sentences, merge_short_sentences
from translate import translate_all
from tts import text_to_speech_full
from merge_video import merge_audio_to_video  # file bạn đã viết

import os


def process_video(input_video):
    # 1. STT
    text = speech_to_text(input_video)

    # 2. Split
    sentences = split_sentences(text)
    sentences = merge_short_sentences(sentences)

    # 3. Translate
    translated = translate_all(sentences)

    # 4. TTS
    full_text = " ".join(translated)
    audio_path = "output.mp3"
    text_to_speech_full(full_text)

    # 5. Merge video
    output_video = input_video.replace(".mp4", "_final.mp4")
    merge_audio_to_video(input_video, audio_path, output_video)

    return output_video