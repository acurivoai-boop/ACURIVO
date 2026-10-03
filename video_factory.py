
import os
import subprocess
from pathlib import Path
import urllib.parse
import urllib.request

OUT = Path("output")
OUT.mkdir(exist_ok=True)

SCRIPT = """
تخيل أن تمتلك شركة تعمل طوال اليوم والليل،
وتستطيع أن تنتج المحتوى وتخدم العملاء وتدير العمليات،
بينما يكون الذكاء الاصطناعي هو المحرك الذي ينفذ المهام المتكررة.

المستقبل لا يعتمد فقط على عدد الموظفين،
بل على قوة الأنظمة التي تعمل خلف الشركة.

وهنا تبدأ فكرة ACURIVO:
منظومة رقمية تجعل الذكاء الاصطناعي ينفذ سلسلة متكاملة من المهام،
بينما يبقى الإنسان صاحب القرار والمراقب النهائي.

هذه ليست شركة بلا إنسان،
بل شركة يستطيع فيها إنسان واحد إدارة منظومة رقمية واسعة.

وهذا هو مستقبل الأعمال.
"""

def run(cmd):
    print("RUN:", " ".join(cmd))
    subprocess.run(cmd, check=True)

def make_voice():
    text_file = OUT / "script.txt"
    audio_file = OUT / "voice.mp3"

    text_file.write_text(SCRIPT, encoding="utf-8")

    run([
        "python",
        "-m",
        "edge_tts",
        "--voice",
        "ar-SA-HamedNeural",
        "--rate=+5%",
        "--text",
        SCRIPT,
        "--write-media",
        str(audio_file)
    ])

    return audio_file

def make_background():
    image = OUT / "background.jpg"

    url = (
        "https://picsum.photos/1920/1080"
        "?random=acurivo"
    )

    urllib.request.urlretrieve(url, image)

    return image

def make_video(image, audio):
    video = OUT / "ACURIVO_VIDEO.mp4"

    run([
        "ffmpeg",
        "-y",
        "-loop",
        "1",
        "-i",
        str(image),
        "-i",
        str(audio),
        "-vf",
        "scale=1920:1080,"
        "zoompan=z='min(zoom+0.0005,1.08)':"
        "d=1:s=1920x1080:fps=30",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-shortest",
        str(video)
    ])

    return video

def main():
    print("================================")
    print("ACURIVO VIDEO FACTORY")
    print("================================")

    audio = make_voice()
    image = make_background()
    video = make_video(image, audio)

    print("================================")
    print("VIDEO CREATED")
    print(video)
    print("================================")

if __name__ == "__main__":
    main()