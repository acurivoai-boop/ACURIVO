# ============================================================
# ACURIVO — STORY VISUAL ENGINE
# CRISTIANO RONALDO — SAUDI ARABIC EDITION
# ============================================================

import re
import shutil
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

WIDTH = 1920
HEIGHT = 1080
FPS = 30

IMAGE_TIMEOUT = 12
MAX_IMAGE_BYTES = 8 * 1024 * 1024
IMAGE_MIN_BYTES = 20000

VOICE = "ar-SA-HamedNeural"

# سعودي طبيعي أكثر
VOICE_RATE = "-4%"
VOICE_PITCH = "-1Hz"

# رفع الصوت النهائي
VOICE_VOLUME = 1.28

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) "
    "AppleWebKit/537.36 Chrome/120 Safari/537.36"
)


# ============================================================
# STORY
# كل وحدة = جملة/لقطة صوتية + كلمات بصرية
# ============================================================

STORY = [

    {
        "text":
        "تخيل طفل صغير في جزيرة ماديرا، كل اللي في باله كرة القدم.",
        "visuals": [
            "Cristiano Ronaldo childhood Madeira",
            "young Cristiano Ronaldo Madeira",
            "Funchal Madeira football"
        ]
    },

    {
        "text":
        "من وهو صغير، كان يلعب في الشوارع والمدرسة، وكان يحلم إنه يصير لاعب محترف.",
        "visuals": [
            "young Cristiano Ronaldo football",
            "Cristiano Ronaldo childhood football",
            "Madeira children football"
        ]
    },

    {
        "text":
        "لكن نقطة التحول الحقيقية جات وهو بعمر أحد عشر سنة، يوم ترك ماديرا وراح لشبونة عشان يلتحق بأكاديمية سبورتينغ.",
        "visuals": [
            "Cristiano Ronaldo Sporting academy",
            "Sporting CP academy Lisbon",
            "Sporting Lisbon youth academy"
        ]
    },

    {
        "text":
        "كان قرار صعب جدًا على طفل بهذا العمر، لكنه كان يعرف وش يبي.",
        "visuals": [
            "Cristiano Ronaldo young Sporting",
            "Sporting CP youth Ronaldo",
            "young football academy Portugal"
        ]
    },

    {
        "text":
        "وفي سبورتينغ، بدأ كل شيء يتغير بسرعة.",
        "visuals": [
            "Cristiano Ronaldo Sporting CP",
            "Ronaldo Sporting Lisbon young",
            "Sporting CP Ronaldo"
        ]
    },

    {
        "text":
        "بعمر خمس عشرة سنة بدأ يتدرب مع فريق سبورتينغ الثاني، وبعدها بسنة بدأ يتدرب مع الفريق الأول.",
        "visuals": [
            "Cristiano Ronaldo Sporting training",
            "Ronaldo Sporting first team",
            "Sporting CP training Ronaldo"
        ]
    },

    {
        "text":
        "وفي عام ألفين واثنين، ظهر رونالدو مع الفريق الأول وهو عمره سبعة عشر سنة فقط.",
        "visuals": [
            "Cristiano Ronaldo Sporting 2002",
            "Ronaldo Sporting 2002 match",
            "Ronaldo Sporting debut"
        ]
    },

    {
        "text":
        "كان واضح من وقتها إن فيه شيء مختلف في هذا اللاعب.",
        "visuals": [
            "Cristiano Ronaldo Sporting young",
            "Ronaldo dribbling Sporting",
            "young Ronaldo skills"
        ]
    },

    {
        "text":
        "وبعدها بسنة، جات اللحظة اللي غيّرت حياته بالكامل.",
        "visuals": [
            "Cristiano Ronaldo Manchester United 2003",
            "Ronaldo Manchester United young",
            "Old Trafford Ronaldo 2003"
        ]
    },

    {
        "text":
        "انتقل لمانشستر يونايتد، وهناك بدأ العالم يتعرف على اسم كريستيانو رونالدو.",
        "visuals": [
            "Cristiano Ronaldo Manchester United",
            "Ronaldo Manchester United 2003",
            "Cristiano Ronaldo Old Trafford"
        ]
    },

    {
        "text":
        "سرعة، مهارات، مراوغات، وثقة ما كانت موجودة عند لاعب بهذا العمر.",
        "visuals": [
            "Ronaldo Manchester United dribbling",
            "Cristiano Ronaldo skills Manchester United",
            "Ronaldo stepovers"
        ]
    },

    {
        "text":
        "لكن رونالدو ما اكتفى بالموهبة.",
        "visuals": [
            "Cristiano Ronaldo training",
            "Ronaldo Manchester United training",
            "Cristiano Ronaldo workout"
        ]
    },

    {
        "text":
        "بدأ يتدرب أكثر، يقوي جسمه، ويطور طريقة لعبه موسم بعد موسم.",
        "visuals": [
            "Cristiano Ronaldo gym training",
            "Ronaldo Manchester United training",
            "Cristiano Ronaldo fitness"
        ]
    },

    {
        "text":
        "ومع الوقت، اللاعب اللي كان يحب المراوغة صار هداف مرعب.",
        "visuals": [
            "Cristiano Ronaldo goal Manchester United",
            "Ronaldo scoring Manchester United",
            "Ronaldo goal celebration United"
        ]
    },

    {
        "text":
        "وفي موسم ألفين وسبعة، ألفين وثمانية، انفجر رونالدو بكل معنى الكلمة.",
        "visuals": [
            "Cristiano Ronaldo 2008 Manchester United",
            "Ronaldo 2008 goals",
            "Ronaldo Manchester United 2008"
        ]
    },

    {
        "text":
        "يسجل من داخل المنطقة، ومن خارجها، ويسجل بالرأس، وحتى من الركلات الحرة.",
        "visuals": [
            "Cristiano Ronaldo goal",
            "Ronaldo header goal",
            "Ronaldo free kick Manchester United"
        ]
    },

    {
        "text":
        "وفي عام ألفين وثمانية، رفع دوري أبطال أوروبا، وفاز بالكرة الذهبية.",
        "visuals": [
            "Cristiano Ronaldo Champions League 2008",
            "Ronaldo Champions League trophy 2008",
            "Cristiano Ronaldo Ballon d'Or 2008"
        ]
    },

    {
        "text":
        "وهنا ما عاد السؤال: هل رونالدو بيصير نجم؟",
        "visuals": [
            "Cristiano Ronaldo celebration",
            "Ronaldo Manchester United star",
            "Ronaldo trophy celebration"
        ]
    },

    {
        "text":
        "السؤال صار: إلى وين ممكن يوصل؟",
        "visuals": [
            "Cristiano Ronaldo stadium",
            "Ronaldo looking at stadium",
            "Cristiano Ronaldo portrait football"
        ]
    },

    {
        "text":
        "وفي عام ألفين وتسعة، انتقل إلى ريال مدريد.",
        "visuals": [
            "Cristiano Ronaldo Real Madrid 2009",
            "Ronaldo Real Madrid presentation",
            "Cristiano Ronaldo Santiago Bernabeu 2009"
        ]
    },

    {
        "text":
        "وهناك بدأت واحدة من أعظم مراحل مسيرته.",
        "visuals": [
            "Cristiano Ronaldo Real Madrid",
            "Ronaldo Real Madrid celebration",
            "Cristiano Ronaldo Madrid"
        ]
    },

    {
        "text":
        "الأهداف صارت أكثر، البطولات صارت أكثر، والمباريات الكبيرة صارت ملعبه المفضل.",
        "visuals": [
            "Cristiano Ronaldo Real Madrid goal",
            "Ronaldo Champions League Real Madrid",
            "Ronaldo Real Madrid goal celebration"
        ]
    },

    {
        "text":
        "كل ما سجل هدف، رجع وسجل غيره.",
        "visuals": [
            "Cristiano Ronaldo goal celebration",
            "Ronaldo scoring Real Madrid",
            "Ronaldo goal celebration"
        ]
    },

    {
        "text":
        "وكل ما وصل للقمة، كان يدور قمة أعلى.",
        "visuals": [
            "Cristiano Ronaldo trophy",
            "Ronaldo Champions League trophy",
            "Cristiano Ronaldo celebration stadium"
        ]
    },

    {
        "text":
        "والسر ما كان الموهبة لحالها.",
        "visuals": [
            "Cristiano Ronaldo training",
            "Ronaldo gym",
            "Cristiano Ronaldo workout"
        ]
    },

    {
        "text":
        "السر كان في الانضباط، والتدريب، والاهتمام بأدق التفاصيل.",
        "visuals": [
            "Cristiano Ronaldo training gym",
            "Ronaldo fitness training",
            "Cristiano Ronaldo training session"
        ]
    },

    {
        "text":
        "رونالدو ما كان ينتظر الموهبة تسوي كل شيء عنه.",
        "visuals": [
            "Cristiano Ronaldo training",
            "Ronaldo focused training",
            "Cristiano Ronaldo gym"
        ]
    },

    {
        "text":
        "كان كل يوم يحاول يخلي نفسه أفضل من اليوم اللي قبله.",
        "visuals": [
            "Cristiano Ronaldo intense training",
            "Ronaldo workout",
            "Cristiano Ronaldo focus"
        ]
    },

    {
        "text":
        "من طفل صغير في ماديرا، إلى لاعب في سبورتينغ، إلى نجم في مانشستر يونايتد، ثم أسطورة في ريال مدريد.",
        "visuals": [
            "Cristiano Ronaldo Sporting",
            "Cristiano Ronaldo Manchester United",
            "Cristiano Ronaldo Real Madrid"
        ]
    },

    {
        "text":
        "هذه مو بس قصة لاعب كرة قدم.",
        "visuals": [
            "Cristiano Ronaldo stadium",
            "Ronaldo football legend",
            "Cristiano Ronaldo portrait"
        ]
    },

    {
        "text":
        "هذه قصة واحد قرر من بدري إنه ما يكون عادي.",
        "visuals": [
            "Cristiano Ronaldo celebration",
            "Cristiano Ronaldo legendary",
            "Ronaldo stadium celebration"
        ]
    },

    {
        "text":
        "وهنا بالضبط بدأت الأسطورة.",
        "visuals": [
            "Cristiano Ronaldo legendary celebration",
            "Ronaldo trophy celebration",
            "Cristiano Ronaldo Champions League"
        ]
    },

]


