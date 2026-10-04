import os
import re
import json
import math
import time
import random
import subprocess
import urllib.parse
import urllib.request
from pathlib import Path

import requests
from PIL import Image


# ============================================================
# ACURIVO VIDEO FACTORY V5
# Cinematic Arabic Documentary Engine
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
WORK_DIR = BASE_DIR / "work"

OUTPUT_DIR.mkdir(exist_ok=True)
WORK_DIR.mkdir(exist_ok=True)

VIDEO_PATH = OUTPUT_DIR / "ACURIVO_VIDEO.mp4"
AUDIO_RAW = WORK_DIR / "voice_raw.mp3"
AUDIO_FINAL = WORK_DIR / "voice_final.mp3"

WIDTH = 1920
HEIGHT = 1080

VOICE = "ar-SA-HamedNeural"

# أبطأ قليلًا من القراءة الآلية
VOICE_RATE = "-8%"

# عدد المشاهد
SCENE_COUNT = 8

# ============================================================
# Utilities
# ============================================================

def run(cmd):
    print("RUN:", " ".join(str(x) for x in cmd))
    subprocess.run(cmd, check=True)


def ffprobe_duration(path):
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    return float(result.stdout.strip())


def clean_text(text):
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# ============================================================
# Topic discovery
# ============================================================

def discover_topic():
    print("\nDISCOVERING TOPIC...")

    queries = [
        "latest technology breakthrough",
        "future technology",
        "artificial intelligence breakthrough",
        "new scientific discovery",
        "future of energy",
        "space technology",
        "robotics future",
        "new invention",
        "advanced technology 2026",
        "science technology future",
    ]

    candidates = []

    for q in queries:
        try:
            encoded = urllib.parse.quote(q)

            url = (
                "https://www.youtube.com/results?"
                f"search_query={encoded}"
            )

            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent":
                    "Mozilla/5.0 (X11; Linux x86_64) "
                    "AppleWebKit/537.36 "
                    "Chrome/120 Safari/537.36"
                },
            )

            html = urllib.request.urlopen(
                req,
                timeout=20
            ).read().decode(
                "utf-8",
                errors="ignore"
            )

            titles = re.findall(
                r'"title":{"runs":\[\{"text":"(.*?)"\}\]',
                html
            )

            for title in titles[:8]:
                title = (
                    title
                    .replace("\\u0026", "&")
                    .replace("\\\"", '"')
                )

                if len(title) > 15:
                    candidates.append(title)

        except Exception as e:
            print("Topic search error:", e)

    if not candidates:
        return "كيف تغيّر الذكاء الاصطناعي طريقة عمل العالم؟"

    # إزالة التكرار
    unique = []

    for item in candidates:
        if item not in unique:
            unique.append(item)

    # نختار موضوعًا يبدو مناسبًا لفيديو وثائقي
    preferred = []

    keywords = [
        "AI",
        "artificial",
        "technology",
        "future",
        "robot",
        "science",
        "energy",
        "space",
        "innovation",
        "new",
        "2026",
    ]

    for title in unique:
        score = 0

        lower = title.lower()

        for word in keywords:
            if word.lower() in lower:
                score += 2

        if 25 <= len(title) <= 110:
            score += 2

        preferred.append((score, title))

    preferred.sort(
        key=lambda x: x[0],
        reverse=True
    )

    topic = preferred[0][1]

    print("SELECTED TOPIC:", topic)

    return topic


# ============================================================
# Arabic documentary script
# ============================================================

