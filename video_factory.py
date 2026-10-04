# ============================================================
# ACURIVO — RONALDO LEGEND STORY
# Production Video Factory
# ============================================================

import os
import re
import math
import time
import shutil
import random
import subprocess
import asyncio
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont
import edge_tts


# ============================================================
# CONFIG
# ============================================================

ROOT = Path(__file__).resolve().parent

WORK = ROOT / "work"
OUTPUT = ROOT / "output"

WORK.mkdir(exist_ok=True)
OUTPUT.mkdir(exist_ok=True)

VIDEO_FINAL = OUTPUT / "ACURIVO_VIDEO.mp4"

AUDIO_RAW = WORK / "voice_raw.mp3"
AUDIO_FINAL = WORK / "voice_final.mp3"

WIDTH = 1920
HEIGHT = 1080
FPS = 30

IMAGE_TIMEOUT = 15
MAX_IMAGE_BYTES = 8 * 1024 * 1024
IMAGE_MIN_BYTES = 20_000

VOICE = "ar-SA-HamedNeural"
VOICE_RATE = "-6%"
VOICE_PITCH = "-1Hz"

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) "
    "AppleWebKit/537.36 Chrome/120 Safari/537.36"
)


# ============================================================
# RONALDO STORY
# ============================================================

TITLE = "رونالدو... الطفل الذي رفض أن يكون عاديًا"

SCENES = [

    {
        "text": """
في جزيرة ماديرا البرتغالية، وُلد طفل اسمه كريستيانو رونالدو.
لم يكن يملك في بدايته ملاعب فاخرة، ولا طريقًا مضمونًا نحو الشهرة.
كان يملك كرة... وحلمًا أكبر من عمره.
ومنذ طفولته، كان يشعر أن كرة القدم ليست مجرد لعبة بالنسبة له.
كانت الطريق التي يريد أن يسلكها مهما كان الثمن.
""",
        "queries": [
            "Cristiano Ronaldo childhood Madeira",
            "Funchal Madeira Portugal football childhood",
            "young Portuguese football player childhood"
        ],
    },

    {
        "text": """
في الحادية عشرة من عمره، اتخذ رونالدو خطوة غيّرت حياته.
غادر ماديرا وانتقل إلى لشبونة للانضمام إلى أكاديمية سبورتينغ.
كان صغيرًا جدًا على أن يعيش بعيدًا عن عائلته،
لكن حلمه كان أكبر من خوفه.
هناك بدأ شيء مختلف تمامًا.
بدأت موهبته تلفت الأنظار،
وبدأ الجميع يلاحظ أن هذا الطفل ليس لاعبًا عاديًا.
""",
        "queries": [
            "Sporting CP academy Lisbon Ronaldo",
            "Sporting Lisbon football academy",
            "Lisbon Portugal football academy training"
        ],
    },

    {
        "text": """
تطور رونالدو بسرعة مذهلة.
في الخامسة عشرة كان يتدرب مع فريق سبورتينغ الثاني،
وفي السادسة عشرة بدأ التدريب مع الفريق الأول.
ثم جاء عام ألفين واثنين...
اللحظة التي ظهر فيها الفتى لأول مرة مع الفريق الأول.
كان عمره سبعة عشر عامًا فقط.
لكن ما قدمه في الملعب جعل الناس يتحدثون عن موهبة استثنائية قادمة.
""",
        "queries": [
            "Cristiano Ronaldo Sporting CP 2002",
            "Ronaldo Sporting Lisbon 2002",
            "Sporting CP Ronaldo young player"
        ],
    },

    {
        "text": """
ثم جاءت اللحظة التي غيرت كل شيء.
في أغسطس عام ألفين وثلاثة،
ظهر رونالدو بقميص مانشستر يونايتد أمام بولتون.
دخل شابًا صغيرًا...
وخرج من المباراة وهو حديث الجميع.
سرعته، مهاراته، جرأته، وقدرته على مواجهة المدافعين
جعلت السير أليكس فيرغسون يدرك أن أمامه مشروع نجم كبير.
""",
        "queries": [
            "Cristiano Ronaldo Manchester United 2003",
            "Ronaldo Manchester United debut 2003",
            "Old Trafford Ronaldo 2003"
        ],
    },

    {
        "text": """
لكن الموهبة وحدها لم تكن كافية.
في مانشستر يونايتد بدأ رونالدو رحلة التحول.
لم يعد مجرد جناح يراوغ المدافعين.
بدأ يتعلم كيف يتحرك، وكيف يسجل، وكيف يتحمل الضغط،
وكيف يحول المهارة إلى أرقام.
كان يتطور موسمًا بعد موسم.
وفي عام ألفين وثمانية،
وصل إلى واحدة من أعظم لحظات مسيرته.
دوري أبطال أوروبا...
ثم الكرة الذهبية.
""",
        "queries": [
            "Cristiano Ronaldo Manchester United 2008 Champions League",
            "Ronaldo Ballon d'Or 2008",
            "Manchester United Ronaldo 2008 celebration"
        ],
    },

    {
        "text": """
ثم جاء الانتقال الذي جعل العالم كله يراقبه.
في عام ألفين وتسعة،
انتقل رونالدو إلى ريال مدريد وهو في الرابعة والعشرين.
لم يكن مجرد انتقال لاعب كبير.
كان بداية مرحلة جديدة.
في مدريد، أصبح أكثر قوة،
وأكثر حسمًا،
وأكثر شراسة أمام المرمى.
تحول اللاعب الموهوب إلى ماكينة أهداف،
وأصبح اسمه مرتبطًا بأكبر ليالي كرة القدم.
""",
        "queries": [
            "Cristiano Ronaldo Real Madrid 2009",
            "Ronaldo Real Madrid presentation 2009",
            "Cristiano Ronaldo Santiago Bernabeu 2009"
        ],
    },

    {
        "text": """
ومع السنوات، لم تعد قصة رونالدو قصة موهبة فقط.
أصبحت قصة انضباط.
تدريب متواصل.
اهتمام بالتفاصيل.
ورغبة لا تهدأ في أن يكون أفضل.
لقد تغير جسده، وتغير أسلوب لعبه،
وتغيرت طريقته في التسجيل...
لكن الشيء الذي لم يتغير كان الجوع.
كلما وصل إلى القمة، بحث عن قمة أعلى.
""",
        "queries": [
            "Cristiano Ronaldo training Real Madrid",
            "Ronaldo intense training football",
            "Cristiano Ronaldo gym training"
        ],
    },

    {
        "text": """
من طفل صغير في ماديرا...
إلى فتى غادر عائلته في الحادية عشرة...
إلى لاعب شاب في سبورتينغ...
ثم نجم في مانشستر يونايتد...
ثم أسطورة في ريال مدريد...
أصبح كريستيانو رونالدو واحدًا من أشهر لاعبي كرة القدم في التاريخ.
لكن ربما تكون أعظم قصته ليست عدد الأهداف...
ولا عدد البطولات...
بل أنه أثبت أن الموهبة تفتح الباب،
لكن العمل والانضباط هما ما يبقيانك في القمة.
هذه ليست فقط قصة لاعب كرة قدم.
هذه قصة طفل قرر منذ البداية...
أنه لن يكون عاديًا.
""",
        "queries": [
            "Cristiano Ronaldo career celebration",
            "Cristiano Ronaldo legendary football career",
            "Ronaldo football stadium celebration"
        ],
    },

]


