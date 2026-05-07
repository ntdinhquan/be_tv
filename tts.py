import edge_tts
import asyncio

# Hàm này là hàm gốc, dùng để lưu file
async def save_tts_audio(text: str, output_path: str, voice: str, rate: str):
    communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate)
    await communicate.save(output_path)

# Hàm này chỉ dùng để chạy độc lập (test file)
def text_to_speech_full(text: str, output_path: str, voice: str, rate: str):
    asyncio.run(save_tts_audio(text, output_path, voice, rate))