def build_script(topic):

    # النص هنا مكتوب ليُقرأ كتعليق وثائقي،
    # وليس كمقالة.

    return f"""
هناك أشياء تتغير أمام أعيننا...
لكننا لا نلاحظها إلا بعد فوات الوقت.

ومن بين أكثر التحولات إثارة للاهتمام اليوم:
{topic}.

الفكرة في ظاهرها قد تبدو بسيطة.
لكن خلفها...
هناك سباق هائل بين العلم، والاقتصاد، والإنسان.

خلال السنوات الأخيرة، لم تعد هذه التقنيات مجرد أفكار بعيدة.
بدأت تدخل إلى حياتنا...
وتغيّر الطريقة التي نعمل بها،
ونتخذ بها قراراتنا،
وننظر بها إلى المستقبل.

واللافت هنا...
أن التطور لا يحدث في مكان واحد.

هناك مختبرات تعمل على حلول جديدة،
وشركات تستثمر مليارات الدولارات،
وباحثون يحاولون دفع الحدود أبعد من أي وقت مضى.

لكن السؤال الحقيقي ليس:
ماذا تستطيع التقنية أن تفعل؟

السؤال الأهم هو...
إلى أين يمكن أن تقودنا؟

فكل تقدم كبير يحمل معه فرصة.
وفي الوقت نفسه...
يفتح بابًا جديدًا من الأسئلة.

وهذا تحديدًا ما يجعل {topic}
أكثر من مجرد خبر عابر.

إنه جزء من قصة أكبر...
قصة مستقبل يتشكل الآن.
""".strip()


# ============================================================
# Text preparation
# ============================================================

def prepare_for_speech(text):

    # تحسين الوقفات
    text = text.replace("...", "…")

    # وقفة قصيرة بعد الفواصل
    text = re.sub(r",\s*", ", ", text)

    # منع الجمل الطويلة جدًا
    text = text.replace(
        "لكن السؤال الحقيقي ليس:",
        "لكن السؤال الحقيقي... ليس:"
    )

    text = text.replace(
        "السؤال الأهم هو...",
        "السؤال الأهم... هو:"
    )

    return clean_text(text)


# ============================================================
# Generate voice
# ============================================================

def generate_voice(text):

    print("\nGENERATING ARABIC VOICE...")

    script_path = WORK_DIR / "script.txt"

    script_path.write_text(
        text,
        encoding="utf-8"
    )

    run([
        "edge-tts",
        "--voice",
        VOICE,
        "--rate",
        VOICE_RATE,
        "--text",
        text,
        "--write-media",
        str(AUDIO_RAW),
    ])

    print("RAW AUDIO GENERATED")

    duration = ffprobe_duration(AUDIO_RAW)

    print(
        f"RAW AUDIO DURATION: {duration:.2f}s"
    )

    # --------------------------------------------------------
    # Cinematic audio processing
    # --------------------------------------------------------

    print("\nADDING CINEMATIC VOICE PROCESSING...")

    filter_complex = (
        "highpass=f=75,"
        "lowpass=f=14500,"
        "acompressor="
        "threshold=-18dB:"
        "ratio=2.2:"
        "attack=20:"
        "release=180,"
        "equalizer="
        "f=2500:"
        "width_type=o:"
        "width=1.2:"
        "g=1.5,"
        "aecho="
        "0.8:"
        "0.32:"
        "55:"
        "0.16,"
        "volume=1.05"
    )

    run([
        "ffmpeg",
        "-y",
        "-i",
        str(AUDIO_RAW),
        "-af",
        filter_complex,
        "-codec:a",
        "libmp3lame",
        "-b:a",
        "192k",
        str(AUDIO_FINAL),
    ])

    final_duration = ffprobe_duration(
        AUDIO_FINAL
    )

    print(
        f"FINAL AUDIO DURATION: "
        f"{final_duration:.2f}s"
    )

    return final_duration


# ============================================================
# Semantic visual planning
# ============================================================

def build_scene_queries(topic):

    return [
        f"{topic} modern technology laboratory",
        f"{topic} futuristic technology 2026",
        f"{topic} scientists research laboratory",
        f"{topic} advanced artificial intelligence technology",
        f"{topic} modern industrial technology",
        f"{topic} futuristic city technology",
        f"{topic} technology innovation close up",
        f"{topic} future world cinematic",
    ]


