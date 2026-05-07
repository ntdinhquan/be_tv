from google import genai

def translate_all(sentences: list, api_key: str):
    client = genai.Client(api_key=api_key)
    joined_text = "\n".join(sentences)

    prompt = f"""
Translate the following Chinese text into Vietnamese for voice-over.
Rules:
- Keep sentence structure
- Natural spoken Vietnamese
- Each sentence stays on one line
- DO NOT merge lines

Text:
{joined_text}
"""
    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents=prompt,
    )
    result = response.text.strip().split("\n")
    return result