# ============================================================
# HELPERS
# ============================================================

def run(cmd, cwd=None):
    print("\nRUN:", " ".join(str(x) for x in cmd))

    result = subprocess.run(
        cmd,
        cwd=cwd,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    if result.stdout:
        print(result.stdout[-4000:])

    return result


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
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    return float(result.stdout.strip())


# ============================================================
# CLEAN
# ============================================================

def clean_workspace():

    print("\n=== CLEAN WORKSPACE ===")

    for folder in [WORK, OUTPUT]:

        folder.mkdir(exist_ok=True)

        for item in folder.iterdir():

            if item.is_file():
                try:
                    item.unlink()
                except Exception:
                    pass

            elif item.is_dir():
                try:
                    shutil.rmtree(item)
                except Exception:
                    pass

    print("WORKSPACE READY")


# ============================================================
# BUILD SCRIPT
# ============================================================

def build_script():

    print("\n=== BUILDING RONALDO STORY ===")

    parts = []

    for scene in SCENES:
        parts.append(scene["text"].strip())

    text = "\n\n".join(parts)

    script_file = WORK / "script.txt"
    script_file.write_text(text, encoding="utf-8")

    print("SCRIPT READY")
    print("CHARACTERS:", len(text))

    return text


# ============================================================
# VOICE
# ============================================================

async def create_voice_async(text):

    communicate = edge_tts.Communicate(
        text,
        VOICE,
        rate=VOICE_RATE,
        pitch=VOICE_PITCH,
    )

    await communicate.save(str(AUDIO_RAW))


def create_voice(text):

    print("\n=== GENERATING ARABIC VOICE ===")

    if AUDIO_RAW.exists():
        AUDIO_RAW.unlink()

    asyncio.run(
        create_voice_async(text)
    )

    if not AUDIO_RAW.exists():
        raise RuntimeError(
            "Voice generation failed."
        )

    duration = ffprobe_duration(
        AUDIO_RAW
    )

    print(
        f"RAW VOICE DURATION: {duration:.2f}s"
    )


# ============================================================
# PREMIUM AUDIO
# ============================================================

def master_audio():

    print("\n=== MASTERING PREMIUM VOICE ===")

    if AUDIO_FINAL.exists():
        AUDIO_FINAL.unlink()

    audio_filter = (
        "highpass=f=65,"
        "lowpass=f=15500,"
        "acompressor="
        "threshold=-20dB:"
        "ratio=2.4:"
        "attack=12:"
        "release=160,"
        "equalizer="
        "f=150:"
        "width_type=o:"
        "width=1:"
        "g=1.0,"
        "equalizer="
        "f=3000:"
        "width_type=o:"
        "width=1:"
        "g=1.5,"
        "aecho="
        "0.88:0.09:60:0.045,"
        "volume=1.15"
    )

    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(AUDIO_RAW),
            "-af",
            audio_filter,
            "-codec:a",
            "libmp3lame",
            "-b:a",
            "192k",
            str(AUDIO_FINAL),
        ]
    )

    duration = ffprobe_duration(
        AUDIO_FINAL
    )

    if duration <= 0:
        raise RuntimeError(
            "Premium audio mastering failed."
        )

    print(
        f"PREMIUM AUDIO: {duration:.2f}s"
    )


