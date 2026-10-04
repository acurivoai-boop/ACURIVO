import asyncio
import hashlib
import os
import re
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path

import edge_tts
import requests
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps


# ============================================================
# ACURIVO VIDEO FACTORY V8
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

    result = subprocess.run(
        [str(x) for x in cmd],
        check=check,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    if result.stdout:
        print(result.stdout[-4000:])

    return result


def ffprobe_duration(path):
    try:
        result = run([
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(path)
        ])

        return float(result.stdout.strip())

    except Exception:
        return 0.0


def clean_text(text):
    text = text or ""

    # Remove HTML / SSML.
    text = re.sub(r"<[^>]+>", " ", text)

    # Remove markdown.
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = re.sub(r"`(.*?)`", r"\1", text)

    # Remove control characters.
    text = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", " ", text)

    # Normalize whitespace.
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
    }

    for a, b in replacements.items():
        text = text.replace(a, b)

    return text


def keyword_tokens(text):
    text = normalize_arabic(text)

    words = re.findall(
        r"[\u0600-\u06FF]{3,}|[A-Za-z]{3,}",
        text
    )

    stop = {
        "this", "that", "with", "from", "into",
        "near", "says", "about", "after",
        "will", "have", "been", "more",
        "latest", "news", "breakthrough",
        "technology", "modern",
        "future", "world",
        "the", "and", "for",
        "كيف", "لماذا", "ماذا", "هذا", "هذه",
        "التي", "الذي", "هناك", "يمكن",
        "خلال", "اليوم", "العالم",
        "بشكل", "اكثر", "الناس",
        "حول", "الى", "على", "من",
        "في", "عن", "مع",
    }

    return [
        w for w in words
        if w.lower() not in stop
    ]


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

            with urllib.request.urlopen(
                req,
                timeout=20
            ) as response:

                html = response.read().decode(
                    "utf-8",
                    errors="ignore"
                )

            titles = re.findall(
                r'"title":{"runs":\[\{"text":"(.*?)"\}\]',
                html
            )

            for title in titles[:15]:

                title = clean_text(title)

                if len(title) < 20:
                    continue

                if title not in candidates:
                    candidates.append(title)

        except Exception as e:
            print("Topic search warning:", e)

    if not candidates:

        return (
            "كيف يغيّر الذكاء الاصطناعي "
            "طريقة عمل الشركات في المستقبل؟"
        )

    priority_words = [
        "AI",
        "artificial",
        "intelligence",
        "ذكاء",
        "الذكاء",
        "robot",
        "robotics",
        "روبوت",
        "future",
        "المستقبل",
        "technology",
        "تقنية",
        "energy",
        "طاقة",
        "space",
        "فضاء",
        "chip",
        "رقائق",
    ]

    bad_words = [
        "football",
        "soccer",
        "match",
        "goal",
        "music",
        "song",
        "movie",
        "trailer",
        "gaming",
        "gameplay",
        "celebrity",
    ]

    scored = []

    for title in candidates:

        score = 0
        lower = title.lower()

        for word in priority_words:

            if word.lower() in lower:
                score += 3

        for word in bad_words:

            if word in lower:
                score -= 10

        score += min(len(title) / 50, 2)

        scored.append((score, title))

    scored.sort(
        key=lambda x: x[0],
        reverse=True
    )

    topic = scored[0][1]

    print("SELECTED TOPIC:", topic)

    return topic


# ============================================================
# SCRIPT
# ============================================================

