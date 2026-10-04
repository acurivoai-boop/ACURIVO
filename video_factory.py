import asyncio
import base64
import json
import os
import random
import re
import subprocess
import sys
import textwrap
import urllib.parse
import urllib.request
from pathlib import Path

import edge_tts
import requests
from PIL import Image, ImageFilter, ImageEnhance, ImageOps


# ============================================================
# ACURIVO VIDEO FACTORY V7
# ============================================================

ROOT = Path(__file__).resolve().parent
WORK = ROOT / "work"
OUTPUT = ROOT / "output"

WORK.mkdir(exist_ok=True)
OUTPUT.mkdir(exist_ok=True)

VIDEO_PATH = OUTPUT / "ACURIVO_VIDEO.mp4"
AUDIO_RAW = WORK / "voice_raw.mp3"
AUDIO_FINAL = WORK / "voice_final.mp3"

VOICE = "ar-SA-HamedNeural"
VOICE_RATE = "-6%"
VOICE_PITCH = "-1Hz"

WIDTH = 1920
HEIGHT = 1080
FPS = 30

SCENE_COUNT = 8

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) "
    "AppleWebKit/537.36 Chrome/120 Safari/537.36"
)


# ============================================================
# BASIC HELPERS
# ============================================================

def run(cmd, check=True):
    print("RUN:", " ".join(str(x) for x in cmd))
    return subprocess.run(
        [str(x) for x in cmd],
        check=check,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )


def ffprobe_duration(path):
    result = run([
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(path)
    ])

    try:
        return float(result.stdout.strip())
    except Exception:
        return 0.0


def clean_text(text):
    text = text or ""

    # Remove HTML
    text = re.sub(r"<[^>]+>", " ", text)

    # Remove SSML if an upstream component accidentally returns it.
    text = re.sub(r"</?(?:speak|voice|p|prosody)[^>]*>", " ", text)
    text = re.sub(r"<break[^>]*/?>", "، ", text)

    # Remove markdown
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = re.sub(r"`(.*?)`", r"\1", text)

    # Remove weird control characters
    text = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", " ", text)

    # Normalize whitespace
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def normalize_arabic(text):
    text = clean_text(text)

    replacements = {
        "أ": "ا",
        "إ": "ا",
        "آ": "ا",
        "ى": "ي",
        "ة": "ة",
    }

    for a, b in replacements.items():
        text = text.replace(a, b)

    return text


def keyword_tokens(text):
    text = normalize_arabic(text)
    words = re.findall(r"[\u0600-\u06FF]{3,}|[A-Za-z]{4,}", text)
    stop = {
        "هذا", "هذه", "ذلك", "تلك", "التي", "الذي",
        "هناك", "يمكن", "خلال", "عندما", "اليوم",
        "العالم", "بشكل", "اكثر", "الناس", "حول",
        "كيف", "لماذا", "ماذا", "انه", "انها",
        "الى", "على", "من", "في", "عن", "مع",
    }
    return [w for w in words if w not in stop]


# ============================================================
# TOPIC DISCOVERY
# ============================================================

def discover_topic():
    print("\n=== DISCOVERING TOPIC ===")

    queries = [
        "latest technology news",
        "AI latest news",
        "artificial intelligence breakthrough",
        "future technology",
        "science technology latest",
        "business technology trend",
        "energy technology latest",
        "space technology latest",
    ]

    candidates = []

    for query in queries:
        try:
            url = (
                "https://www.youtube.com/results?search_query="
                + urllib.parse.quote(query)
            )

            req = urllib.request.Request(
                url,
                headers={"User-Agent": USER_AGENT}
            )

            with urllib.request.urlopen(req, timeout=20) as response:
                html = response.read().decode("utf-8", errors="ignore")

            titles = re.findall(
                r'"title":{"runs":\[\{"text":"(.*?)"\}\]',
                html
            )

            for title in titles[:12]:
                title = clean_text(title)

                if len(title) < 20:
                    continue

                if title not in candidates:
                    candidates.append(title)

        except Exception as e:
            print("Topic search warning:", e)

    if not candidates:
        return (
            "كيف يغيّر الذكاء الاصطناعي طريقة عمل الشركات "
            "واتخاذ القرارات في السنوات القادمة؟"
        )

    # Prefer contemporary / explanatory topics.
    priority_words = [
        "AI", "AI", "artificial",
        "ذكاء", "الذكاء",
        "future", "المستقبل",
        "technology", "تقنية",
        "robot", "روبوت",
        "energy", "طاقة",
        "space", "فضاء",
        "chip", "رقائق",
    ]

    scored = []

    for title in candidates:
        score = 0

        lower = title.lower()

        for word in priority_words:
            if word.lower() in lower:
                score += 3

        # Penalize obvious entertainment / sports.
        bad = [
            "football", "soccer", "match", "goal",
            "music", "song", "movie", "trailer",
            "gaming", "gameplay", "celebrity"
        ]

        for word in bad:
            if word in lower:
                score -= 10

        score += min(len(title) / 50, 2)

        scored.append((score, title))

    scored.sort(reverse=True)

    topic = scored[0][1]

    print("SELECTED TOPIC:", topic)

    return topic