# ============================================================
# Wikimedia image search
# ============================================================

def search_wikimedia(query, limit=5):

    print("IMAGE SEARCH:", query)

    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": query,
        "gsrnamespace": 6,
        "gsrlimit": limit,
        "prop": "imageinfo",
        "iiprop": "url|mime",
        "iiurlwidth": 1920,
        "format": "json",
    }

    try:
        response = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params=params,
            timeout=30,
        )

        data = response.json()

        pages = data.get(
            "query",
            {}
        ).get(
            "pages",
            {}
        )

        results = []

        for page in pages.values():

            imageinfo = page.get(
                "imageinfo",
                []
            )

            if not imageinfo:
                continue

            info = imageinfo[0]

            mime = info.get(
                "mime",
                ""
            )

            if not mime.startswith("image/"):
                continue

            url = info.get(
                "thumburl"
            ) or info.get(
                "url"
            )

            if url:
                results.append({
                    "url": url,
                    "title": page.get(
                        "title",
                        ""
                    )
                })

        return results

    except Exception as e:
        print(
            "Wikimedia error:",
            e
        )

        return []


# ============================================================
# Image download
# ============================================================

def download_image(url, path):

    try:

        response = requests.get(
            url,
            timeout=40,
            headers={
                "User-Agent":
                "ACURIVO/5.0"
            },
        )

        response.raise_for_status()

        temp = path.with_suffix(
            ".download"
        )

        temp.write_bytes(
            response.content
        )

        img = Image.open(
            temp
        ).convert("RGB")

        # توحيد الحجم
        img.thumbnail(
            (1920, 1080),
            Image.Resampling.LANCZOS
        )

        canvas = Image.new(
            "RGB",
            (1920, 1080)
        )

        x = (
            1920 - img.width
        ) // 2

        y = (
            1080 - img.height
        ) // 2

        canvas.paste(
            img,
            (x, y)
        )

        canvas.save(
            path,
            "JPEG",
            quality=94
        )

        temp.unlink(
            missing_ok=True
        )

        return True

    except Exception as e:

        print(
            "Download error:",
            e
        )

        return False


# ============================================================
# Build visual sequence
# ============================================================

def collect_images(topic):

    print("\nBUILDING VISUAL STORY...")

    queries = build_scene_queries(
        topic
    )

    image_paths = []

    used_titles = set()

    for index, query in enumerate(
        queries,
        start=1
    ):

        results = search_wikimedia(
            query,
            limit=8
        )

        selected = None

        for item in results:

            title = item["title"]

            if title in used_titles:
                continue

            selected = item

            break

        if not selected:
            print(
                f"NO GOOD IMAGE FOR SCENE {index}"
            )
            continue

        filename = (
            WORK_DIR /
            f"scene_{index:02d}.jpg"
        )

        print(
            f"SCENE {index}: "
            f"{selected['title']}"
        )

        if download_image(
            selected["url"],
            filename
        ):

            used_titles.add(
                selected["title"]
            )

            image_paths.append(
                filename
            )

    return image_paths


# ============================================================
# Cinematic scene rendering
# ============================================================