def build_script(topic):

    topic = clean_text(topic)

    scenes = [

        {
            "text": (
                f"في السنوات الأخيرة، بدأ موضوع {topic} "
                "يتحول من فكرة متخصصة إلى موضوع يؤثر "
                "في القرارات والأعمال والحياة اليومية."
            ),
            "visual": [
                "robotics",
                "artificial intelligence",
                "technology",
                "robot"
            ],
        },

        {
            "text": (
                "لكن السؤال الأهم ليس فقط ماذا يحدث، "
                "بل لماذا أصبح هذا الموضوع مهمًا الآن؟ "
                "السبب هو تسارع التطور، وتداخل التقنية "
                "مع قطاعات كانت في السابق بعيدة عنها."
            ),
            "visual": [
                "artificial intelligence",
                "technology innovation",
                "future technology",
                "robotics"
            ],
        },

        {
            "text": (
                "التغيير الحقيقي يظهر عندما تنتقل الفكرة "
                "من المختبر أو الأخبار إلى تطبيقات فعلية. "
                "عندها تبدأ الشركات والمؤسسات في إعادة التفكير "
                "في طريقة العمل، والتكلفة، والسرعة، وحتى المخاطر."
            ),
            "visual": [
                "industrial robotics",
                "technology industry",
                "smart factory",
                "automation"
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
            "visual": [
                "data center",
                "computer data",
                "artificial intelligence data",
                "human computer"
            ],
        },

        {
            "text": (
                "وفي المقابل، توجد تحديات لا يمكن تجاهلها. "
                "منها الخصوصية، والأمن، والاعتماد الزائد على الأنظمة، "
                "إضافة إلى الحاجة إلى مهارات جديدة تستطيع التعامل "
                "مع هذا التحول بسرعة ووعي."
            ),
            "visual": [
                "cybersecurity",
                "computer security",
                "digital security",
                "data security"
            ],
        },

        {
            "text": (
                "ورغم هذه التحديات، فإن الاتجاه العام واضح. "
                "الجهات التي تفهم التحول مبكرًا تستطيع بناء ميزة "
                "تنافسية، بينما قد تجد الجهات المتأخرة نفسها "
                "تتعامل مع واقع جديد فرض نفسه بالفعل."
            ),
            "visual": [
                "business technology",
                "digital transformation",
                "modern industry",
                "innovation"
            ],
        },

        {
            "text": (
                "خلال السنوات القادمة، لن يكون السؤال فقط "
                "من يملك التقنية الأقوى. "
                "السؤال سيكون: من يستطيع تحويلها إلى قيمة حقيقية، "
                "وبطريقة آمنة ومستدامة وقابلة للتوسع؟"
            ),
            "visual": [
                "future technology",
                "advanced robotics",
                "future industry",
                "artificial intelligence future"
            ],
        },

        {
            "text": (
                "وفي النهاية، قد لا يكون أهم ما في هذا التحول "
                "هو التقنية نفسها، بل الطريقة التي ستغير بها "
                "قراراتنا وأعمالنا ونظرتنا إلى المستقبل. "
                "وهذا بالضبط ما يجعل متابعة هذه التطورات "
                "أمرًا يستحق الانتباه."
            ),
            "visual": [
                "future technology",
                "technology future",
                "artificial intelligence",
                "digital future"
            ],
        },
    ]

    return scenes


# ============================================================
# VOICE
# ============================================================

async def generate_voice_async(text, output):

    text = clean_text(text)

    # IMPORTANT:
    # Python API instead of edge-tts CLI.
    # No SSML.
    # No <break>.
    # No --file.

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

    asyncio.run(
        generate_voice_async(
            text,
            output
        )
    )

    duration = ffprobe_duration(output)

    if duration <= 0:
        raise RuntimeError(
            "Voice generation produced an invalid audio file."
        )

    print(
        f"VOICE DURATION: {duration:.2f}s"
    )


# ============================================================
# AUDIO MASTERING
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

    duration = ffprobe_duration(
        AUDIO_FINAL
    )

    if duration <= 0:
        raise RuntimeError(
            "Final audio mastering failed."
        )

    print(
        f"MASTERED AUDIO: {duration:.2f}s"
    )


# ============================================================
# WIKIMEDIA
# ============================================================

def search_wikimedia(query, limit=10):

    try:

        api = (
            "https://commons.wikimedia.org/"
            "w/api.php"
        )

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
            headers={
                "User-Agent": USER_AGENT
            },
            timeout=25,
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
                "imageinfo",
                [{}]
            )[0]

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
                ),
            })

        return results

    except Exception as e:

        print(
            "Wikimedia warning:",
            e
        )

        return []