# ============================================================
# SCRIPT GENERATION
# ============================================================

def build_script(topic):
    """
    Creates 8 independent narration scenes.
    The wording intentionally avoids SSML.
    """

    topic = clean_text(topic)

    scenes = [
        {
            "text": (
                f"في السنوات الأخيرة، بدأ موضوع {topic} "
                "يتحول من فكرة متخصصة إلى موضوع يؤثر في القرارات "
                "والأعمال والحياة اليومية."
            ),
            "queries": [
                topic,
                topic + " technology",
                topic + " modern",
            ],
        },
        {
            "text": (
                "لكن السؤال الأهم ليس فقط ماذا يحدث، "
                "بل لماذا أصبح هذا الموضوع مهمًا الآن؟ "
                "السبب هو تسارع التطور، وتداخل التقنية مع قطاعات "
                "كانت في السابق بعيدة عنها."
            ),
            "queries": [
                topic + " technology",
                topic + " innovation",
                topic + " future",
            ],
        },
        {
            "text": (
                "التغيير الحقيقي يظهر عندما تنتقل الفكرة "
                "من المختبر أو الأخبار إلى تطبيقات فعلية. "
                "عندها تبدأ الشركات والمؤسسات في إعادة التفكير "
                "في طريقة العمل، والتكلفة، والسرعة، وحتى المخاطر."
            ),
            "queries": [
                topic + " industry",
                topic + " business",
                topic + " real world",
            ],
        },
        {
            "text": (
                "وهنا تظهر نقطة مهمة. "
                "التقنية وحدها لا تكفي. "
                "القيمة الحقيقية تأتي من الطريقة التي تستخدم بها، "
                "ومن جودة البيانات، ومن قدرة الإنسان على اتخاذ "
                "القرار الصحيح في الوقت المناسب."
            ),
            "queries": [
                topic + " data",
                topic + " decision making",
                topic + " enterprise",
            ],
        },
        {
            "text": (
                "وفي المقابل، توجد تحديات لا يمكن تجاهلها. "
                "منها الخصوصية، والأمن، والاعتماد الزائد على الأنظمة، "
                "إضافة إلى الحاجة إلى مهارات جديدة تستطيع التعامل "
                "مع هذا التحول بسرعة ووعي."
            ),
            "queries": [
                topic + " cybersecurity",
                topic + " risk",
                topic + " security",
            ],
        },
        {
            "text": (
                "ورغم هذه التحديات، فإن الاتجاه العام واضح. "
                "الجهات التي تفهم التحول مبكرًا تستطيع بناء ميزة "
                "تنافسية، بينما قد تجد الجهات المتأخرة نفسها "
                "تتعامل مع واقع جديد فرض نفسه بالفعل."
            ),
            "queries": [
                topic + " future business",
                topic + " transformation",
                topic + " innovation",
            ],
        },
        {
            "text": (
                "خلال السنوات القادمة، لن يكون السؤال فقط "
                "من يملك التقنية الأقوى. "
                "السؤال سيكون: من يستطيع تحويلها إلى قيمة حقيقية، "
                "وبطريقة آمنة ومستدامة وقابلة للتوسع؟"
            ),
            "queries": [
                topic + " future",
                topic + " next generation",
                topic + " emerging technology",
            ],
        },
        {
            "text": (
                "وفي النهاية، قد لا يكون أهم ما في هذا التحول "
                "هو التقنية نفسها، بل الطريقة التي ستغير بها "
                "قراراتنا وأعمالنا ونظرتنا إلى المستقبل. "
                "وهذا بالضبط ما يجعل متابعة هذه التطورات أمرًا يستحق الانتباه."
            ),
            "queries": [
                topic + " future",
                topic + " world",
                topic + " innovation future",
            ],
        },
    ]

    return scenes


