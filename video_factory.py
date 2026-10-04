import os
import re
import json
import time
import random
import shutil
import subprocess
import requests
import edge_tts
import asyncio

from urllib.parse import quote
from pathlib import Path


# ============================================================
# ACURIVO VIDEO FACTORY V3
# Natural Arabic Voice + Smooth Topic-Related Visuals
# ============================================================

OUTPUT_DIR = Path("output")
IMAGE_DIR = OUTPUT_DIR / "images"

VIDEO_FILE = OUTPUT_DIR / "ACURIVO_VIDEO.mp4"
REPORT_FILE = OUTPUT_DIR / "report.txt"

VOICE = "ar-SA-HamedNeural"

MAX_IMAGES = 8
MIN_IMAGES = 5

MIN_SCRIPT_WORDS = 190
MAX_SCRIPT_WORDS = 330

REQUEST_TIMEOUT = 25


# ============================================================
# TOPIC SETTINGS
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
    "science breakthrough",
    "technology breakthrough"
]


# ============================================================
# HELPERS
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

    text = re.sub(
        r"https?://\S+",
        "",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def count_words(text):

    return len(
        re.findall(
            r"\S+",
            text
        )
    )


def is_blocked_topic(topic):

    low = topic.lower()

    for term in BLOCKED_TERMS:

        if term in low:
            return True

    return False


# ============================================================
# TOPIC DISCOVERY
# ============================================================

def search_youtube_topics():

    print("\n========================================")
    print("ACURIVO TOPIC SCOUT")
    print("========================================")

    candidates = []

    for query in SEARCH_TERMS:

        print(
            "Searching:",
            query
        )

        try:

            result = subprocess.run(
                [
                    "yt-dlp",
                    f"ytsearch10:{query}",
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

            print(
                "Topic search warning:",
                e
            )

    if not candidates:

        return (
            "مستقبل الذكاء الاصطناعي "
            "وتأثيره على حياتنا"
        )

    unique = list(
        dict.fromkeys(candidates)
    )

    random.shuffle(unique)

    selected = unique[0]

    print(
        "\nSELECTED TOPIC:"
    )

    print(selected)

    return selected


# ============================================================
# TRANSLATION
# ============================================================

def translate_to_arabic(text):

    print(
        "\nTRANSLATING TOPIC..."
    )

    url = (
        "https://translate.googleapis.com/"
        "translate_a/single"
        "?client=gtx"
        "&sl=auto"
        "&tl=ar"
        "&dt=t"
        "&q="
        + quote(text)
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

    translated = clean_text(
        translated
    )

    if not translated:

        translated = text

    print(
        "ARABIC TOPIC:"
    )

    print(translated)

    return translated


# ============================================================
# NATURAL ARABIC SCRIPT
# ============================================================

def create_script(topic_ar):

    print(
        "\nCREATING NATURAL ARABIC SCRIPT..."
    )

    script = f"""
هل يمكن أن يغيّر {topic_ar} الطريقة التي نعيش بها في المستقبل؟

ربما يبدو هذا السؤال بسيطًا، لكن الإجابة قد تكون أكبر بكثير مما نتوقع.

في السنوات الأخيرة، بدأ العالم يشهد تطورات متسارعة في مجالات مختلفة. وما كان يبدو قبل فترة قصيرة مجرد فكرة بعيدة، أصبح اليوم واقعًا نراه أمامنا.

ومن هنا تأتي أهمية {topic_ar}.

فالموضوع لا يتعلق بتطور واحد فقط، وإنما بمجموعة من التغيّرات التي يمكن أن تؤثر في طريقة عملنا، وتعلّمنا، واتخاذنا للقرارات.

واللافت أن سرعة هذا التغيير أصبحت أكبر من أي وقت مضى.

كلما ظهرت تقنية جديدة، بدأت تطبيقاتها بالانتشار في مجالات أخرى. وبعد فترة قصيرة، تتحول الفكرة من تجربة محدودة إلى أداة يمكن أن يستخدمها الملايين.

لكن هناك سؤالًا مهمًا.

ماذا يعني ذلك بالنسبة للمستقبل؟

إذا استمر هذا التطور بالسرعة نفسها، فقد نشهد خلال السنوات القادمة تغيّرات كبيرة في كثير من المجالات.

قد تصبح بعض المهام أسرع وأكثر دقة.

وقد تظهر وظائف جديدة لم تكن موجودة من قبل.

وقد تتغير الطريقة التي نتعامل بها مع المعلومات، والأجهزة، وحتى مع القرارات اليومية.

ومع ذلك، لا يعني التقدم أن كل شيء سيكون أسهل.

فكل تقنية جديدة تحمل معها فرصًا، وفي الوقت نفسه تفرض تحديات جديدة.

ولهذا فإن فهم الاتجاه الذي يسير فيه العالم أصبح أكثر أهمية من مجرد متابعة الأخبار.

الشخص الذي يفهم التغيير مبكرًا، يستطيع أن يستعد له.

والشركات التي تراقب هذه التحولات، تستطيع أن تبحث عن الفرص قبل أن تصبح واضحة للجميع.

أما السؤال الأهم، فهو إلى أين يمكن أن يصل هذا التطور؟

من الصعب معرفة المستقبل بدقة.

لكن شيئًا واحدًا يبدو واضحًا.

العالم يتغير بسرعة.

وما نراه اليوم قد يكون مجرد البداية.

لذلك، فإن متابعة {topic_ar} ليست مجرد متابعة لخبر جديد.

إنها محاولة لفهم ما يمكن أن يحدث غدًا.

فالمستقبل لا يصل فجأة.

إنه يبدأ بأفكار صغيرة، ثم تتطور هذه الأفكار، وتصبح تقنيات، ثم تتحول إلى واقع.

وربما يكون الشيء الذي نراه اليوم مجرد أول خطوة في تغيير أكبر بكثير.

السؤال إذن ليس: هل سيتغير العالم؟

بل:

هل سنكون مستعدين عندما يتغير؟

تابعنا للمزيد من القصص والأفكار التي تساعدك على فهم العالم من زاوية مختلفة.
"""

    # --------------------------------------------------------
    # تحسين النطق العربي
    # --------------------------------------------------------

    replacements = {

        "الذكاء الاصطناعي":
            "الذَّكاء الاصطناعي",

        "التكنولوجيا":
            "التِّكنولوجيا",

        "التقنية":
            "التِّقنية",

        "المعلومات":
            "المَعلومات",

        "المستقبل":
            "المُستقبل",

        "التطور":
            "التَّطوُّر",

        "التغييرات":
            "التَّغيُّرات",

        "التغيير":
            "التَّغيير",

        "القرارات":
            "القَرارات",

        "المجالات":
            "المَجالات",

        "السنوات":
            "السَّنوات",

        "الملايين":
            "المَلايين",

        "الشركات":
            "الشَّركات",

        "الفرص":
            "الفُرَص",

        "التحديات":
            "التَّحدِّيات"
    }

    for old, new in replacements.items():

        script = script.replace(
            old,
            new
        )

    # --------------------------------------------------------
    # تحسين التنفس والإيقاع
    # --------------------------------------------------------

    script = script.replace(
        "،",
        "، "
    )

    script = script.replace(
        ".",
        ". "
    )

    script = script.replace(
        "؟",
        "؟ "
    )

    script = re.sub(
        r"\s+",
        " ",
        script
    )

    script = clean_text(
        script
    )

    words = count_words(
        script
    )

    print(
        "SCRIPT WORDS:",
        words
    )

    if words < MIN_SCRIPT_WORDS:

        raise RuntimeError(
            "النص قصير جدًا: "
            + str(words)
        )

    if words > MAX_SCRIPT_WORDS:

        script = " ".join(
            script.split()
            [:MAX_SCRIPT_WORDS]
        )

    return script


# ============================================================
# WIKIMEDIA VISUAL SEARCH
# ============================================================

def wikimedia_search_images(
    topic,
    limit=MAX_IMAGES
):

    print(
        "\n========================================"
    )

    print(
        "SEARCHING TOPIC-RELATED VISUALS"
    )

    print(
        "========================================"
    )

    api = (
        "https://commons.wikimedia.org/"
        "w/api.php"
    )

    queries = [
        topic,
        " ".join(
            topic.split()[:6]
        )
    ]

    found = []

    headers = {
        "User-Agent":
            "ACURIVO/3.0 educational video factory"
    }

    for query in queries:

        if len(found) >= limit:
            break

        print(
            "Visual query:",
            query
        )

        params = {

            "action":
                "query",

            "generator":
                "search",

            "gsrsearch":
                query,

            "gsrnamespace":
                6,

            "gsrlimit":
                30,

            "prop":
                "imageinfo",

            "iiprop":
                "url|mime",

            "iiurlwidth":
                1280,

            "format":
                "json"
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

            pages = (
                data
                .get("query", {})
                .get("pages", {})
            )

            for page in pages.values():

                info = page.get(
                    "imageinfo"
                )

                if not info:
                    continue

                item = info[0]

                mime = item.get(
                    "mime",
                    ""
                )

                if not mime.startswith(
                    "image/"
                ):
                    continue

                image_url = (
                    item.get(
                        "thumburl"
                    )
                    or
                    item.get(
                        "url"
                    )
                )

                if not image_url:
                    continue

                if image_url.lower().endswith(
                    ".svg"
                ):
                    continue

                title = page.get(
                    "title",
                    ""
                )

                found.append({

                    "url":
                        image_url,

                    "title":
                        title
                })

                if len(found) >= limit:
                    break

        except Exception as e:

            print(
                "Visual search warning:",
                e
            )

    unique = []

    seen = set()

    for item in found:

        url = item["url"]

        if url in seen:
            continue

        seen.add(url)

        unique.append(
            item
        )

    print(
        "RELATED VISUALS FOUND:",
        len(unique)
    )

    return unique[:limit]


# ============================================================
# DOWNLOAD IMAGES
# ============================================================

def download_related_images(topic):

    IMAGE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    results = (
        wikimedia_search_images(
            topic
        )
    )

    downloaded = []

    for index, item in enumerate(
        results
    ):

        filename = (
            IMAGE_DIR /
            f"topic_{index:02d}.jpg"
        )

        print(
            f"Downloading visual "
            f"{index + 1}/"
            f"{len(results)}"
        )

        try:

            response = requests.get(
                item["url"],
                timeout=REQUEST_TIMEOUT,
                headers={
                    "User-Agent":
                        "ACURIVO/3.0"
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

                f.write(
                    content
                )

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
# FALLBACK
# ============================================================

def download_fallback_images():

    print(
        "\nUSING FALLBACK VISUALS."
    )

    downloaded = []

    IMAGE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    for i in range(
        MAX_IMAGES
    ):

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
                "Fallback warning:",
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

    print(
        "\nCREATING NATURAL ARABIC VOICE..."
    )

    communicate = edge_tts.Communicate(
        script,
        VOICE,
        rate="-4%",
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

def get_audio_duration(
    audio_file
):

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
# IMAGE NORMALIZATION
# ============================================================

def normalize_images(images):

    normalized = []

    for index, image in enumerate(
        images
    ):

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
                "force_original_aspect_ratio="
                "increase,"
                "crop=1280:720,"
                "setsar=1"
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
# SMOOTH VIDEO
# ============================================================

def create_video(
    images,
    audio_file,
    duration
):

    print(
        "\n========================================"
    )

    print(
        "CREATING SMOOTH FULL-LENGTH VIDEO"
    )

    print(
        "========================================"
    )

    if not images:

        raise RuntimeError(
            "لا توجد صور لإنشاء الفيديو."
        )

    image_duration = (
        duration /
        len(images)
    )

    print(
        "IMAGES:",
        len(images)
    )

    print(
        "SECONDS PER IMAGE:",
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
                "file '"
                + str(
                    Path(image)
                    .resolve()
                )
                + "'\n"
            )

            f.write(
                "duration "
                + f"{image_duration:.6f}"
                + "\n"
            )

        f.write(
            "file '"
            + str(
                Path(images[-1])
                .resolve()
            )
            + "'\n"
        )

    final_duration = (
        duration + 0.30
    )

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
        (
            "format=yuv420p,"
            "fps=30"
        ),

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

        "-shortest",

        "-movflags",
        "+faststart",

        str(VIDEO_FILE)
    ])

    verify_video_duration()

    return VIDEO_FILE


# ============================================================
# VIDEO DURATION CHECK
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

    video_duration = (
        get_video_duration()
    )

    audio_duration = (
        get_audio_duration(
            OUTPUT_DIR /
            "voice.mp3"
        )
    )

    difference = (
        video_duration -
        audio_duration
    )

    print(
        "\n========================================"
    )

    print(
        "FINAL DURATION CHECK"
    )

    print(
        "========================================"
    )

    print(
        f"AUDIO : "
        f"{audio_duration:.2f}s"
    )

    print(
        f"VIDEO : "
        f"{video_duration:.2f}s"
    )

    print(
        f"DIFFERENCE : "
        f"{difference:.2f}s"
    )

    if (
        video_duration + 0.05
        < audio_duration
    ):

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
            "ACURIVO VIDEO FACTORY V3\n"
        )

        f.write(
            "================================\n\n"
        )

        f.write(
            "Original topic:\n"
        )

        f.write(
            topic + "\n\n"
        )

        f.write(
            "Arabic topic:\n"
        )

        f.write(
            topic_ar + "\n\n"
        )

        f.write(
            "Script words: "
            + str(
                count_words(script)
            )
            + "\n"
        )

        f.write(
            "Audio duration: "
            + f"{audio_duration:.2f}"
            + " seconds\n"
        )

        f.write(
            "Video duration: "
            + f"{video_duration:.2f}"
            + " seconds\n"
        )

        f.write(
            "Images used: "
            + str(image_count)
            + "\n"
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

        OUTPUT_DIR /
        "voice.mp3",

        OUTPUT_DIR /
        "images.txt"
    ]:

        if filename.exists():

            filename.unlink()


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "\n"
        "====================================================\n"
        "        ACURIVO VIDEO FACTORY V3\n"
        "  NATURAL ARABIC + SMOOTH RELATED VISUALS\n"
        "====================================================\n"
    )

    cleanup_old_files()

    # 1. Topic
    topic = (
        search_youtube_topics()
    )

    # 2. Arabic topic
    topic_ar = (
        translate_to_arabic(
            topic
        )
    )

    # 3. Natural script
    script = (
        create_script(
            topic_ar
        )
    )

    # 4. Voice
    audio_file = (
        create_audio(
            script
        )
    )

    # 5. Exact duration
    audio_duration = (
        get_audio_duration(
            audio_file
        )
    )

    # 6. Related visuals
    images = (
        download_related_images(
            topic
        )
    )

    # 7. Fallback only if needed
    if len(images) < MIN_IMAGES:

        extra = (
            download_fallback_images()
        )

        images.extend(
            extra
        )

    if not images:

        raise RuntimeError(
            "لم يتم العثور على صور."
        )

    images = images[
        :MAX_IMAGES
    ]

    # 8. Normalize
    normalized = (
        normalize_images(
            images
        )
    )

    # 9. Full video
    video = (
        create_video(
            normalized,
            audio_file,
            audio_duration
        )
    )

    # 10. Final duration
    video_duration = (
        get_video_duration()
    )

    # 11. Report
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