# ============================================================
# WIKIMEDIA SEARCH
# ============================================================

def wikimedia_search(query, limit=8):

    url = (
        "https://commons.wikimedia.org/w/api.php"
    )

    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": query,
        "gsrnamespace": 6,
        "gsrlimit": limit,
        "prop": "imageinfo",
        "iiprop": "url|size|mime",
        "format": "json",
    }

    try:

        response = requests.get(
            url,
            params=params,
            headers={
                "User-Agent": USER_AGENT
            },
            timeout=IMAGE_TIMEOUT,
        )

        response.raise_for_status()

        data = response.json()

        pages = (
            data
            .get("query", {})
            .get("pages", {})
        )

        results = []

        for page in pages.values():

            info = (
                page
                .get("imageinfo", [])
            )

            if not info:
                continue

            item = info[0]

            image_url = item.get("url")

            mime = (
                item
                .get("mime", "")
                .lower()
            )

            width = item.get("width", 0)
            height = item.get("height", 0)

            if not image_url:
                continue

            if not mime.startswith("image/"):
                continue

            if width < 500 or height < 300:
                continue

            results.append(
                {
                    "title": page.get(
                        "title",
                        ""
                    ),
                    "url": image_url,
                    "width": width,
                    "height": height,
                }
            )

        return results

    except Exception as e:

        print(
            "WIKIMEDIA SEARCH ERROR:",
            e
        )

        return []


# ============================================================
# IMAGE DOWNLOAD — ROBUST
# ============================================================

def download_image(url, output):

    try:

        print(
            "DOWNLOADING IMAGE..."
        )

        response = requests.get(
            url,
            headers={
                "User-Agent": USER_AGENT
            },
            timeout=(5, IMAGE_TIMEOUT),
            stream=True,
            allow_redirects=True,
        )

        response.raise_for_status()

        content_type = (
            response.headers
            .get("Content-Type", "")
            .lower()
        )

        if not content_type.startswith(
            "image/"
        ):
            raise RuntimeError(
                f"Invalid content type: {content_type}"
            )

        content_length = (
            response.headers
            .get("Content-Length")
        )

        if content_length:

            try:

                if int(content_length) > MAX_IMAGE_BYTES:

                    raise RuntimeError(
                        "Image exceeds maximum size."
                    )

            except ValueError:
                pass

        data = bytearray()

        for chunk in response.iter_content(
            chunk_size=64 * 1024
        ):

            if not chunk:
                continue

            data.extend(chunk)

            if len(data) > MAX_IMAGE_BYTES:

                raise RuntimeError(
                    "Image exceeds maximum size."
                )

        if len(data) < IMAGE_MIN_BYTES:

            raise RuntimeError(
                "Image too small."
            )

        output.write_bytes(
            bytes(data)
        )

        # First validation
        with Image.open(output) as img:
            img.verify()

        # Second validation
        with Image.open(output) as img:

            img.load()

            width, height = img.size

            if width < 300 or height < 300:

                raise RuntimeError(
                    "Image resolution is too small."
                )

        print(
            f"IMAGE OK: "
            f"{len(data) / 1024 / 1024:.2f} MB"
        )

        return True

    except Exception as e:

        print(
            "Image download failed:",
            e
        )

        try:
            output.unlink(
                missing_ok=True
            )
        except Exception:
            pass

        return False


