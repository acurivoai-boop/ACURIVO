import os
import re
import subprocess
import urllib.parse
import urllib.request
from pathlib import Path

import requests
from PIL import Image


# ============================================================
# ACURIVO VIDEO FACTORY V6
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

# إيقاع أكثر هدوءًا
VOICE_RATE = "-6%"

SCENE_COUNT = 8


# ============================================================
# UTILITIES
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


def cleanup():

    for item in WORK_DIR.iterdir():

        try:

            if item.is_file():
                item.unlink()

        except Exception:
            pass


# ============================================================
# TOPIC DISCOVERY
# ============================================================

def discover_topic():

    print("\nDISCOVERING TOPIC...")

    queries = [
        "latest AI technology 2026",
        "new technology breakthrough 2026",
        "future technology 2026",
        "artificial intelligence breakthrough 2026",
        "new science discovery 2026",
        "robotics breakthrough 2026",
        "future energy technology 2026",
        "space technology 2026",
    ]

    candidates = []

    for query in queries:

        try:

            encoded = urllib.parse.quote(query)

            url = (
                "https://www.youtube.com/results?"
                f"search_query={encoded}"
            )

            request = urllib.request.Request(
                url,
                headers={
                    "User-Agent":
                    "Mozilla/5.0 "
                    "(X11; Linux x86_64) "
                    "AppleWebKit/537.36 "
                    "Chrome/120 Safari/537.36"
                },
            )

            html = urllib.request.urlopen(
                request,
                timeout=20
            ).read().decode(
                "utf-8",
                errors="ignore"
            )

            titles = re.findall(
                r'"title":{"runs":\[\{"text":"(.*?)"\}\]',
                html
            )

            for title in titles[:10]:

                title = (
                    title
                    .replace("\\u0026", "&")
                    .replace('\\"', '"')
                )

                if len(title) >= 15:
                    candidates.append(title)

        except Exception as error:

            print(
                "Topic search error:",
                error
            )

    if not candidates:

        return (
            "كيف يغيّر الذكاء الاصطناعي "
            "شكل المستقبل؟"
        )

    unique = list(dict.fromkeys(candidates))

    keywords = [
        "AI",
        "artificial intelligence",
        "technology",
        "future",
        "robot",
        "science",
        "energy",
        "space",
        "quantum",
        "breakthrough",
        "new",
        "2026",
    ]

    scored = []

    for title in unique:

        score = 0
        lower = title.lower()

        for keyword in keywords:

            if keyword.lower() in lower:
                score += 2

        if 25 <= len(title) <= 100:
            score += 3

        scored.append(
            (score, title)
        )

    scored.sort(
        key=lambda item: item[0],
        reverse=True
    )

    topic = scored[0][1]

    print(
        "\nSELECTED TOPIC:",
        topic
    )

    return topic


# ============================================================
# DOCUMENTARY SCRIPT
# ============================================================

def build_script(topic):

    return f"""
هناك تغيّرات تحدث الآن…
وقد لا ندرك حجمها إلا بعد سنوات.

ومن بين أكثرها إثارة للاهتمام…
{topic}.

في البداية، قد يبدو الأمر مجرد تطور تقني جديد.

لكن الحقيقة…
أن الصورة أكبر من ذلك بكثير.

وراء هذا التطور…
هناك علماء، وشركات، واستثمارات ضخمة،
ومنافسة عالمية على الوصول إلى المستقبل.

والأهم…
أن هذه التقنيات بدأت تنتقل من المختبرات…
إلى العالم الحقيقي.

تدخل في الأعمال.
وفي الصناعة.
وفي طريقة اتخاذ القرارات.

وهنا يبدأ السؤال الحقيقي…

ليس فقط:
ماذا تستطيع التقنية أن تفعل؟

بل…
إلى أين يمكن أن تقودنا؟

لأن كل قفزة تقنية كبيرة…
تفتح بابًا جديدًا من الفرص.

وفي الوقت نفسه…
تطرح أسئلة لم تكن موجودة من قبل.

ولهذا السبب…
فإن {topic}
ليس مجرد خبر عابر.

إنه جزء من تحول أكبر…

تحول بدأ بالفعل.

وربما يكون تأثيره على حياتنا…
أكبر مما نتوقع.
""".strip()


# ============================================================
# SPEECH CLEANING
# ============================================================

