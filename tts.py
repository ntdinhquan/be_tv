import edge_tts
import asyncio

async def generate_full(text):
    communicate = edge_tts.Communicate(
        text=text,
        voice="vi-VN-HoaiMyNeural",
        rate="+10%"
    )

    await communicate.save("output.mp3")


def text_to_speech_full(text):
    asyncio.run(generate_full(text))