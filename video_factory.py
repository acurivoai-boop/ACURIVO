import os
import re
import json
import time
import random
import shutil
import subprocess
import requests
import edge_tts

from urllib.parse import quote
from pathlib import Path


# ============================================================
# ACURIVO VIDEO FACTORY v2
# Topic-aware visuals + exact audio duration
# ============================================================

OUTPUT_DIR = Path("output")
IMAGE_DIR = OUTPUT_DIR / "images"

VIDEO_FILE = OUTPUT_DIR / "ACURIVO_VIDEO.mp4"
REPORT_FILE = OUTPUT_DIR / "report.txt"

VOICE = "ar-SA-HamedNeural"

MAX_IMAGES = 8
MIN_SCRIPT_WORDS = 170
MAX_SCRIPT_WORDS = 320

REQUEST_TIMEOUT = 25


# ============================================================
# GENERAL HELPERS
# ============================================================

def run_command(command):
    print("\nRUN:", " ".join(command))

    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    print(result.stdout)

    if result.returncode != 0:
        raise RuntimeError(
            "Command failed:\n" + result.stdout
        )

    return result.stdout


def clean_text(text):
    if not text:
        return ""

    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def count_words(text):
    return len(re.findall(r"\S+", text))


def safe_filename(text):
    text = re.sub(r"[^\w\u0600-\u06FF -]", "", text)
    text = re.sub(r"\s+", "_", text)
    return text[:80]


# ============================================================
# TOPIC DISCOVERY
# ============================================================

BLOCKED_TERMS = [
    "vlog",
    "daily vlog",
    "my life",
    "we moved",
    "i started",
    "my business",
    "personal update",
    "family",
    "relationship",
    "wedding",
    "pregnancy",
    "house tour",
    "room tour",
    "day in my life",
    "life update"
]


SEARCH_TERMS = [
    "artificial intelligence",
    "future technology",
    "science discovery",
    "space technology",
    "robotics",
    "future of humanity",
    "medical technology",
    "energy technology",
    "interesting science",
    "technology breakthrough"
]


def is_blocked_topic(topic):
    low = topic.lower()

    for term in BLOCKED_TERMS:
        if term in low:
            return True

    return False