def prepare_for_speech(text):

    replacements = {
        "—": ",",
        "–": ",",
        "«": "",
        "»": "",
        '"': "",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # مسافات طبيعية
    text = re.sub(
        r"[ \t]+",
        " ",
        text
    )

    # تنظيف الأسطر
    lines = []

    for line in text.splitlines():

        line = line.strip()

        if line:
            lines.append(line)

    return "\n".join(lines)


# ============================================================
# CREATE SSML
# ============================================================

def create_ssml(text):

    # نحول الأسطر إلى فقرات منفصلة
    paragraphs = []

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        # وقفات بشرية خفيفة
        line = line.replace(
            "…",
            '<break time="450ms"/>'
        )

        line = line.replace(
            ".",
            '.<break time="220ms"/>'
        )

        line = line.replace(
            "؟",
            '؟<break time="350ms"/>'
        )

        line = line.replace(
            ":",
            ':<break time="250ms"/>'
        )

        paragraphs.append(
            f"<p>{line}</p>"
        )

    body = "\n".join(
        paragraphs
    )

    ssml = f"""
<speak version="1.0"
 xmlns="http://www.w3.org/2001/10/synthesis"
 xml:lang="ar-SA">

<voice name="{VOICE}">

{body}

</voice>

</speak>
""".strip()

    return ssml


# ============================================================
# GENERATE VOICE
# ============================================================

def generate_voice(text):

    print(
        "\nGENERATING CINEMATIC ARABIC VOICE..."
    )

    ssml_path = (
        WORK_DIR /
        "voice.ssml"
    )

    ssml = create_ssml(
        text
    )

    ssml_path.write_text(
        ssml,
        encoding="utf-8"
    )

    # --------------------------------------------------------
    # Edge TTS via SSML
    # --------------------------------------------------------

    run([
        "edge-tts",
        "--voice",
        VOICE,
        "--rate",
        VOICE_RATE,
        "--text",
        ssml,
        "--write-media",
        str(AUDIO_RAW),
    ])

    raw_duration = ffprobe_duration(
        AUDIO_RAW
    )

    print(
        "RAW VOICE:",
        f"{raw_duration:.2f}s"
    )

    # --------------------------------------------------------
    # CINEMATIC MASTERING
    # --------------------------------------------------------

    print(
        "\nMASTERING VOICE..."
    )

    audio_filter = (
        "highpass=f=70,"
        "lowpass=f=15000,"
        "acompressor="
        "threshold=-18dB:"
        "ratio=2.0:"
        "attack=18:"
        "release=180,"
        "equalizer="
        "f=180:"
        "width_type=o:"
        "width=1:"
        "g=0.7,"
        "equalizer="
        "f=2800:"
        "width_type=o:"
        "width=1.1:"
        "g=1.2,"
        "aecho="
        "0.78:"
        "0.18:"
        "65:"
        "0.08,"
        "volume=1.03"
    )

    run([
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
    ])

    final_duration = ffprobe_duration(
        AUDIO_FINAL
    )

    print(
        "MASTERED VOICE:",
        f"{final_duration:.2f}s"
    )

    return final_duration


# ============================================================
# VISUAL QUERIES
# ============================================================

def build_scene_queries(topic):

    return [

        f"{topic} modern technology",

        f"{topic} scientists laboratory",

        f"{topic} advanced futuristic technology",

        f"{topic} artificial intelligence computer",

        f"{topic} modern industry innovation",

        f"{topic} people technology future",

        f"{topic} futuristic city",

        f"{topic} future innovation cinematic",
    ]


# ============================================================
# WIKIMEDIA SEARCH
# ============================================================

def search_wikimedia(
    query,
    limit=10
):

    print(
        "\nSEARCHING VISUAL:",
        query
    )

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
            headers={
                "User-Agent":
                "ACURIVO/6.0"
            },
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

            info_list = page.get(
                "imageinfo",
                []
            )

            if not info_list:
                continue

            info = info_list[0]

            mime = info.get(
                "mime",
                ""
            )

            if not mime.startswith(
                "image/"
            ):
                continue

            url = (
                info.get("thumburl")
                or info.get("url")
            )

            if not url:
                continue

            results.append({
                "url": url,
                "title": page.get(
                    "title",
                    ""
                )
            })

        return results

    except Exception as error:

        print(
            "Wikimedia error:",
            error
        )

        return []


# ============================================================
# DOWNLOAD IMAGE
# ============================================================

def download_image(
    url,
    path
):

    try:

        response = requests.get(
            url,
            timeout=40,
            headers={
                "User-Agent":
                "ACURIVO/6.0"
            },
        )

        response.raise_for_status()

        temp = path.with_suffix(
            ".tmp"
        )

        temp.write_bytes(
            response.content
        )

        image = Image.open(
            temp
        ).convert("RGB")

        target_ratio = (
            WIDTH / HEIGHT
        )

        current_ratio = (
            image.width /
            image.height
        )

        if current_ratio > target_ratio:

            new_width = int(
                image.height *
                target_ratio
            )

            left = (
                image.width -
                new_width
            ) // 2

            image = image.crop(
                (
                    left,
                    0,
                    left + new_width,
                    image.height
                )
            )

        else:

            new_height = int(
                image.width /
                target_ratio
            )

            top = (
                image.height -
                new_height
            ) // 2

            image = image.crop(
                (
                    0,
                    top,
                    image.width,
                    top + new_height
                )
            )

        image = image.resize(
            (
                WIDTH,
                HEIGHT
            ),
            Image.Resampling.LANCZOS
        )

        image.save(
            path,
            "JPEG",
            quality=94
        )

        temp.unlink(
            missing_ok=True
        )

        return True

    except Exception as error:

        print(
            "IMAGE ERROR:",
            error
        )

        return False


# ============================================================
# COLLECT IMAGES
# ============================================================

def collect_images(topic):

    print(
        "\nBUILDING VISUAL STORY..."
    )

    queries = build_scene_queries(
        topic
    )

    images = []

    used = set()

    for index, query in enumerate(
        queries,
        start=1
    ):

        results = search_wikimedia(
            query,
            limit=10
        )

        selected = None

        for item in results:

            if item["title"] in used:
                continue

            selected = item
            break

        if not selected:

            print(
                f"SCENE {index}: "
                "NO IMAGE"
            )

            continue

        output = (
            WORK_DIR /
            f"scene_{index:02d}.jpg"
        )

        print(
            f"SCENE {index}: "
            f"{selected['title']}"
        )

        if download_image(
            selected["url"],
            output
        ):

            used.add(
                selected["title"]
            )

            images.append(
                output
            )

    print(
        "\nIMAGES READY:",
        len(images)
    )

    return images


# ============================================================
# RENDER SCENE
# ============================================================

def render_scene(
    image,
    output,
    duration,
    index
):

    frames = max(
        1,
        int(duration * 30)
    )

    if index % 3 == 0:

        zoom = (
            "zoompan="
            "z='min(zoom+0.0007,1.10)':"
            "x='iw/2-(iw/zoom/2)':"
            "y='ih/2-(ih/zoom/2)':"
            f"d={frames}:"
            "s=1920x1080:"
            "fps=30"
        )

    elif index % 3 == 1:

        zoom = (
            "zoompan="
            "z='min(zoom+0.00055,1.08)':"
            "x='iw/2-(iw/zoom/2)':"
            "y='ih/2-(ih/zoom/2)':"
            f"d={frames}:"
            "s=1920x1080:"
            "fps=30"
        )

    else:

        zoom = (
            "zoompan="
            "z='min(zoom+0.00045,1.07)':"
            "x='iw/2-(iw/zoom/2)':"
            "y='ih/2-(ih/zoom/2)':"
            f"d={frames}:"
            "s=1920x1080:"
            "fps=30"
        )

    vf = (
        f"scale={WIDTH}:{HEIGHT}:"
        "force_original_aspect_ratio=increase,"
        f"crop={WIDTH}:{HEIGHT},"
        "setsar=1,"
        f"{zoom}"
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
        f"{duration:.3f}",
        "-an",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "20",
        "-pix_fmt",
        "yuv420p",
        str(output),
    ])


