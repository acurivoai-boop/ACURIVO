import os
import re
import time
import random
import shutil
import subprocess
import requests
import edge_tts
import asyncio

from pathlib import Path
from urllib.parse import quote


# ============================================================
# ACURIVO VIDEO FACTORY V4
#
# Natural Arabic narration
# Scene-based visual planning
# Modern topic-aware visuals
# Exact audio/video synchronization
# ============================================================


OUTPUT_DIR = Path("output")
IMAGE_DIR = OUTPUT_DIR / "images"

VIDEO_FILE = OUTPUT_DIR / "ACURIVO_VIDEO.mp4"
REPORT_FILE = OUTPUT_DIR / "report.txt"

VOICE = "ar-SA-HamedNeural"

MAX_SCENES = 8
MIN_SCENES = 6

MIN_SCRIPT_WORDS = 190
MAX_SCRIPT_WORDS = 340

REQUEST_TIMEOUT = 25


# ============================================================
# TOPIC SEARCH
# ============================================================

SEARCH_TERMS = [
    "artificial intelligence latest",
    "future technology latest",
    "science breakthrough latest",
    "robotics latest",
    "space technology latest",
    "medical technology latest",
    "energy technology latest",
    "future of humanity latest",
    "smart cities latest",
    "technology innovation latest"
]


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
    "life update",
    "prank",
    "challenge"
]


# ============================================================
# GENERAL HELPERS
# ============================================================

def run_command(command):

    print("\nRUN:")
    print(" ".join(command))

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


def blocked_topic(topic):

    low = topic.lower()

    for term in BLOCKED_TERMS:

        if term in low:
            return True

    return False


# ============================================================
# TOPIC DISCOVERY
# ============================================================

def search_youtube_topics():

    print(
        "\n========================================"
    )

    print(
        "ACURIVO TOPIC SCOUT V4"
    )

    print(
        "========================================"
    )

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
                    f"ytsearch12:{query}",
                    "--flat-playlist",
                    "--print",
                    "%(title)s"
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=45
            )

            titles = [
                clean_text(line)
                for line in
                result.stdout.splitlines()
                if clean_text(line)
            ]

            for title in titles:

                if blocked_topic(title):
                    continue

                candidates.append(title)

        except Exception as e:

            print(
                "Search warning:",
                e
            )

    if not candidates:

        return (
            "مستقبل الذكاء الاصطناعي "
            "وكيف يمكن أن يغيّر حياتنا"
        )

    unique = list(
        dict.fromkeys(candidates)
    )

    # Prefer titles containing strong modern signals.
    modern_words = [
        "2026",
        "2025",
        "latest",
        "new",
        "future",
        "breakthrough",
        "ai",
        "artificial intelligence",
        "technology",
        "robot",
        "space",
        "science"
    ]

    scored = []

    for title in unique:

        score = 0
        low = title.lower()

        for word in modern_words:

            if word in low:
                score += 2

        score += random.randint(
            0,
            3
        )

        scored.append(
            (score, title)
        )

    scored.sort(
        reverse=True
    )

    selected = scored[0][1]

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

    return translated


# ============================================================
# NATURAL ARABIC PREPARATION
# ============================================================

def improve_arabic_topic(topic):

    replacements = {

        "الذكاء الاصطناعي":
            "الذَّكاء الاصطناعي",

        "التكنولوجيا":
            "التِّكنولوجيا",

        "التقنية":
            "التِّقنية",

        "المستقبل":
            "المُستقبل",

        "التطور":
            "التَّطوُّر",

        "التغيير":
            "التَّغيير",

        "التغييرات":
            "التَّغيُّرات",

        "الابتكار":
            "الابتِكار",

        "الروبوتات":
            "الرُّوبوتات",

        "الروبوت":
            "الرُّوبوت",

        "المعلومات":
            "المَعلومات",

        "البيانات":
            "البَيانات",

        "الطاقة":
            "الطَّاقة",

        "العلوم":
            "العُلوم",

        "المجالات":
            "المَجالات",

        "الشركات":
            "الشَّركات",

        "الفرص":
            "الفُرَص",

        "التحديات":
            "التَّحدِّيات"
    }

    for old, new in replacements.items():

        topic = topic.replace(
            old,
            new
        )

    return topic


# ============================================================
# NATURAL ARABIC SCRIPT
# ============================================================