# ============================================================
# COMMAND
# ============================================================

def run(cmd):

    print("\nRUN:", " ".join(map(str, cmd)))

    result = subprocess.run(
        cmd,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    if result.stdout:
        print(result.stdout[-2500:])

    return result


def duration(path):

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

def clean():

    print("\n=== CLEAN ===")

    for folder in [WORK, OUTPUT]:

        folder.mkdir(exist_ok=True)

        for item in folder.iterdir():

            if item.is_file():
                item.unlink(missing_ok=True)

            elif item.is_dir():
                shutil.rmtree(item, ignore_errors=True)


# ============================================================
# SENTENCE VOICE
# ============================================================

async def make_voice(text, output):

    communicate = edge_tts.Communicate(
        text,
        VOICE,
        rate=VOICE_RATE,
        pitch=VOICE_PITCH,
    )

    await communicate.save(
        str(output)
    )


def create_sentence_audio(index, text):

    output = (
        WORK /
        f"audio_{index:03d}.mp3"
    )

    asyncio.run(
        make_voice(
            text,
            output
        )
    )

    return output


# ============================================================
# MEDIAWIKI SEARCH
# ============================================================

def search_images(query):

    url = (
        "https://commons.wikimedia.org/w/api.php"
    )

    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": query,
        "gsrnamespace": 6,
        "gsrlimit": 10,
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

            info = page.get(
                "imageinfo",
                []
            )

            if not info:
                continue

            info = info[0]

            image_url = info.get(
                "url"
            )

            mime = info.get(
                "mime",
                ""
            ).lower()

            width = info.get(
                "width",
                0
            )

            height = info.get(
                "height",
                0
            )

            if not image_url:
                continue

            if not mime.startswith(
                "image/"
            ):
                continue

            if width < 500:
                continue

            if height < 300:
                continue

            results.append(
                {
                    "url": image_url,
                    "title": page.get(
                        "title",
                        ""
                    ),
                    "width": width,
                    "height": height,
                }
            )

        return results

    except Exception as e:

        print(
            "SEARCH ERROR:",
            e
        )

        return []


# ============================================================
# IMAGE SCORING
# ============================================================

def score(title, query):

    title = title.lower()
    query = query.lower()

    points = 0

    if "ronaldo" in title:
        points += 10

    if "cristiano" in title:
        points += 10

    keywords = re.findall(
        r"[a-z]+",
        query
    )

    for word in keywords:

        if len(word) > 3 and word in title:
            points += 2

    if "football" in title:
        points += 2

    if "soccer" in title:
        points += 2

    return points


# ============================================================
# DOWNLOAD
# ============================================================

def download_image(url, output):

    try:

        response = requests.get(
            url,
            headers={
                "User-Agent": USER_AGENT
            },
            timeout=(5, IMAGE_TIMEOUT),
            stream=True,
        )

        response.raise_for_status()

        content_type = (
            response.headers
            .get(
                "Content-Type",
                ""
            )
            .lower()
        )

        if not content_type.startswith(
            "image/"
        ):
            return False

        data = bytearray()

        for chunk in response.iter_content(
            chunk_size=64 * 1024
        ):

            if not chunk:
                continue

            data.extend(chunk)

            if len(data) > MAX_IMAGE_BYTES:
                return False

        if len(data) < IMAGE_MIN_BYTES:
            return False

        output.write_bytes(
            bytes(data)
        )

        # verify
        with Image.open(output) as img:
            img.verify()

        # load again
        with Image.open(output) as img:

            img.load()

            if img.width < 300:
                return False

            if img.height < 300:
                return False

        return True

    except Exception as e:

        print(
            "IMAGE ERROR:",
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
# FIND BEST IMAGE
# ============================================================

def find_visual(index, queries):

    print(
        f"\n=== VISUAL BOT {index} ==="
    )

    candidates = []

    for query in queries:

        print(
            "QUERY:",
            query
        )

        results = search_images(
            query
        )

        for item in results:

            candidates.append(
                (
                    score(
                        item["title"],
                        query
                    ),
                    item
                )
            )

    candidates.sort(
        key=lambda x: x[0],
        reverse=True
    )

    used = set()

    for points, item in candidates:

        url = item["url"]

        if url in used:
            continue

        used.add(url)

        print(
            "TRY:",
            item["title"],
            "SCORE:",
            points
        )

        path = (
            WORK /
            f"visual_{index:03d}.jpg"
        )

        if download_image(
            url,
            path
        ):

            print(
                "VISUAL SELECTED:",
                item["title"]
            )

            return path

    print(
        "NO ONLINE IMAGE."
    )

    return create_fallback(
        index
    )


# ============================================================
# FALLBACK
# ============================================================

def create_fallback(index):

    path = (
        WORK /
        f"visual_{index:03d}.jpg"
    )

    img = Image.new(
        "RGB",
        (WIDTH, HEIGHT),
        (18, 20, 28)
    )

    draw = ImageDraw.Draw(
        img
    )

    for y in range(HEIGHT):

        v = int(
            18 +
            35 * y / HEIGHT
        )

        draw.line(
            [
                (0, y),
                (WIDTH, y)
            ],
            fill=(
                v,
                v,
                v + 10
            )
        )

    try:

        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            75
        )

        small = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            32
        )

    except Exception:

        font = None
        small = None

    title = (
        "CRISTIANO RONALDO"
    )

    box = draw.textbbox(
        (0, 0),
        title,
        font=font
    )

    tw = box[2] - box[0]
    th = box[3] - box[1]

    draw.text(
        (
            (WIDTH - tw) / 2,
            (HEIGHT - th) / 2
        ),
        title,
        fill="white",
        font=font
    )

    draw.text(
        (70, HEIGHT - 80),
        "ACURIVO",
        fill="white",
        font=small
    )

    img.save(
        path,
        quality=95
    )

    return path


