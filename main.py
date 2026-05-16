from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import yt_dlp
import shutil
import os
import uuid

from typing import Optional
from stt import speech_to_text
from text_utils import split_sentences, merge_short_sentences
from translate import translate_all
from tts import text_to_speech_full
from tts import save_tts_audio
from merge_video import merge_audio_to_video
from fastapi.responses import Response
from fastapi import Requests

app = FastAPI()

# config CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Mount thư mục outputs để frontend có thể tải/xem video kết quả
app.mount("/outputs", StaticFiles(directory=OUTPUT_DIR), name="outputs")
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

@app.get("/")
def read_root():
    return {"message": "MVID API is running!"}


@app.post("/upload-only")
async def upload_only(file: UploadFile = File(...)):
    unique_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename)[1]
    input_path = os.path.join(UPLOAD_DIR, f"manual_{unique_id}{ext}")
    
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    return {
        "message": "success",
        "video_path": input_path
    }

@app.post("/download-url")
async def download_url(request: Requests, url: str = Form(...)):
    try:
        unique_id = str(uuid.uuid4())
        output_filename = f"dl_{unique_id}.mp4"
        output_path = os.path.join(UPLOAD_DIR, output_filename)

        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': output_path,
            'quiet': True,
            'no_warnings': True,
            'merge_output_format': 'mp4' # Ép FFmpeg ghép ra file .mp4
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)
            
        base_url = str(request.base_url).rstrip("/")
        preview_url = f"{base_url}/uploads/{output_filename}"

        return {
            "message": "success",
            "video_path": output_path, # Đường dẫn vật lý cho AI xử lý
            "preview_url": preview_url # Link trực tiếp cho FE hiện hình
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi tải video: {str(e)}")

@app.post("/preview-voice")
async def preview_voice(
    text: str = Form(...),
    voice: str = Form(...),
    rate: int = Form(...)
):
    try:
        temp_preview_path = os.path.join(OUTPUT_DIR, f"preview_{uuid.uuid4()}.mp3")
        rate_str = f"{rate:+d}%"
        
        # Chỉ lấy 1 đoạn ngắn để nghe thử cho nhanh (ví dụ 100 ký tự đầu)
        preview_text = text[:150] 
        
        from tts import save_tts_audio
        await save_tts_audio(preview_text, temp_preview_path, voice, rate_str)
        
        with open(temp_preview_path, "rb") as f:
            audio_data = f.read()
            
        # Xóa file tạm sau khi đọc vào memory
        os.remove(temp_preview_path)
        
        return Response(content=audio_data, media_type="audio/mpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/extract-script")
async def extract_script(file: Optional[UploadFile] = File(None), api_key: str = Form(...), video_path: Optional[str] = Form(None)):
    if not api_key:
        raise HTTPException(status_code=400, detail="Thiếu Gemini API Key")

    # Lưu video
    if file and file.filename:
        unique_id = str(uuid.uuid4())
        ext = os.path.splitext(file.filename)[1]
        input_path = os.path.join(UPLOAD_DIR, f"{unique_id}{ext}")
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    elif video_path and os.path.exists(video_path):
        input_path = video_path # Dùng luôn video có sẵn
    else:
        raise HTTPException(status_code=400, detail="Vui lòng tải lên video hoặc cung cấp link.")

    try:
        # 1. STT -> Split -> Merge
        text = speech_to_text(input_path)
        sentences = split_sentences(text)
        sentences = merge_short_sentences(sentences)

        # 2. Dịch bằng API Key của User
        translated_sentences = translate_all(sentences, api_key)
        vietnamese_script = "\n".join(translated_sentences)

        return {
            "message": "success",
            "video_path": input_path,  # Trả về path để dùng cho bước sau
            "script": vietnamese_script
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-video")
async def generate_video(
    video_path: str = Form(...),
    script: str = Form(...),
    voice: str = Form(...),
    rate: int = Form(...),
    bgm_volume: float = Form(...),
    bgm_start: float = Form(...),
    bgm_end: float = Form(...),
    bgm: UploadFile = File(None)
):
    clean_text = " ".join(script.split()) 
    print(f"DEBUG: Script received and cleaned: '{clean_text}'") 

    if not clean_text:
        raise HTTPException(status_code=400, detail="Script cannot be empty")

    unique_id = str(uuid.uuid4())
    tts_audio_path = os.path.join(OUTPUT_DIR, f"{unique_id}_tts.mp3")
    output_video_path = os.path.join(OUTPUT_DIR, f"{unique_id}_final.mp4")
    bgm_audio_path = None

    try:
        # 2. Định dạng tốc độ chuẩn xác: +10%, -5%, +0%
        # {rate:+d} sẽ tự động thêm dấu + cho số dương và số 0
        rate_str = f"{rate:+d}%"
        print(f"DEBUG: Rate string: '{rate_str}' | Voice: '{voice}'")

        from tts import save_tts_audio
        await save_tts_audio(clean_text, tts_audio_path, voice, rate_str)

        # Kiểm tra file audio sau khi tạo
        if not os.path.exists(tts_audio_path) or os.path.getsize(tts_audio_path) == 0:
            raise Exception("TTS failed: Audio file is empty or not created.")

        if bgm and bgm.filename:
            bgm_audio_path = os.path.join(UPLOAD_DIR, f"{unique_id}_bgm{os.path.splitext(bgm.filename)[1]}")
            with open(bgm_audio_path, "wb") as buffer:
                shutil.copyfileobj(bgm.file, buffer)

        # --- PHẦN MERGE VIDEO ---
        from merge_video import merge_audio_to_video
        merge_audio_to_video(
            input_video=video_path,
            tts_audio=tts_audio_path,
            output_video=output_video_path,
            bgm_audio=bgm_audio_path,
            bgm_volume=bgm_volume, 
            bgm_start=bgm_start, 
            bgm_end=bgm_end
        )
        
        return {
            "message": "success",
            "output_url": f"https://quan2002-mvid-api.hf.space/outputs/{os.path.basename(output_video_path)}"
        }
    except Exception as e:
        print(f"Error during video generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))