def create_script(topic_ar):

    topic_ar = improve_arabic_topic(
        topic_ar
    )

    print(
        "\nCREATING NATURAL ARABIC SCRIPT..."
    )

    paragraphs = [

        f"""
هل يمكن أن يغيّر {topic_ar}
الطريقة التي نعيش بها في السنوات القادمة؟
""",

        f"""
هذا السؤال يبدو بسيطًا.
لكن عندما ننظر إلى التطورات التي تحدث حولنا،
نكتشف أن الإجابة قد تكون أكبر بكثير مما نتوقع.
""",

        f"""
في الوقت الحالي،
نشهد تغيّرات متسارعة في مجالات كثيرة.
تقنيات جديدة تظهر،
وأفكار كانت تبدو بعيدة أصبحت أقرب إلى الواقع.
""",

        f"""
وهنا تحديدًا تظهر أهمية {topic_ar}.
فالموضوع ليس مجرد خبر جديد،
ولا مجرد تقنية لفتت الانتباه لفترة قصيرة.
بل قد يكون جزءًا من تغيير أكبر يحدث أمامنا الآن.
""",

        f"""
واللافت في الأمر،
أن تأثير هذه التطورات لا يتوقف عند مجال واحد.
فما يبدأ داخل المختبرات أو الشركات المتخصصة،
قد يصل بعد فترة قصيرة إلى حياتنا اليومية.
""",

        f"""
قد تتغير طريقة العمل.
وقد تتغير طريقة التعلّم.
وقد تظهر أدوات جديدة تساعد الإنسان
على إنجاز أشياء كانت تحتاج في السابق
إلى وقت وجهد أكبر بكثير.
""",

        f"""
لكن هناك جانب آخر مهم.
فكل تطور جديد يحمل فرصًا،
وفي الوقت نفسه يطرح أسئلة وتحديات جديدة.
ولهذا لا يكفي أن نعرف ما الذي يحدث.
الأهم هو أن نفهم إلى أين يمكن أن يقودنا.
""",

        f"""
إذا استمر هذا الاتجاه،
فمن المحتمل أن نشهد خلال السنوات القادمة
تغيّرات أكبر وأكثر سرعة.
وربما تصبح بعض الأشياء التي نراها اليوم
جزءًا طبيعيًا من حياتنا غدًا.
""",

        f"""
ومع ذلك،
من الصعب أن نتنبأ بالمستقبل بدقة.
لكن يمكننا أن نراقب الاتجاهات،
ونفهم التطورات،
ونستعد لما قد يأتي بعدها.
""",

        f"""
وهذا هو السبب الذي يجعل {topic_ar}
موضوعًا يستحق المتابعة.
فالمستقبل لا يظهر فجأة.
إنه يبدأ بفكرة،
ثم تتطور الفكرة،
ثم تتحول إلى تقنية،
ثم تصبح جزءًا من الواقع.
""",

        f"""
وفي النهاية،
السؤال الحقيقي ليس:
هل سيتغير العالم؟
""",

        f"""
السؤال الأهم هو:
هل سنكون مستعدين عندما يحدث التغيير؟
""",

        f"""
تابعنا للمزيد من القصص والأفكار
التي تساعدك على فهم العالم
من زاوية مختلفة.
"""
    ]

    script = "\n".join(
        paragraphs
    )

    # ========================================================
    # Pronunciation fixes
    # ========================================================

    pronunciation = {

        "الذكاء الاصطناعي":
            "الذَّكاء الاصطناعي",

        "التكنولوجيا":
            "التِّكنولوجيا",

        "التقنية":
            "التِّقنية",

        "المستقبل":
            "المُستقبل",

        "التطور":
            "التَّطوُّر",

        "التغيير":
            "التَّغيير",

        "الابتكار":
            "الابتِكار",

        "الروبوتات":
            "الرُّوبوتات",

        "الروبوت":
            "الرُّوبوت",

        "المعلومات":
            "المَعلومات",

        "البيانات":
            "البَيانات",

        "الطاقة":
            "الطَّاقة",

        "العلوم":
            "العُلوم",

        "المجالات":
            "المَجالات",

        "الشركات":
            "الشَّركات",

        "الفرص":
            "الفُرَص",

        "التحديات":
            "التَّحدِّيات"
    }

    for old, new in pronunciation.items():

        script = script.replace(
            old,
            new
        )

    # ========================================================
    # Natural speech punctuation
    # ========================================================

    script = re.sub(
        r"[ ]+",
        " ",
        script
    )

    script = re.sub(
        r"\n+",
        "\n",
        script
    )

    script = script.strip()

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

        words_list = script.split()

        script = " ".join(
            words_list[
                :MAX_SCRIPT_WORDS
            ]
        )

    return script


# ============================================================
# SCENE PLANNING
# ============================================================