# ============================================================
# IMAGE CLIP
# ============================================================

def make_visual_clip(
    image,
    output,
    seconds,
    index
):

    frames = max(
        1,
        int(seconds * FPS)
    )

    zoom = (
        f"1.00+"
        f"0.07*on/{frames}"
    )

    vf = (
        "scale="
        f"{WIDTH}:{HEIGHT}:"
        "force_original_aspect_ratio=increase,"
        f"crop={WIDTH}:{HEIGHT},"
        f"zoompan=z='{zoom}':"
        f"d={frames}:"
        f"s={WIDTH}x{HEIGHT}:"
        f"fps={FPS},"
        "eq=contrast=1.04:"
        "saturation=1.06:"
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
            f"{seconds:.3f}",
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
# AUDIO MASTER
# ============================================================

def master_audio(
    raw,
    final
):

    audio_filter = (
        "highpass=f=65,"
        "lowpass=f=15500,"
        "acompressor="
        "threshold=-19dB:"
        "ratio=2.2:"
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
        "g=1.3,"
        "aecho="
        "0.88:0.08:55:0.035,"
        f"volume={VOICE_VOLUME}"
    )

    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(raw),
            "-af",
            audio_filter,
            "-codec:a",
            "libmp3lame",
            "-b:a",
            "192k",
            str(final),
        ]
    )