# ============================================================
# VOICE
# ============================================================

async def generate_voice_async(text, output):
    """
    Direct Python API.
    No edge-tts CLI.
    No SSML.
    """

    text = clean_text(text)

    communicate = edge_tts.Communicate(
        text=text,
        voice=VOICE,
        rate=VOICE_RATE,
        pitch=VOICE_PITCH,
    )

    await communicate.save(str(output))


def generate_voice(text, output):
    print("\n=== GENERATING ARABIC VOICE ===")

    if output.exists():
        output.unlink()

    asyncio.run(generate_voice_async(text, output))

    duration = ffprobe_duration(output)

    if duration <= 0:
        raise RuntimeError("Voice generation produced an invalid audio file.")

    print(f"VOICE DURATION: {duration:.2f}s")


# ============================================================
# CINEMATIC AUDIO
# ============================================================

def master_audio():
    print("\n=== MASTERING VOICE ===")

    if AUDIO_FINAL.exists():
        AUDIO_FINAL.unlink()

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
        "0.88:0.10:55:0.055,"
        "volume=1.03"
    )

    run([
        "ffmpeg",
        "-y",
        "-i", str(AUDIO_RAW),
        "-af", audio_filter,
        "-codec:a", "libmp3lame",
        "-b:a", "192k",
        str(AUDIO_FINAL),
    ])

    duration = ffprobe_duration(AUDIO_FINAL)

    if duration <= 0:
        raise RuntimeError("Final audio mastering failed.")

    print(f"MASTERED AUDIO: {duration:.2f}s")


# ============================================================
# WIKIMEDIA SEARCH
# ============================================================

def search_wikimedia(query, limit=8):
    try:
        api = "https://commons.wikimedia.org/w/api.php"

        params = {
            "action": "query",
            "format": "json",
            "generator": "search",
            "gsrsearch": query,
            "gsrnamespace": 6,
            "gsrlimit": limit,
            "prop": "imageinfo",
            "iiprop": "url|mime|size",
            "iiurlwidth": 1600,
        }

        response = requests.get(
            api,
            params=params,
            headers={"User-Agent": USER_AGENT},
            timeout=25,
        )

        response.raise_for_status()

        data = response.json()

        pages = data.get("query", {}).get("pages", {})

        results = []

        for page in pages.values():
            info = page.get("imageinfo", [{}])[0]

            mime = info.get("mime", "")

            if not mime.startswith("image/"):
                continue

            url = info.get("thumburl") or info.get("url")

            if url:
                results.append({
                    "url": url,
                    "title": page.get("title", ""),
                })

        return results

    except Exception as e:
        print("Wikimedia search warning:", e)
        return []


# ============================================================
# IMAGE RELEVANCE
# ============================================================

def score_image(title, query):
    title_words = set(keyword_tokens(title))
    query_words = set(keyword_tokens(query))

    if not query_words:
        return 0

    overlap = len(title_words & query_words)

    score = overlap * 10

    # Reward useful visual concepts.
    visual_words = [
        "technology",
        "computer",
        "robot",
        "machine",
        "laboratory",
        "science",
        "energy",
        "space",
        "industry",
        "data",
        "artificial",
        "intelligence",
        "future",
        "research",
        "satellite",
        "chip",
        "server",
    ]

    combined = " ".join(title_words)

    for word in visual_words:
        if word in combined:
            score += 1

    return score


def select_image(query, candidates):
    if not candidates:
        return None

    ranked = sorted(
        candidates,
        key=lambda x: score_image(
            x.get("title", ""),
            query
        ),
        reverse=True
    )

    return ranked[0]


# ============================================================
# IMAGE DOWNLOAD
# ============================================================

def download_image(url, output):
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": USER_AGENT}
        )

        with urllib.request.urlopen(req, timeout=30) as response:
            data = response.read()

        output.write_bytes(data)

        with Image.open(output) as img:
            img.verify()

        return True

    except Exception as e:
        print("Image download failed:", e)

        try:
            output.unlink(missing_ok=True)
        except Exception:
            pass

        return False