# ============================================================
# WIKIPEDIA FALLBACK
# ============================================================

def search_wikipedia(query, limit=5):

    results = []

    languages = [
        "en",
        "ar",
    ]

    for language in languages:

        try:

            api = (
                f"https://{language}.wikipedia.org/"
                "w/api.php"
            )

            params = {
                "action": "query",
                "format": "json",
                "generator": "search",
                "gsrsearch": query,
                "gsrlimit": limit,
                "prop": "pageimages",
                "piprop": "thumbnail",
                "pithumbsize": 1600,
            }

            response = requests.get(
                api,
                params=params,
                headers={
                    "User-Agent": USER_AGENT
                },
                timeout=20,
            )

            response.raise_for_status()

            data = response.json()

            pages = (
                data
                .get("query", {})
                .get("pages", {})
            )

            for page in pages.values():

                thumb = page.get(
                    "thumbnail"
                )

                if not thumb:
                    continue

                url = thumb.get(
                    "source"
                )

                if url:

                    results.append({
                        "url": url,
                        "title": page.get(
                            "title",
                            ""
                        ),
                    })

        except Exception as e:

            print(
                "Wikipedia warning:",
                e
            )

    return results


# ============================================================
# IMAGE SCORING
# ============================================================

def score_image(title, query):

    title_words = set(
        keyword_tokens(title)
    )

    query_words = set(
        keyword_tokens(query)
    )

    if not title_words or not query_words:
        return 0

    overlap = len(
        title_words & query_words
    )

    score = overlap * 10

    useful = [
        "robot",
        "robotics",
        "artificial",
        "intelligence",
        "technology",
        "computer",
        "machine",
        "industry",
        "factory",
        "data",
        "server",
        "cyber",
        "security",
        "science",
        "laboratory",
        "energy",
        "space",
        "satellite",
        "chip",
        "future",
        "automation",
    ]

    combined = " ".join(
        title_words
    ).lower()

    for word in useful:

        if word in combined:
            score += 2

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
# DOWNLOAD IMAGE
# ============================================================

def download_image(url, output):

    try:

        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": USER_AGENT
            }
        )

        with urllib.request.urlopen(
            req,
            timeout=30
        ) as response:

            data = response.read()

        if len(data) < 5000:
            raise RuntimeError(
                "Image response too small."
            )

        output.write_bytes(data)

        with Image.open(output) as img:
            img.verify()

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
# CINEMATIC FALLBACK IMAGE
# ============================================================