# ============================================================
# SCORE IMAGE
# ============================================================

def score_image(title, query):

    title_lower = title.lower()
    query_words = set(
        re.findall(
            r"[a-zA-Z0-9]+",
            query.lower()
        )
    )

    title_words = set(
        re.findall(
            r"[a-zA-Z0-9]+",
            title_lower
        )
    )

    score = len(
        query_words.intersection(
            title_words
        )
    )

    # Strong Ronaldo relevance
    if "ronaldo" in title_lower:
        score += 8

    if "cristiano" in title_lower:
        score += 8

    if "football" in title_lower:
        score += 2

    if "sporting" in title_lower:
        score += 2

    if "manchester" in title_lower:
        score += 2

    if "real madrid" in title_lower:
        score += 2

    return score


# ============================================================
# FALLBACK CINEMATIC IMAGE
# ============================================================

def create_fallback_image(index, text):

    output = (
        WORK /
        f"scene_{index:02d}.jpg"
    )

    img = Image.new(
        "RGB",
        (WIDTH, HEIGHT),
        (15, 18, 25),
    )

    draw = ImageDraw.Draw(img)

    # Gradient
    for y in range(HEIGHT):

        shade = int(
            15 +
            35 * y / HEIGHT
        )

        draw.line(
            [(0, y), (WIDTH, y)],
            fill=(
                shade,
                shade,
                shade + 8
            ),
        )

    # Football-like circles
    random.seed(index)

    for _ in range(20):

        x = random.randint(
            0,
            WIDTH
        )

        y = random.randint(
            0,
            HEIGHT
        )

        r = random.randint(
            10,
            50
        )

        draw.ellipse(
            [
                x-r,
                y-r,
                x+r,
                y+r
            ],
            outline=(
                120,
                120,
                140
            ),
            width=2,
        )

    # Text
    try:

        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            70,
        )

        small_font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            32,
        )

    except Exception:

        font = None
        small_font = None

    title = "CRISTIANO RONALDO"

    bbox = draw.textbbox(
        (0, 0),
        title,
        font=font
    )

    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]

    draw.text(
        (
            (WIDTH - tw) / 2,
            HEIGHT / 2 - th
        ),
        title,
        fill=(245, 245, 245),
        font=font,
    )

    draw.text(
        (70, HEIGHT - 90),
        f"ACURIVO  •  STORY {index}",
        fill=(180, 180, 190),
        font=small_font,
    )

    img.save(
        output,
        quality=94
    )

    return output


# ============================================================
# CREATE SCENE IMAGE
# ============================================================

def create_scene_image(index, scene):

    print(
        f"\n=== SCENE {index} VISUAL ==="
    )

    image_path = (
        WORK /
        f"scene_{index:02d}.jpg"
    )

    candidates = []

    # Search every relevant query
    for query in scene["queries"]:

        print(
            "SEARCH:",
            query
        )

        results = wikimedia_search(
            query,
            limit=8
        )

        for item in results:

            score = score_image(
                item["title"],
                query
            )

            candidates.append(
                (
                    score,
                    item
                )
            )

    # Sort best first
    candidates.sort(
        key=lambda x: x[0],
        reverse=True
    )

    # Remove duplicate URLs
    seen = set()
    unique = []

    for score, item in candidates:

        url = item["url"]

        if url in seen:
            continue

        seen.add(url)

        unique.append(
            (
                score,
                item
            )
        )

    # Try all good candidates
    for score, item in unique:

        print(
            "TRY IMAGE:",
            item["title"]
        )

        if download_image(
            item["url"],
            image_path
        ):

            print(
                "SELECTED:",
                item["title"]
            )

            return image_path

    # Never kill the video
    print(
        "NO VALID IMAGE FOUND."
    )

    print(
        "CREATING CINEMATIC FALLBACK."
    )

    return create_fallback_image(
        index,
        scene["text"]
    )


# ============================================================
# KEN BURNS / CINEMATIC VIDEO
# ============================================================