# ============================================================
# IMAGE PREPARATION
# ============================================================

def prepare_image(source, target):
    with Image.open(source) as img:
        img = img.convert("RGB")

        # Fill 16:9 without distortion.
        img = ImageOps.fit(
            img,
            (WIDTH, HEIGHT),
            method=Image.Resampling.LANCZOS,
            centering=(0.5, 0.5),
        )

        # Mild cinematic processing.
        img = ImageEnhance.Contrast(img).enhance(1.04)
        img = ImageEnhance.Color(img).enhance(1.02)
        img = img.filter(ImageFilter.GaussianBlur(radius=0.05))

        img.save(
            target,
            "JPEG",
            quality=94,
            optimize=True
        )


# ============================================================
# SCENE IMAGE CREATION
# ============================================================

def create_scene_image(scene_index, scene):
    print(f"\n=== VISUAL SCENE {scene_index} ===")

    candidates = []

    for query in scene["queries"]:
        print("SEARCH:", query)

        results = search_wikimedia(query, limit=8)

        for item in results:
            if item["url"] not in [x["url"] for x in candidates]:
                candidates.append(item)

        if len(candidates) >= 10:
            break

    selected = select_image(
        " ".join(scene["queries"]),
        candidates
    )

    if not selected:
        raise RuntimeError(
            f"No relevant visual found for scene {scene_index}."
        )

    print("SELECTED IMAGE:", selected["title"])

    raw = WORK / f"scene_{scene_index}_raw.jpg"
    final = WORK / f"scene_{scene_index}.jpg"

    if not download_image(selected["url"], raw):
        raise RuntimeError(
            f"Could not download image for scene {scene_index}."
        )

    prepare_image(raw, final)

    return final


# ============================================================
# SCENE AUDIO
# ============================================================

def generate_scene_audios(scenes):
    print("\n=== GENERATING SCENE AUDIO ===")

    audio_files = []

    for i, scene in enumerate(scenes, start=1):
        path = WORK / f"scene_{i}_voice.mp3"

        if path.exists():
            path.unlink()

        generate_voice(scene["text"], path)

        audio_files.append(path)

    return audio_files


# ============================================================
# CONCATENATE SCENE AUDIO
# ============================================================

def concatenate_audio(audio_files, output):
    print("\n=== CONCATENATING SCENE AUDIO ===")

    list_file = WORK / "audio_list.txt"

    with list_file.open("w", encoding="utf-8") as f:
        for path in audio_files:
            safe = str(path.resolve()).replace("'", "'\\''")
            f.write(f"file '{safe}'\n")

    run([
        "ffmpeg",
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(list_file),
        "-c:a", "libmp3lame",
        "-b:a", "192k",
        str(output),
    ])

    duration = ffprobe_duration(output)

    if duration <= 0:
        raise RuntimeError("Audio concatenation failed.")

    print(f"TOTAL AUDIO: {duration:.2f}s")


# ============================================================
# SCENE VIDEO
# ============================================================

def render_scene(index, image_path, audio_path):
    print(f"\n=== RENDERING SCENE {index} ===")

    duration = ffprobe_duration(audio_path)

    if duration <= 0:
        raise RuntimeError(
            f"Invalid audio duration for scene {index}"
        )

    output = WORK / f"scene_{index}.mp4"

    # Slightly different zoom direction per scene.
    if index % 2 == 0:
        zoom = (
            "zoompan="
            "z='min(zoom+0.00045,1.12)':"
            "x='iw/2-(iw/zoom/2)':"
            "y='ih/2-(ih/zoom/2)':"
            f"d=1:s={WIDTH}x{HEIGHT}:fps={FPS}"
        )
    else:
        zoom = (
            "zoompan="
            "z='min(zoom+0.00038,1.10)':"
            "x='iw/2-(iw/zoom/2)':"
            "y='ih/2-(ih/zoom/2)':"
            f"d=1:s={WIDTH}x{HEIGHT}:fps={FPS}"
        )

    run([
        "ffmpeg",
        "-y",
        "-loop", "1",
        "-i", str(image_path),
        "-i", str(audio_path),
        "-vf", zoom,
        "-t", f"{duration:.3f}",
        "-r", str(FPS),
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        str(output),
    ])

    actual = ffprobe_duration(output)

    if actual <= 0:
        raise RuntimeError(
            f"Scene {index} rendering failed."
        )

    return output