def create_fallback_image(
    scene_index,
    topic,
    scene
):

    print(
        f"Creating cinematic fallback "
        f"for scene {scene_index}"
    )

    output = (
        WORK /
        f"scene_{scene_index}_fallback.jpg"
    )

    # Stable seed based on topic + scene.
    seed = hashlib.md5(
        f"{topic}-{scene_index}".encode(
            "utf-8"
        )
    ).hexdigest()

    values = [
        int(seed[i:i+2], 16)
        for i in range(0, 12, 2)
    ]

    base = Image.new(
        "RGB",
        (WIDTH, HEIGHT),
        (
            12 + values[0] % 18,
            16 + values[1] % 20,
            24 + values[2] % 28,
        )
    )

    draw = ImageDraw.Draw(base)

    # Cinematic geometric technology background.
    for i in range(14):

        x = (
            values[(i + 1) % len(values)]
            / 255
            * WIDTH
        )

        y = (
            values[(i + 2) % len(values)]
            / 255
            * HEIGHT
        )

        radius = 100 + (
            values[(i + 3) % len(values)]
            * 2
        )

        draw.ellipse(
            (
                x - radius,
                y - radius,
                x + radius,
                y + radius,
            ),
            outline=(
                45,
                65,
                90
            ),
            width=3,
        )

    # Topic keywords as small visual labels.
    words = keyword_tokens(
        topic
    )[:5]

    y = 80

    for word in words:

        draw.text(
            (80, y),
            word.upper(),
            fill=(
                170,
                185,
                205
            )
        )

        y += 55

    # Dark cinematic vignette.
    vignette = Image.new(
        "L",
        (WIDTH, HEIGHT),
        0
    )

    vdraw = ImageDraw.Draw(
        vignette
    )

    vdraw.ellipse(
        (
            -WIDTH * 0.2,
            -HEIGHT * 0.2,
            WIDTH * 1.2,
            HEIGHT * 1.2,
        ),
        fill=255
    )

    vignette = vignette.filter(
        ImageFilter.GaussianBlur(180)
    )

    base = Image.composite(
        base,
        Image.new(
            "RGB",
            (WIDTH, HEIGHT),
            (5, 7, 12)
        ),
        vignette
    )

    base = ImageEnhance.Contrast(
        base
    ).enhance(1.15)

    base.save(
        output,
        "JPEG",
        quality=92
    )

    return output


# ============================================================
# PREPARE IMAGE
# ============================================================

def prepare_image(
    source,
    target
):

    with Image.open(source) as img:

        img = img.convert(
            "RGB"
        )

        img = ImageOps.fit(
            img,
            (WIDTH, HEIGHT),
            method=Image.Resampling.LANCZOS,
            centering=(0.5, 0.5),
        )

        img = ImageEnhance.Contrast(
            img
        ).enhance(1.04)

        img = ImageEnhance.Color(
            img
        ).enhance(1.03)

        img.save(
            target,
            "JPEG",
            quality=94,
            optimize=True
        )


# ============================================================
# SCENE IMAGE
# ============================================================

def create_scene_image(
    scene_index,
    scene,
    topic
):

    print(
        f"\n=== VISUAL SCENE "
        f"{scene_index} ==="
    )

    candidates = []

    # --------------------------------------------------------
    # 1. Search using short visual queries.
    # --------------------------------------------------------

    for query in scene["visual"]:

        print(
            "WIKIMEDIA SEARCH:",
            query
        )

        results = search_wikimedia(
            query,
            limit=10
        )

        for item in results:

            existing_urls = {
                x["url"]
                for x in candidates
            }

            if item["url"] not in existing_urls:

                candidates.append(item)

        if len(candidates) >= 12:
            break

    # --------------------------------------------------------
    # 2. If Wikimedia is weak, search Wikipedia.
    # --------------------------------------------------------

    if not candidates:

        for query in scene["visual"]:

            print(
                "WIKIPEDIA SEARCH:",
                query
            )

            results = search_wikipedia(
                query,
                limit=5
            )

            candidates.extend(
                results
            )

            if candidates:
                break

    # --------------------------------------------------------
    # 3. Try topic keywords.
    # --------------------------------------------------------

    if not candidates:

        topic_words = keyword_tokens(
            topic
        )

        for word in topic_words[:5]:

            print(
                "TOPIC FALLBACK SEARCH:",
                word
            )

            results = search_wikimedia(
                word,
                limit=10
            )

            candidates.extend(
                results
            )

            if candidates:
                break

    raw = (
        WORK /
        f"scene_{scene_index}_raw.jpg"
    )

    final = (
        WORK /
        f"scene_{scene_index}.jpg"
    )

    # --------------------------------------------------------
    # 4. Select and download.
    # --------------------------------------------------------

    selected = select_image(
        " ".join(
            scene["visual"]
        ),
        candidates
    )

    if selected:

        print(
            "SELECTED IMAGE:",
            selected.get(
                "title",
                ""
            )
        )

        if download_image(
            selected["url"],
            raw
        ):

            prepare_image(
                raw,
                final
            )

            return final

    # --------------------------------------------------------
    # 5. Never stop the whole video because of an image.
    # --------------------------------------------------------

    print(
        "No external image available."
    )

    fallback = create_fallback_image(
        scene_index,
        topic,
        scene
    )

    prepare_image(
        fallback,
        final
    )

    return final