def render_video(
    images,
    audio_duration
):

    print("\nRENDERING CINEMATIC VIDEO...")

    if not images:
        raise RuntimeError(
            "No images available."
        )

    scene_count = len(images)

    # توزيع دقيق للمدة
    base_duration = (
        audio_duration /
        scene_count
    )

    image_duration = (
        base_duration + 0.25
    )

    # --------------------------------------------------------
    # Create individual scenes
    # --------------------------------------------------------

    scene_files = []

    for index, image in enumerate(
        images
    ):

        scene_output = (
            WORK_DIR /
            f"render_{index:02d}.mp4"
        )

        # تنويع الحركة
        if index % 3 == 0:
            zoom = (
                "zoompan="
                "z='min(zoom+0.0009,1.12)':"
                "x='iw/2-(iw/zoom/2)':"
                "y='ih/2-(ih/zoom/2)':"
                "d=1"
            )

        elif index % 3 == 1:
            zoom = (
                "zoompan="
                "z='min(zoom+0.0007,1.10)':"
                "x='iw/2-(iw/zoom/2)':"
                "y='ih/2-(ih/zoom/2)':"
                "d=1"
            )

        else:
            zoom = (
                "zoompan="
                "z='min(zoom+0.0006,1.08)':"
                "x='iw/2-(iw/zoom/2)':"
                "y='ih/2-(ih/zoom/2)':"
                "d=1"
            )

        vf = (
            f"scale={WIDTH}:{HEIGHT}:"
            "force_original_aspect_ratio=increase,"
            f"crop={WIDTH}:{HEIGHT},"
            "setsar=1,"
            f"{zoom},"
            "fps=30"
        )

        run([
            "ffmpeg",
            "-y",
            "-loop",
            "1",
            "-i",
            str(image),
            "-vf",
            vf,
            "-t",
            str(image_duration),
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "20",
            "-pix_fmt",
            "yuv420p",
            str(scene_output),
        ])

        scene_files.append(
            scene_output
        )

    # --------------------------------------------------------
    # Concatenate
    # --------------------------------------------------------

    concat_file = (
        WORK_DIR /
        "concat.txt"
    )

    with concat_file.open(
        "w",
        encoding="utf-8"
    ) as f:

        for scene in scene_files:

            f.write(
                "file '"
                + str(scene)
                .replace("'", "'\\''")
                + "'\n"
            )

    video_no_audio = (
        WORK_DIR /
        "video_no_audio.mp4"
    )

    run([
        "ffmpeg",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(concat_file),
        "-c",
        "copy",
        str(video_no_audio),
    ])

    # --------------------------------------------------------
    # Final audio + video
    # --------------------------------------------------------

    run([
        "ffmpeg",
        "-y",
        "-i",
        str(video_no_audio),
        "-i",
        str(AUDIO_FINAL),
        "-map",
        "0:v:0",
        "-map",
        "1:a:0",
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-t",
        str(audio_duration),
        "-movflags",
        "+faststart",
        str(VIDEO_PATH),
    ])

    final_duration = ffprobe_duration(
        VIDEO_PATH
    )

    print(
        "\nFINAL VIDEO DURATION:",
        f"{final_duration:.2f}s"
    )

    if final_duration + 0.2 < audio_duration:
        raise RuntimeError(
            "VIDEO ENDED BEFORE AUDIO."
        )

    print(
        "VIDEO LENGTH CHECK: PASS"
    )


# ============================================================
# Cleanup
# ============================================================

def cleanup():

    print("\nCLEANUP...")

    for item in WORK_DIR.iterdir():

        try:

            if item.is_file():
                item.unlink()

        except Exception:
            pass


# ============================================================
# Main
# ============================================================

def main():

    print(
        "\n"
        "=====================================\n"
        " ACURIVO VIDEO FACTORY V5\n"
        " CINEMATIC ARABIC DOCUMENTARY ENGINE\n"
        "=====================================\n"
    )

    cleanup()

    topic = discover_topic()

    script = build_script(
        topic
    )

    script = prepare_for_speech(
        script
    )

    print(
        "\nSCRIPT:\n"
    )

    print(script)

    audio_duration = generate_voice(
        script
    )

    images = collect_images(
        topic
    )

    if len(images) < 4:
        raise RuntimeError(
            "Not enough relevant images."
        )

    render_video(
        images,
        audio_duration
    )

    print(
        "\n====================================="
    )

    print(
        "ACURIVO V5 COMPLETE"
    )

    print(
        "VIDEO:",
        VIDEO_PATH
    )

    print(
        "=====================================\n"
    )


if __name__ == "__main__":
    main()