# ============================================================
# BUILD AUDIO PER SENTENCE
# ============================================================

def build_audio():

    print(
        "\n=== AUDIO BOT ==="
    )

    audio_files = []

    for index, item in enumerate(
        STORY,
        start=1
    ):

        print(
            f"AUDIO {index}:",
            item["text"]
        )

        raw = (
            WORK /
            f"audio_raw_{index:03d}.mp3"
        )

        final = (
            WORK /
            f"audio_{index:03d}.mp3"
        )

        asyncio.run(
            make_voice(
                item["text"],
                raw
            )
        )

        master_audio(
            raw,
            final
        )

        audio_files.append(
            final
        )

    return audio_files


# ============================================================
# BUILD VISUAL + AUDIO UNITS
# ============================================================

def build_units():

    print(
        "\n=== STORY VISUAL BOT ==="
    )

    audio_files = build_audio()

    units = []

    for index, (
        item,
        audio
    ) in enumerate(
        zip(
            STORY,
            audio_files
        ),
        start=1
    ):

        audio_duration = duration(
            audio
        )

        # كل جملة لها صورة رئيسية
        # والصورة تتغير تلقائياً إذا كانت الجملة طويلة
        visual = find_visual(
            index,
            item["visuals"]
        )

        # إذا الجملة طويلة نستخدم صورتين
        # من نفس المجموعة
        if audio_duration >= 5.5:

            mid = audio_duration / 2

            visual2 = find_visual(
                index + 1000,
                item["visuals"][1:]
            )

            units.append(
                {
                    "audio": audio,
                    "visuals": [
                        (visual, mid),
                        (
                            visual2,
                            audio_duration - mid
                        )
                    ]
                }
            )

        else:

            units.append(
                {
                    "audio": audio,
                    "visuals": [
                        (
                            visual,
                            audio_duration
                        )
                    ]
                }
            )

    return units