# ============================================================
# CONCATENATE VIDEO
# ============================================================

def concatenate_video(scene_videos):
    print("\n=== BUILDING FINAL VIDEO ===")

    list_file = WORK / "video_list.txt"

    with list_file.open("w", encoding="utf-8") as f:
        for path in scene_videos:
            safe = str(path.resolve()).replace("'", "'\\''")
            f.write(f"file '{safe}'\n")

    temp_video = WORK / "video_concat.mp4"

    run([
        "ffmpeg",
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(list_file),
        "-c", "copy",
        str(temp_video),
    ])

    return temp_video


# ============================================================
# FINAL AUDIO / VIDEO MUX
# ============================================================

def mux_final_video(video_file):
    print("\n=== FINAL VIDEO MUX ===")

    if VIDEO_PATH.exists():
        VIDEO_PATH.unlink()

    run([
        "ffmpeg",
        "-y",
        "-i", str(video_file),
        "-i", str(AUDIO_FINAL),
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        "-shortest",
        str(VIDEO_PATH),
    ])

    duration = ffprobe_duration(VIDEO_PATH)

    if duration <= 0:
        raise RuntimeError("Final video duration is invalid.")

    size_mb = VIDEO_PATH.stat().st_size / 1024 / 1024

    print(f"\nFINAL VIDEO: {duration:.2f}s")
    print(f"FINAL SIZE: {size_mb:.2f} MB")

    if size_mb > 45:
        print("WARNING: Video exceeds 45 MB.")


# ============================================================
# CLEAN WORK FILES
# ============================================================

def cleanup():
    print("\n=== CLEANUP ===")

    # Keep the final assets useful for debugging,
    # but remove accidental SSML/script leftovers.
    for path in [
        WORK / "script.txt",
        WORK / "script_ssml.txt",
    ]:
        try:
            path.unlink(missing_ok=True)
        except Exception:
            pass


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 60)
    print("ACURIVO VIDEO FACTORY V7")
    print("=" * 60)

    # 1. Discover topic
    topic = discover_topic()

    # 2. Build scene-based script
    scenes = build_script(topic)

    print("\n=== SCRIPT ===")

    full_text_parts = []

    for i, scene in enumerate(scenes, start=1):
        print(f"\nSCENE {i}:")
        print(scene["text"])
        full_text_parts.append(scene["text"])

    full_text = "\n\n".join(full_text_parts)

    # Save plain text only for inspection.
    (WORK / "script.txt").write_text(
        full_text,
        encoding="utf-8"
    )

    # 3. Generate individual scene audio.
    scene_audios = generate_scene_audios(scenes)

    # 4. Concatenate and master.
    concatenate_audio(scene_audios, AUDIO_RAW)
    master_audio()

    # 5. Create topic-specific visuals.
    scene_images = []

    for i, scene in enumerate(scenes, start=1):
        image = create_scene_image(i, scene)
        scene_images.append(image)

    # 6. Render each scene according to its own narration duration.
    scene_videos = []

    for i, (image, audio) in enumerate(
        zip(scene_images, scene_audios),
        start=1
    ):
        video = render_scene(
            i,
            image,
            audio
        )

        scene_videos.append(video)

    # 7. Concatenate scenes.
    concat_video = concatenate_video(scene_videos)

    # 8. Final mux using mastered audio.
    mux_final_video(concat_video)

    # 9. Verify.
    final_duration = ffprobe_duration(VIDEO_PATH)
    final_size = VIDEO_PATH.stat().st_size / 1024 / 1024

    print("\n" + "=" * 60)
    print("ACURIVO VIDEO READY")
    print("=" * 60)
    print(f"TOPIC: {topic}")
    print(f"DURATION: {final_duration:.2f}s")
    print(f"SIZE: {final_size:.2f} MB")
    print(f"FILE: {VIDEO_PATH}")

    if final_duration < 30:
        raise RuntimeError(
            "Final video is unexpectedly short."
        )

    if final_size > 45:
        raise RuntimeError(
            f"Final video is too large: {final_size:.2f} MB"
        )

    cleanup()

    print("\nSUCCESS.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("\nFATAL ERROR:")
        print(str(e))
        sys.exit(1)