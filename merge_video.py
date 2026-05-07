import subprocess
import os

def merge_audio_to_video(input_video, tts_audio, output_video, bgm_audio=None, bgm_volume=0.3, bgm_start=0, bgm_end=10):
    if not os.path.exists(input_video):
        raise FileNotFoundError(f"Video not found: {input_video}")
    if not os.path.exists(tts_audio):
        raise FileNotFoundError(f"TTS Audio not found: {tts_audio}")

    if bgm_audio and os.path.exists(bgm_audio):
        # Lệnh FFmpeg mix TTS và Nhạc nền (giảm âm lượng BGM)
        cmd = [
            "ffmpeg", "-y",
            "-i", input_video,
            "-i", tts_audio,
            "-ss", str(bgm_start),    # Thời điểm bắt đầu cắt nhạc
            "-to", str(bgm_end),      # Thời điểm kết thúc cắt nhạc
            "-i", bgm_audio,
            "-filter_complex", 
            f"[1:a]volume=1.0[a1];[2:a]volume={bgm_volume}[a2];[a1][a2]amix=inputs=2:duration=first[a]",
            "-map", "0:v:0",
            "-map", "[a]",
            "-c:v", "copy",
            "-c:a", "aac",
            "-shortest",
            output_video
        ]
    else:
        # Lệnh gốc: Chỉ có TTS
        cmd = [
            "ffmpeg", "-y",
            "-i", input_video,
            "-i", tts_audio,
            "-c:v", "copy",
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-shortest",
            output_video
        ]

    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True)
    print(f"\n✅ Done → {output_video}")