# ============================================================
# CONCAT VIDEO UNITS
# ============================================================

def build_video(units):

    print(
        "\n=== VIDEO EDITOR BOT ==="
    )

    video_files = []

    counter = 0

    for unit_index, unit in enumerate(
        units,
        start=1
    ):

        for visual, seconds in unit[
            "visuals"
        ]:

            counter += 1

            clip = (
                WORK /
                f"clip_{counter:03d}.mp4"
            )

            print(
                f"CLIP {counter}: "
                f"{seconds:.2f}s"
            )

            make_visual_clip(
                visual,
                clip,
                seconds,
                counter
            )

            video_files.append(
                clip
            )

    concat_file = (
        WORK /
        "video_concat.txt"
    )

    concat_file.write_text(
        "\n".join(
            f"file '{x.resolve()}'"
            for x in video_files
        ),
        encoding="utf-8"
    )

    silent_video = (
        WORK /
        "silent_video.mp4"
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
            str(silent_video),
        ]
    )

    return silent_video


# ============================================================
# BUILD COMPLETE AUDIO
# ============================================================

def build_master_audio():

    print(
        "\n=== MASTER AUDIO ==="
    )

    concat_file = (
        WORK /
        "audio_concat.txt"
    )

    audio_files = sorted(
        WORK.glob(
            "audio_[0-9][0-9][0-9].mp3"
        )
    )

    concat_file.write_text(
        "\n".join(
            f"file '{x.resolve()}'"
            for x in audio_files
        ),
        encoding="utf-8"
    )

    combined = (
        WORK /
        "master_voice.mp3"
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
            "-c:a",
            "libmp3lame",
            "-b:a",
            "192k",
            str(combined),
        ]
    )

    return combined


# ============================================================
# FINAL
# ============================================================

def final_render(
    silent_video,
    master_audio
):

    print(
        "\n=== FINAL RENDER BOT ==="
    )

    if VIDEO_FINAL.exists():
        VIDEO_FINAL.unlink()

    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(silent_video),
            "-i",
            str(master_audio),
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
            "FINAL VIDEO FAILED"
        )

    video_duration = duration(
        VIDEO_FINAL
    )

    size_mb = (
        VIDEO_FINAL.stat().st_size
        / 1024
        / 1024
    )

    print(
        "\n================================"
    )

    print(
        "ACURIVO VIDEO COMPLETE"
    )

    print(
        f"DURATION: {video_duration:.2f}s"
    )

    print(
        f"SIZE: {size_mb:.2f} MB"
    )

    print(
        "================================"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        """
============================================================
ACURIVO STORY VISUAL ENGINE
CRISTIANO RONALDO
SAUDI ARABIC EDITION
============================================================
"""
    )

    clean()

    units = build_units()

    silent_video = build_video(
        units
    )

    master_audio = build_master_audio()

    final_render(
        silent_video,
        master_audio
    )

    print(
        "\nACURIVO PRODUCTION FINISHED."
    )


if __name__ == "__main__":
    main()