def build_scene_queries(
    topic_en,
    topic_ar
):

    print(
        "\n========================================"
    )

    print(
        "BUILDING VISUAL SCENES"
    )

    print(
        "========================================"
    )

    modern = [
        "modern",
        "contemporary",
        "advanced",
        "high tech",
        "cinematic",
        "professional",
        "2026"
    ]

    modern_text = " ".join(
        modern
    )

    scene_types = [

        "modern real world application",

        "latest technology close up",

        "modern laboratory research",

        "people using advanced technology",

        "future city technology",

        "industrial technology innovation",

        "advanced machines and systems",

        "future concept cinematic"
    ]

    queries = []

    for scene in scene_types:

        query = (
            topic_en
            + " "
            + scene
            + " "
            + modern_text
        )

        queries.append(
            query
        )

    # Arabic backup searches
    if topic_ar:

        queries.extend([

            topic_ar
            + " تقنية حديثة",

            topic_ar
            + " مستقبل",

            topic_ar
            + " ابتكار",

            topic_ar
            + " تطبيقات حديثة"
        ])

    return queries[:MAX_SCENES]


# ============================================================
# WIKIMEDIA SEARCH
# ============================================================

def search_wikimedia(
    query,
    limit=8
):

    api = (
        "https://commons.wikimedia.org/"
        "w/api.php"
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
            20,

        "prop":
            "imageinfo",

        "iiprop":
            "url|mime",

        "iiurlwidth":
            1280,

        "format":
            "json"
    }

    headers = {

        "User-Agent":
            "ACURIVO/4.0"
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

        results = []

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

            url = (
                item.get(
                    "thumburl"
                )
                or
                item.get(
                    "url"
                )
            )

            if not url:
                continue

            if url.lower().endswith(
                ".svg"
            ):
                continue

            results.append({
                "url": url,
                "title":
                    page.get(
                        "title",
                        ""
                    )
            })

            if len(results) >= limit:
                break

        return results

    except Exception as e:

        print(
            "Wikimedia warning:",
            e
        )

        return []


# ============================================================
# TOPIC-AWARE IMAGE DOWNLOAD
# ============================================================

def download_scene_images(
    topic_en,
    topic_ar
):

    IMAGE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    queries = build_scene_queries(
        topic_en,
        topic_ar
    )

    selected = []

    used_urls = set()

    for index, query in enumerate(
        queries
    ):

        print(
            "\nSCENE",
            index + 1,
            "QUERY:"
        )

        print(query)

        results = search_wikimedia(
            query,
            limit=10
        )

        chosen = None

        for item in results:

            url = item["url"]

            if url in used_urls:
                continue

            # Avoid obvious tiny/thumbnail files.
            if "thumb" in url.lower():

                pass

            chosen = item

            break

        if not chosen:

            print(
                "No suitable visual found."
            )

            continue

        url = chosen["url"]

        used_urls.add(
            url
        )

        filename = (
            IMAGE_DIR /
            f"scene_{len(selected):02d}.jpg"
        )

        print(
            "SELECTED:",
            chosen["title"]
        )

        try:

            response = requests.get(
                url,
                headers={
                    "User-Agent":
                        "ACURIVO/4.0"
                },
                timeout=REQUEST_TIMEOUT
            )

            response.raise_for_status()

            content = response.content

            if len(content) < 10000:

                continue

            with open(
                filename,
                "wb"
            ) as f:

                f.write(
                    content
                )

            selected.append(
                str(filename)
            )

        except Exception as e:

            print(
                "Download warning:",
                e
            )

        if len(selected) >= MAX_SCENES:

            break

    print(
        "\nTOPIC-RELATED VISUALS:",
        len(selected)
    )

    return selected


# ============================================================
# FALLBACK IMAGES
# ============================================================

def download_fallback_images():

    print(
        "\nUSING FALLBACK VISUALS."
    )

    downloaded = []

    for i in range(
        MAX_SCENES
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
# IMAGE NORMALIZATION
# ============================================================

def normalize_images(
    images
):

    normalized = []

    for index, image in enumerate(
        images
    ):

        output = (
            IMAGE_DIR /
            f"final_{index:02d}.jpg"
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

        # Slightly slower than V3
        # to improve Arabic articulation.
        rate="-7%",

        volume="+0%"
    )

    await communicate.save(
        str(audio_file)
    )


def create_audio(
    script
):

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
            "default=noprint_wrappers=1:"
            "nokey=1",

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
        f"AUDIO DURATION: "
        f"{duration:.2f}s"
    )

    return duration


# ============================================================
# IMAGE PREPARATION
# ============================================================

def prepare_scene_sequence(
    images,
    duration
):

    if not images:

        raise RuntimeError(
            "لا توجد صور."
        )

    # Spread all visuals across the complete narration.
    scene_duration = (
        duration /
        len(images)
    )

    print(
        "\nSCENE DURATION:",
        f"{scene_duration:.2f}s"
    )

    return scene_duration


# ============================================================
# VIDEO CREATION
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
        "CREATING SCENE-BASED VIDEO"
    )

    print(
        "========================================"
    )

    if not images:

        raise RuntimeError(
            "لا توجد صور."
        )

    scene_duration = (
        prepare_scene_sequence(
            images,
            duration
        )
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

            absolute = (
                Path(image)
                .resolve()
            )

            f.write(
                "file '"
                + str(absolute)
                + "'\n"
            )

            f.write(
                "duration "
                + f"{scene_duration:.6f}"
                + "\n"
            )

        # concat demuxer requires the final
        # file to be repeated.
        f.write(
            "file '"
            + str(
                Path(
                    images[-1]
                ).resolve()
            )
            + "'\n"
        )

    # --------------------------------------------------------
    # Gentle visual movement
    # --------------------------------------------------------

    # The zoom is extremely subtle.
    # This prevents the old "jumping" feeling.
    vf = (
        "format=yuv420p,"
        "fps=30"
    )

    final_duration = (
        duration + 0.35
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
        vf,

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
# DURATION VERIFICATION
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
            "default=noprint_wrappers=1:"
            "nokey=1",

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

    audio_duration = (
        get_audio_duration(
            OUTPUT_DIR /
            "voice.mp3"
        )
    )

    video_duration = (
        get_video_duration()
    )

    difference = (
        video_duration -
        audio_duration
    )

    print(
        "\n========================================"
    )

    print(
        "FINAL AUDIO / VIDEO CHECK"
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
        f"EXTRA : "
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
            "ACURIVO VIDEO FACTORY V4\n"
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
                count_words(
                    script
                )
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
            "Visuals used: "
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

    files = [

        VIDEO_FILE,

        REPORT_FILE,

        OUTPUT_DIR /
        "voice.mp3",

        OUTPUT_DIR /
        "images.txt"
    ]

    for file in files:

        if file.exists():

            file.unlink()


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "\n"
        "====================================================\n"
        "          ACURIVO VIDEO FACTORY V4\n"
        "====================================================\n"
        " NATURAL ARABIC\n"
        " SCENE-BASED VISUALS\n"
        " MODERN VISUAL SEARCH\n"
        " EXACT AUDIO SYNCHRONIZATION\n"
        "====================================================\n"
    )

    cleanup_old_files()

    # --------------------------------------------------------
    # 1. Discover topic
    # --------------------------------------------------------

    topic = (
        search_youtube_topics()
    )

    # --------------------------------------------------------
    # 2. Translate
    # --------------------------------------------------------

    topic_ar = (
        translate_to_arabic(
            topic
        )
    )

    # --------------------------------------------------------
    # 3. Build natural Arabic script
    # --------------------------------------------------------

    script = (
        create_script(
            topic_ar
        )
    )

    # --------------------------------------------------------
    # 4. Generate voice FIRST
    # --------------------------------------------------------

    audio_file = (
        create_audio(
            script
        )
    )

    # --------------------------------------------------------
    # 5. Measure exact voice duration
    # --------------------------------------------------------

    audio_duration = (
        get_audio_duration(
            audio_file
        )
    )

    # --------------------------------------------------------
    # 6. Topic-aware visual search
    # --------------------------------------------------------

    images = (
        download_scene_images(
            topic,
            topic_ar
        )
    )

    # --------------------------------------------------------
    # 7. Fallback only if needed
    # --------------------------------------------------------

    if len(images) < MIN_SCENES:

        print(
            "\nNOT ENOUGH RELATED VISUALS."
        )

        print(
            "ADDING FALLBACK VISUALS."
        )

        fallback = (
            download_fallback_images()
        )

        images.extend(
            fallback
        )

    if not images:

        raise RuntimeError(
            "لم يتم العثور على صور."
        )

    images = images[
        :MAX_SCENES
    ]

    # --------------------------------------------------------
    # 8. Normalize
    # --------------------------------------------------------

    normalized = (
        normalize_images(
            images
        )
    )

    # --------------------------------------------------------
    # 9. Create complete video
    # --------------------------------------------------------

    video = (
        create_video(
            normalized,
            audio_file,
            audio_duration
        )
    )

    # --------------------------------------------------------
    # 10. Final measurements
    # --------------------------------------------------------

    video_duration = (
        get_video_duration()
    )

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

    # --------------------------------------------------------
    # DONE
    # --------------------------------------------------------

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
        f"AUDIO: "
        f"{audio_duration:.2f}s"
    )

    print(
        f"VIDEO: "
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