# ============================================================
# FINAL RENDER
# ============================================================

def render_video(
    images,
    audio_duration
):

    print(
        "\nRENDERING FINAL VIDEO..."
    )

    if not images:
        raise RuntimeError(
            "No images available."
        )

    count = len(images)

    scene_duration = (
        audio_duration /
        count
    )

    scene_files = []

    for index, image in enumerate(
        images
    ):

        scene_output = (
            WORK_DIR /
            f"render_{index:02d}.mp4"
        )

        render_scene(
            image,
            scene_output,
            scene_duration + 0.15,
            index
        )

        scene_files.append(
            scene_output
        )

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
                .replace(
                    "'",
                    "'\\''"
                )
                + "'\n"
            )

    video_only = (
        WORK_DIR /
        "video_only.mp4"
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
        str(video_only),
    ])

    run([
        "ffmpeg",
        "-y",
        "-i",
        str(video_only),
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
        f"{audio_duration:.3f}",
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

    if final_duration + 0.15 < audio_duration:

        raise RuntimeError(
            "VIDEO ENDED BEFORE AUDIO."
        )

    print(
        "DURATION CHECK: PASS"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "\n"
        "========================================\n"
        " ACURIVO VIDEO FACTORY V6\n"
        " CINEMATIC DOCUMENTARY ENGINE\n"
        "========================================\n"
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
            "Not enough visuals."
        )

    render_video(
        images,
        audio_duration
    )

    print(
        "\n========================================"
    )

    print(
        "ACURIVO V6 COMPLETE"
    )

    print(
        "========================================\n"
    )


if __name__ == "__main__":
    main()