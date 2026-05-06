from fastapi import FastAPI, UploadFile, File
import shutil
import os

from main import process_video  # bạn sẽ viết hàm này

app = FastAPI()

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    input_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    output_path = process_video(input_path)

    return {
        "message": "done",
        "output": output_path
    }