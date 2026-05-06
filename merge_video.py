import subprocess
import os

def merge_audio_to_video(input_video, input_audio, output_video="final.mp4"):
    if not os.path.exists(input_video):
        raise FileNotFoundError(f"Video not found: {input_video}")

    if not os.path.exists(input_audio):
        raise FileNotFoundError(f"Audio not found: {input_audio}")

    cmd = [
        "ffmpeg",
        "-y",                     # overwrite
        "-i", input_video,        # video gốc
        "-i", input_audio,        # audio tiếng Việt
        "-c:v", "copy",           # giữ nguyên video (nhanh)
        "-map", "0:v:0",          # lấy video từ input 0
        "-map", "1:a:0",          # lấy audio từ input 1
        "-shortest",              # cắt theo track ngắn hơn
        output_video
    ]

    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True)

    print(f"\n✅ Done → {output_video}")


if __name__ == "__main__":
    merge_audio_to_video(
        input_video=r"D:\projects\ads\nâng sên xe máy\j2download_hd_no_watermark.mp4",   # sửa path của bạn
        input_audio="output.mp3",           # file TTS bạn đã tạo
        output_video="final.mp4"
    )