def search_youtube_topics():
    print("\n========================================")
    print("ACURIVO TOPIC SCOUT")
    print("========================================")

    candidates = []

    for query in SEARCH_TERMS:

        print("Searching:", query)

        try:
            result = subprocess.run(
                [
                    "yt-dlp",
                    f"ytsearch8:{query}",
                    "--flat-playlist",
                    "--print",
                    "%(title)s"
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=45
            )

            lines = [
                clean_text(x)
                for x in result.stdout.splitlines()
                if clean_text(x)
            ]

            for title in lines:

                if is_blocked_topic(title):
                    continue

                candidates.append(title)

        except Exception as e:
            print("Topic search warning:", e)

    if not candidates:
        return "مستقبل الذكاء الاصطناعي وتأثيره على حياتنا"

    # Remove duplicates
    unique = list(dict.fromkeys(candidates))

    # Randomize slightly so the channel doesn't repeat
    random.shuffle(unique)

    selected = unique[0]

    print("\nSELECTED TOPIC:")
    print(selected)

    return selected


# ============================================================
# TRANSLATION
# ============================================================

def translate_to_arabic(text):

    print("\nTRANSLATING TOPIC...")

    url = (
        "https://translate.googleapis.com/translate_a/single"
        "?client=gtx"
        "&sl=auto"
        "&tl=ar"
        "&dt=t"
        "&q=" + quote(text)
    )

    response = requests.get(
        url,
        timeout=REQUEST_TIMEOUT
    )

    response.raise_for_status()

    data = response.json()

    translated = ""

    for item in data[0]:
        if item and item[0]:
            translated += item[0]

    translated = clean_text(translated)

    if not translated:
        translated = text

    print("ARABIC TOPIC:")
    print(translated)

    return translated


# ============================================================
# SCRIPT CREATION
# ============================================================

def create_script(topic_ar):

    print("\nCREATING ARABIC SCRIPT...")

    script = f"""
هل تخيلت يومًا أن فكرة تبدو بسيطة يمكن أن تغيّر الطريقة التي نعيش بها في المستقبل؟

موضوعنا اليوم هو: {topic_ar}.

هذا الموضوع لا يتعلق فقط بما نراه اليوم، بل بما يمكن أن يحدث خلال السنوات القادمة.

عندما نتابع التطورات الحديثة، نكتشف أن العالم يتغير بسرعة كبيرة. أفكار كانت تبدو خيالية قبل سنوات أصبحت اليوم جزءًا من الواقع، وبعضها يتطور بوتيرة أسرع مما يتوقعه كثير من الناس.

الأمر المثير للاهتمام هو أن التأثير الحقيقي لا يأتي من التقنية وحدها، بل من الطريقة التي نستخدمها بها. عندما تجتمع المعرفة مع الابتكار والبيانات والقدرة على اتخاذ القرار، يمكن أن تظهر نتائج تغير قطاعات كاملة.

وهنا تظهر أهمية {topic_ar}.

فبدلًا من النظر إلى هذا الموضوع باعتباره مجرد اتجاه مؤقت، من الأفضل أن نسأل سؤالًا أكبر:

إلى أين يمكن أن يقودنا هذا التطور؟

قد نشهد خلال السنوات القادمة أدوات أكثر ذكاءً، وعمليات أسرع، واكتشافات جديدة، وربما طرقًا مختلفة تمامًا للعمل والتعلم واتخاذ القرارات.

لكن هناك جانبًا آخر مهمًا.

كل تقدم جديد يحمل معه فرصًا وتحديات في الوقت نفسه. ولذلك فإن فهم ما يحدث مبكرًا يمنح الإنسان قدرة أفضل على الاستعداد للمستقبل بدلًا من انتظار التغيير بعد حدوثه.

والأهم أن المستقبل لا يصنعه الأشخاص الذين يتوقعونه فقط، بل الأشخاص الذين يفهمون اتجاهه ويستعدون له.

لهذا السبب يستحق {topic_ar} أن نتابعه باهتمام.

فما نراه اليوم قد يكون مجرد بداية لشيء أكبر بكثير غدًا.

والسؤال الحقيقي ليس: هل سيتغير العالم؟

بل:

هل سنكون مستعدين عندما يحدث التغيير؟

تابعنا للمزيد من القصص والأفكار التي تساعدك على فهم العالم من زاوية مختلفة.
"""

    script = clean_text(script)

    words = count_words(script)

    print("SCRIPT WORDS:", words)

    if words < MIN_SCRIPT_WORDS:
        raise RuntimeError(
            f"النص قصير جدًا: {words} كلمة"
        )

    if words > MAX_SCRIPT_WORDS:
        words_list = script.split()
        script = " ".join(
            words_list[:MAX_SCRIPT_WORDS]
        )

    return script


# ============================================================
# WIKIMEDIA COMMONS IMAGE SEARCH
# ============================================================

def wikimedia_search_images(topic, limit=MAX_IMAGES):

    print("\n========================================")
    print("SEARCHING TOPIC-RELATED VISUALS")
    print("========================================")

    api = "https://commons.wikimedia.org/w/api.php"

    # Search both Arabic and English
    queries = [
        topic,
        translate_to_arabic(topic),
        " ".join(topic.split()[:5])
    ]

    found = []

    headers = {
        "User-Agent":
            "ACURIVO/2.0 educational video factory"
    }

    for query in queries:

        if len(found) >= limit:
            break

        print("Image search:", query)

        params = {
            "action": "query",
            "generator": "search",
            "gsrsearch": query,
            "gsrnamespace": 6,
            "gsrlimit": 20,
            "prop": "imageinfo",
            "iiprop": "url|mime",
            "iiurlwidth": 1280,
            "format": "json"
        }

        try:
            response = requests.get(
                api,
                params=params,
                headers=headers,
                timeout=REQUEST_TIMEOUT
            )

            response.raise_for_status()

            data = response.json()

            pages = data.get(
                "query",
                {}
            ).get(
                "pages",
                {}
            )

            for page in pages.values():

                info = page.get("imageinfo")

                if not info:
                    continue

                item = info[0]

                mime = item.get("mime", "")

                if not mime.startswith("image/"):
                    continue

                image_url = (
                    item.get("thumburl")
                    or item.get("url")
                )

                if not image_url:
                    continue

                if image_url.lower().endswith(".svg"):
                    continue

                title = page.get(
                    "title",
                    ""
                )

                found.append({
                    "url": image_url,
                    "title": title
                })

                if len(found) >= limit:
                    break

        except Exception as e:
            print(
                "Wikimedia search warning:",
                e
            )

    # Remove duplicates
    unique = []
    seen = set()

    for item in found:

        url = item["url"]

        if url in seen:
            continue

        seen.add(url)
        unique.append(item)

    print(
        "RELATED IMAGES FOUND:",
        len(unique)
    )

    return unique[:limit]


# ============================================================
# IMAGE DOWNLOAD
# ============================================================

def download_related_images(topic):

    IMAGE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    results = wikimedia_search_images(
        topic,
        MAX_IMAGES
    )

    downloaded = []

    for index, item in enumerate(results):

        filename = (
            IMAGE_DIR /
            f"topic_{index:02d}.jpg"
        )

        print(
            f"Downloading image {index + 1}/"
            f"{len(results)}"
        )

        try:

            response = requests.get(
                item["url"],
                timeout=REQUEST_TIMEOUT,
                headers={
                    "User-Agent":
                        "ACURIVO/2.0"
                }
            )

            response.raise_for_status()

            content = response.content

            if len(content) < 5000:
                continue

            with open(
                filename,
                "wb"
            ) as f:
                f.write(content)

            # Verify image using ffmpeg
            check = subprocess.run(
                [
                    "ffprobe",
                    "-v",
                    "error",
                    "-select_streams",
                    "v:0",
                    "-show_entries",
                    "stream=width,height",
                    "-of",
                    "csv=p=0",
                    str(filename)
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            if check.returncode != 0:
                filename.unlink(
                    missing_ok=True
                )
                continue

            downloaded.append(
                str(filename)
            )

        except Exception as e:
            print(
                "Image download warning:",
                e
            )

    return downloaded


# ============================================================
# FALLBACK VISUALS
# ============================================================

def download_fallback_images():

    print(
        "\nRELATED IMAGES WERE NOT ENOUGH."
    )

    print(
        "USING SAFE FALLBACK VISUALS."
    )

    downloaded = []

    IMAGE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    for i in range(MAX_IMAGES):

        filename = (
            IMAGE_DIR /
            f"fallback_{i:02d}.jpg"
        )

        try:

            url = (
                "https://picsum.photos/"
                "1280/720?random="
                + str(
                    int(time.time())
                    + i
                )
            )

            response = requests.get(
                url,
                timeout=REQUEST_TIMEOUT
            )

            response.raise_for_status()

            with open(
                filename,
                "wb"
            ) as f:
                f.write(
                    response.content
                )

            downloaded.append(
                str(filename)
            )

        except Exception as e:
            print(
                "Fallback image warning:",
                e
            )

    return downloaded


# ============================================================
# AUDIO
# ============================================================

async def create_audio_async(
    script,
    audio_file
):

    print("\nCREATING ARABIC VOICE...")

    communicate = edge_tts.Communicate(
        script,
        VOICE,
        rate="+0%",
        volume="+0%"
    )

    await communicate.save(
        str(audio_file)
    )


def create_audio(script):

    audio_file = (
        OUTPUT_DIR /
        "voice.mp3"
    )

    import asyncio

    asyncio.run(
        create_audio_async(
            script,
            audio_file
        )
    )

    return audio_file


# ============================================================
# AUDIO DURATION
# ============================================================

def get_audio_duration(audio_file):

    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(audio_file)
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(
            "تعذر قراءة مدة الصوت."
        )

    duration = float(
        result.stdout.strip()
    )

    if duration <= 0:
        raise RuntimeError(
            "مدة الصوت غير صحيحة."
        )

    print(
        f"\nAUDIO DURATION: "
        f"{duration:.2f} seconds"
    )

    return duration


# ============================================================
# IMAGE PREPARATION
# ============================================================

def normalize_images(images):

    normalized = []

    for index, image in enumerate(images):

        output = (
            IMAGE_DIR /
            f"normalized_{index:02d}.jpg"
        )

        run_command([
            "ffmpeg",
            "-y",
            "-i",
            image,
            "-vf",
            (
                "scale=1280:720:"
                "force_original_aspect_ratio=increase,"
                "crop=1280:720"
            ),
            "-q:v",
            "3",
            str(output)
        ])

        normalized.append(
            str(output)
        )

    return normalized


# ============================================================
# VIDEO CREATION
# ============================================================

def create_video(images, audio_file, duration):

    print("\n========================================")
    print("CREATING FULL-LENGTH VIDEO")
    print("========================================")

    if not images:
        raise RuntimeError(
            "لا توجد صور لإنشاء الفيديو."
        )

    # Exactly enough time for the full audio.
    image_duration = duration / len(images)

    print(
        f"IMAGES: {len(images)}"
    )

    print(
        f"SECONDS PER IMAGE: "
        f"{image_duration:.2f}"
    )

    concat_file = (
        OUTPUT_DIR /
        "images.txt"
    )

    with open(
        concat_file,
        "w",
        encoding="utf-8"
    ) as f:

        for image in images:

            f.write(
                f"file '{Path(image).resolve()}'\n"
            )

            f.write(
                f"duration {image_duration:.6f}\n"
            )

        # Required by concat demuxer
        f.write(
            f"file '{Path(images[-1]).resolve()}'\n"
        )

    # Small safety margin prevents audio truncation
    final_duration = duration + 0.20

    run_command([
        "ffmpeg",
        "-y",

        "-f",
        "concat",

        "-safe",
        "0",

        "-i",
        str(concat_file),

        "-i",
        str(audio_file),

        "-vf",
        "format=yuv420p",

        "-c:v",
        "libx264",

        "-preset",
        "veryfast",

        "-crf",
        "23",

        "-c:a",
        "aac",

        "-b:a",
        "128k",

        "-t",
        f"{final_duration:.3f}",

        "-movflags",
        "+faststart",

        str(VIDEO_FILE)
    ])

    # Final verification
    verify_video_duration()

    return VIDEO_FILE


# ============================================================
# FINAL VIDEO VERIFICATION
# ============================================================

def get_video_duration():

    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(VIDEO_FILE)
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(
            "تعذر قراءة مدة الفيديو."
        )

    return float(
        result.stdout.strip()
    )


def verify_video_duration():

    video_duration = get_video_duration()

    audio_duration = get_audio_duration(
        OUTPUT_DIR / "voice.mp3"
    )

    difference = (
        video_duration -
        audio_duration
    )

    print("\n========================================")
    print("FINAL DURATION CHECK")
    print("========================================")

    print(
        f"AUDIO : {audio_duration:.2f}s"
    )

    print(
        f"VIDEO : {video_duration:.2f}s"
    )

    print(
        f"DIFFERENCE : {difference:.2f}s"
    )

    # Video must NEVER be shorter than audio.
    if video_duration + 0.05 < audio_duration:
        raise RuntimeError(
            "ERROR: الفيديو أقصر من الصوت."
        )

    print(
        "DURATION CHECK: PASS"
    )


# ============================================================
# REPORT
# ============================================================

def create_report(
    topic,
    topic_ar,
    script,
    audio_duration,
    video_duration,
    image_count
):

    with open(
        REPORT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            "ACURIVO VIDEO FACTORY REPORT\n"
        )

        f.write(
            "================================\n\n"
        )

        f.write(
            f"Original topic:\n{topic}\n\n"
        )

        f.write(
            f"Arabic topic:\n{topic_ar}\n\n"
        )

        f.write(
            f"Script words: "
            f"{count_words(script)}\n"
        )

        f.write(
            f"Audio duration: "
            f"{audio_duration:.2f} seconds\n"
        )

        f.write(
            f"Video duration: "
            f"{video_duration:.2f} seconds\n"
        )

        f.write(
            f"Images used: "
            f"{image_count}\n"
        )

        f.write(
            "\nDURATION CHECK: PASS\n"
        )


# ============================================================
# CLEANUP
# ============================================================

def cleanup_old_files():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    if IMAGE_DIR.exists():
        shutil.rmtree(
            IMAGE_DIR
        )

    for filename in [
        VIDEO_FILE,
        REPORT_FILE,
        OUTPUT_DIR / "voice.mp3",
        OUTPUT_DIR / "images.txt"
    ]:
        if filename.exists():
            filename.unlink()


# ============================================================
# MAIN FACTORY
# ============================================================

def main():

    print(
        "\n"
        "====================================================\n"
        "        ACURIVO VIDEO FACTORY v2\n"
        "  TOPIC-AWARE VISUALS + EXACT AUDIO TIMING\n"
        "====================================================\n"
    )

    cleanup_old_files()

    # --------------------------------------------------------
    # 1. Find topic
    # --------------------------------------------------------

    topic = search_youtube_topics()

    # --------------------------------------------------------
    # 2. Arabic topic
    # --------------------------------------------------------

    topic_ar = translate_to_arabic(
        topic
    )

    # --------------------------------------------------------
    # 3. Create complete script
    # --------------------------------------------------------

    script = create_script(
        topic_ar
    )

    # --------------------------------------------------------
    # 4. Create voice first
    # --------------------------------------------------------

    audio_file = create_audio(
        script
    )

    # --------------------------------------------------------
    # 5. Get exact audio duration
    # --------------------------------------------------------

    audio_duration = get_audio_duration(
        audio_file
    )

    # --------------------------------------------------------
    # 6. Search topic-related images
    # --------------------------------------------------------

    images = download_related_images(
        topic
    )

    # --------------------------------------------------------
    # 7. Fallback if necessary
    # --------------------------------------------------------

    if len(images) < 4:

        extra = download_fallback_images()

        images.extend(
            extra
        )

    if not images:
        raise RuntimeError(
            "لم يتم العثور على أي صور."
        )

    images = images[:MAX_IMAGES]

    # --------------------------------------------------------
    # 8. Normalize images
    # --------------------------------------------------------

    normalized = normalize_images(
        images
    )

    # --------------------------------------------------------
    # 9. Build video to exact audio duration
    # --------------------------------------------------------

    video = create_video(
        normalized,
        audio_file,
        audio_duration
    )

    # --------------------------------------------------------
    # 10. Final duration
    # --------------------------------------------------------

    video_duration = get_video_duration()

    # --------------------------------------------------------
    # 11. Report
    # --------------------------------------------------------

    create_report(
        topic,
        topic_ar,
        script,
        audio_duration,
        video_duration,
        len(normalized)
    )

    print(
        "\n"
        "====================================================\n"
        "             ACURIVO BUILD COMPLETE\n"
        "====================================================\n"
    )

    print(
        "VIDEO:",
        video
    )

    print(
        f"AUDIO DURATION: "
        f"{audio_duration:.2f}s"
    )

    print(
        f"VIDEO DURATION: "
        f"{video_duration:.2f}s"
    )

    print(
        "VISUALS:",
        len(normalized)
    )

    print(
        "STATUS: SUCCESS"
    )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":
    main()