def image_to_video(
    image,
    output,
    duration,
    index
):

    zoom_start = 1.00 + (
        (index % 3) * 0.015
    )

    zoom_end = zoom_start + 0.07

    frames = max(
        1,
        int(duration * FPS)
    )

    zoom_expression = (
        f"{zoom_start:.4f}+"
        f"({zoom_end - zoom_start:.4f})"
        f"*on/{frames}"
    )

    vf = (
        "scale="
        f"{WIDTH}:"
        f"{HEIGHT}:"
        "force_original_aspect_ratio=increase,"
        f"crop={WIDTH}:{HEIGHT},"
        f"zoompan=z='{zoom_expression}':"
        f"d={frames}:"
        f"s={WIDTH}x{HEIGHT}:"
        f"fps={FPS},"
        "eq=contrast=1.03:"
        "saturation=1.05:"
        "brightness=-0.01,"
        "format=yuv420p"
    )

    run(
        [
            "ffmpeg",
            "-y",
            "-loop",
            "1",
            "-i",
            str(image),
            "-vf",
            vf,
            "-t",
            str(duration),
            "-r",
            str(FPS),
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "22",
            "-pix_fmt",
            "yuv420p",
            str(output),
        ]
    )


# ============================================================
# BUILD SCENES
# ============================================================

def build_scene_videos():

    print(
        "\n=== BUILDING SCENE VIDEOS ==="
    )

    total_audio_duration = (
        ffprobe_duration(
            AUDIO_FINAL
        )
    )

    # Allocate time according to text length
    text_lengths = [
        len(scene["text"])
        for scene in SCENES
    ]

    total_chars = sum(
        text_lengths
    )

    scene_files = []

    for index, scene in enumerate(
        SCENES,
        start=1
    ):

        share = (
            len(scene["text"])
            / total_chars
        )

        duration = (
            total_audio_duration
            * share
        )

        # Keep scenes visually meaningful
        duration = max(
            4.0,
            duration
        )

        image = create_scene_image(
            index,
            scene
        )

        scene_video = (
            WORK /
            f"scene_{index:02d}.mp4"
        )

        print(
            f"SCENE {index}: "
            f"{duration:.2f}s"
        )

        image_to_video(
            image,
            scene_video,
            duration,
            index
        )

        scene_files.append(
            scene_video
        )

    return scene_files


# ============================================================
# CONCAT
# ============================================================

def concat_scenes(scene_files):

    print(
        "\n=== CONCATENATING SCENES ==="
    )

    concat_file = (
        WORK / "concat.txt"
    )

    lines = []

    for scene in scene_files:

        safe_path = (
            scene
            .resolve()
            .as_posix()
        )

        lines.append(
            f"file '{safe_path}'"
        )

    concat_file.write_text(
        "\n".join(lines),
        encoding="utf-8"
    )

    video_no_audio = (
        WORK /
        "video_no_audio.mp4"
    )

    run(
        [
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
        ]
    )

    return video_no_audio


# ============================================================
# FINAL VIDEO
# ============================================================

def create_final_video(
    video_no_audio
):

    print(
        "\n=== CREATING FINAL VIDEO ==="
    )

    if VIDEO_FINAL.exists():
        VIDEO_FINAL.unlink()

    run(
        [
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
            "-shortest",
            "-movflags",
            "+faststart",
            str(VIDEO_FINAL),
        ]
    )

    if not VIDEO_FINAL.exists():

        raise RuntimeError(
            "Final video was not created."
        )

    duration = ffprobe_duration(
        VIDEO_FINAL
    )

    size_mb = (
        VIDEO_FINAL.stat().st_size
        / 1024
        / 1024
    )

    print(
        "\n=============================="
    )

    print(
        "FINAL VIDEO READY"
    )

    print(
        f"DURATION: {duration:.2f}s"
    )

    print(
        f"SIZE: {size_mb:.2f} MB"
    )

    print(
        "=============================="
    )

    if size_mb > 45:

        print(
            "WARNING: VIDEO ABOVE 45 MB"
        )

    return VIDEO_FINAL


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        """
========================================================
ACURIVO — CRISTIANO RONALDO LEGEND STORY
========================================================
"""
    )

    clean_workspace()

    # 1
    script = build_script()

    # 2
    create_voice(
        script
    )

    # 3
    master_audio()

    # 4
    scene_files = (
        build_scene_videos()
    )

    # 5
    video_no_audio = (
        concat_scenes(
            scene_files
        )
    )

    # 6
    create_final_video(
        video_no_audio
    )

    print(
        "\nACURIVO RONALDO VIDEO COMPLETE."
    )


if __name__ == "__main__":
    main()