# ============================================================
# SCENE AUDIO
# ============================================================

def generate_scene_audios(
    scenes
):

    print(
        "\n=== GENERATING SCENE AUDIO ==="
    )

    audio_files = []

    for i, scene in enumerate(
        scenes,
        start=1
    ):

        path = (
            WORK /
            f"scene_{i}_voice.mp3"
        )

        if path.exists():
            path.unlink()

        generate_voice(
            scene["text"],
            path
        )

        audio_files.append(
            path
        )

    return audio_files


# ============================================================
# CONCATENATE AUDIO
# ============================================================

def concatenate_audio(
    audio_files,
    output
):

    print(
        "\n=== CONCATENATING AUDIO ==="
    )

    list_file = (
        WORK /
        "audio_list.txt"
    )

    with list_file.open(
        "w",
        encoding="utf-8"
    ) as f:

        for path in audio_files:

            safe = (
                str(path.resolve())
                .replace(
                    "'",
                    "'\\''"
                )
            )

            f.write(
                f"file '{safe}'\n"
            )

    run([
        "ffmpeg",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(list_file),
        "-c:a",
        "libmp3lame",
        "-b:a",
        "192k",
        str(output),
    ])

    duration = ffprobe_duration(
        output
    )

    if duration <= 0:

        raise RuntimeError(
            "Audio concatenation failed."
        )

    print(
        f"TOTAL AUDIO: {duration:.2f}s"
    )


# ============================================================
# RENDER SCENE
# ============================================================

def render_scene(
    index,
    image_path,
    audio_path
):

    print(
        f"\n=== RENDERING SCENE "
        f"{index} ==="
    )

    duration = ffprobe_duration(
        audio_path
    )

    if duration <= 0:

        raise RuntimeError(
            f"Invalid audio duration "
            f"for scene {index}"
        )

    output = (
        WORK /
        f"scene_{index}.mp4"
    )

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
        "-loop",
        "1",
        "-i",
        str(image_path),
        "-i",
        str(audio_path),
        "-vf",
        zoom,
        "-t",
        f"{duration:.3f}",
        "-r",
        str(FPS),
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "20",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-shortest",
        str(output),
    ])

    actual = ffprobe_duration(
        output
    )

    if actual <= 0:

        raise RuntimeError(
            f"Scene {index} rendering failed."
        )

    return output


# ============================================================
# CONCATENATE VIDEO
# ============================================================

def concatenate_video(
    scene_videos
):

    print(
        "\n=== BUILDING FINAL VIDEO ==="
    )

    list_file = (
        WORK /
        "video_list.txt"
    )

    with list_file.open(
        "w",
        encoding="utf-8"
    ) as f:

        for path in scene_videos:

            safe = (
                str(path.resolve())
                .replace(
                    "'",
                    "'\\''"
                )
            )

            f.write(
                f"file '{safe}'\n"
            )

    temp_video = (
        WORK /
        "video_concat.mp4"
    )

    run([
        "ffmpeg",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(list_file),
        "-c",
        "copy",
        str(temp_video),
    ])

    return temp_video


# ============================================================
# FINAL MUX
# ============================================================

