import re

def split_sentences(text: str):
    raw_sentences = re.split(r'[。]', text)

    result = []

    for sentence in raw_sentences:
        parts = re.split(r'[，,]', sentence)

        buffer = ""

        for part in parts:
            part = part.strip()
            if not part:
                continue

            if len(part) < 6:
                buffer += part
            else:
                if buffer:
                    result.append(buffer + part)
                    buffer = ""
                else:
                    result.append(part)

        if buffer:
            result.append(buffer)

    return result

def merge_short_sentences(sentences):
    result = []
    buffer = ""

    for s in sentences:
        if len(buffer + s) > 30:
            if buffer:
                result.append(buffer)
                buffer = s
            else:
                result.append(s)
        else:
            if len(s) < 10:
                buffer += s
            else:
                if buffer:
                    result.append(buffer + s)
                    buffer = ""
                else:
                    result.append(s)

    if buffer:
        result.append(buffer)
    return result