def mux_final_video(
    video_file
):

    print(
        "\n=== FINAL VIDEO MUX ==="
    )

    if VIDEO_PATH.exists():
        VIDEO_PATH.unlink()

    run([
        "ffmpeg",
        "-y",
        "-i",
        str(video_file),
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
        "-movflags",
        "+faststart",
        "-shortest",
        str(VIDEO_PATH),
    ])

    duration = ffprobe_duration(
        VIDEO_PATH
    )

    if duration <= 0:

        raise RuntimeError(
            "Final video duration is invalid."
        )

    size_mb = (
        VIDEO_PATH.stat().st_size
        / 1024
        / 1024
    )

    print(
        f"\nFINAL VIDEO: "
        f"{duration:.2f}s"
    )

    print(
        f"FINAL SIZE: "
        f"{size_mb:.2f} MB"
    )

    if size_mb > 45:

        raise RuntimeError(
            f"Final video is too large: "
            f"{size_mb:.2f} MB"
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print(
        "ACURIVO VIDEO FACTORY V8"
    )
    print("=" * 60)

    # --------------------------------------------------------
    # 1. Discover topic
    # --------------------------------------------------------

    topic = discover_topic()

    # --------------------------------------------------------
    # 2. Build script
    # --------------------------------------------------------

    scenes = build_script(
        topic
    )

    print(
        "\n=== SCRIPT ==="
    )

    full_text = []

    for i, scene in enumerate(
        scenes,
        start=1
    ):

        print(
            f"\nSCENE {i}:"
        )

        print(
            scene["text"]
        )

        full_text.append(
            scene["text"]
        )

    script_text = (
        "\n\n".join(
            full_text
        )
    )

    (
        WORK /
        "script.txt"
    ).write_text(
        script_text,
        encoding="utf-8"
    )

    # --------------------------------------------------------
    # 3. Generate scene voices
    # --------------------------------------------------------

    scene_audios = (
        generate_scene_audios(
            scenes
        )
    )

    # --------------------------------------------------------
    # 4. Build master audio
    # --------------------------------------------------------

    concatenate_audio(
        scene_audios,
        AUDIO_RAW
    )

    master_audio()

    # --------------------------------------------------------
    # 5. Create scene visuals
    # --------------------------------------------------------

    scene_images = []

    for i, scene in enumerate(
        scenes,
        start=1
    ):

        image = create_scene_image(
            i,
            scene,
            topic
        )

        scene_images.append(
            image
        )

    # --------------------------------------------------------
    # 6. Render scenes
    # --------------------------------------------------------

    scene_videos = []

    for i, (image, audio) in enumerate(
        zip(
            scene_images,
            scene_audios
        ),
        start=1
    ):

        video = render_scene(
            i,
            image,
            audio
        )

        scene_videos.append(
            video
        )

    # --------------------------------------------------------
    # 7. Concatenate
    # --------------------------------------------------------

    concat_video = (
        concatenate_video(
            scene_videos
        )
    )

    # --------------------------------------------------------
    # 8. Final mux
    # --------------------------------------------------------

    mux_final_video(
        concat_video
    )

    # --------------------------------------------------------
    # 9. Final verification
    # --------------------------------------------------------

    final_duration = (
        ffprobe_duration(
            VIDEO_PATH
        )
    )

    final_size = (
        VIDEO_PATH.stat().st_size
        / 1024
        / 1024
    )

    print("\n" + "=" * 60)
    print(
        "ACURIVO VIDEO READY"
    )
    print("=" * 60)

    print(
        f"TOPIC: {topic}"
    )

    print(
        f"DURATION: "
        f"{final_duration:.2f}s"
    )

    print(
        f"SIZE: "
        f"{final_size:.2f} MB"
    )

    print(
        f"FILE: {VIDEO_PATH}"
    )

    if final_duration < 30:

        raise RuntimeError(
            "Final video is unexpectedly short."
        )

    if final_size > 45:

        raise RuntimeError(
            f"Final video is too large: "
            f"{final_size:.2f} MB"
        )

    print(
        "\nSUCCESS."
    )


if __name__ == "__main__":

    try:

        main()

    except Exception as e:

        print(
            "\nFATAL ERROR:"
        )

        print(
            str(e)
        )

        sys.exit(1)