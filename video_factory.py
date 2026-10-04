import asyncio
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import quote

import edge_tts
import requests
from PIL import Image, ImageOps, ImageFilter


# ============================================================
# ACURIVO VIDEO FACTORY
# RONALDO STORY — SAUDI ARABIC / DYNAMIC VISUAL ENGINE
# ============================================================

BASE = Path(__file__).resolve().parent

OUTPUT_DIR = BASE / "output"
WORK_DIR = BASE / "work"

OUTPUT_DIR.mkdir(exist_ok=True)
WORK_DIR.mkdir(exist_ok=True)

FINAL_VIDEO = OUTPUT_DIR / "ACURIVO_VIDEO.mp4"

VOICE = "ar-SA-HamedNeural"
VOICE_RATE = "-3%"
VOICE_PITCH = "-1Hz"

VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
FPS = 30

MAX_VIDEO_MB = 45

IMAGE_TIMEOUT = 20
MAX_IMAGE_BYTES = 8 * 1024 * 1024
IMAGE_MIN_BYTES = 12 * 1024

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) "
    "AppleWebKit/537.36 "
    "(KHTML, like Gecko) "
    "Chrome/125 Safari/537.36 "
    "ACURIVO-VideoFactory/1.0"
)

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": USER_AGENT,
    "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
})

USED_IMAGE_URLS = set()


# ============================================================
# STORY
# ============================================================

STORY = [

    {
        "text": (
            "تخيل معاي طفل صغير في جزيرة ماديرا، "
            "ما عنده شهرة، ولا فلوس، ولا أحد يعرف اسمه. "
            "لكن عنده شيء واحد ما كان ينقصه أبدًا... الإصرار."
        ),
        "queries": [
            "Cristiano Ronaldo childhood Madeira",
            "Cristiano Ronaldo young Madeira",
            "Funchal Madeira football childhood",
            "Cristiano Ronaldo childhood football"
        ],
    },

    {
        "text": (
            "هذا الطفل كان اسمه كريستيانو رونالدو. "
            "ومن وهو صغير، كان واضح إنه يتعامل مع الكورة بطريقة مختلفة عن الباقين."
        ),
        "queries": [
            "Cristiano Ronaldo young football",
            "Cristiano Ronaldo childhood football Portugal",
            "Cristiano Ronaldo young Sporting",
            "Ronaldo youth football"
        ],
    },

    {
        "text": (
            "وعمره تقريبًا إحدى عشر سنة، أخذ قرار صعب جدًا. "
            "ترك ماديرا وراح للبرتغال عشان يلعب ويتدرب في سبورتينغ لشبونة."
        ),
        "queries": [
            "Cristiano Ronaldo Sporting Lisbon youth",
            "Cristiano Ronaldo Sporting CP academy",
            "Sporting Lisbon academy Ronaldo",
            "Cristiano Ronaldo Lisbon young"
        ],
    },

    {
        "text": (
            "القرار هذا كان يعني إنه يبعد عن أهله وحياته اللي يعرفها، "
            "ويبدأ من الصفر في مكان جديد."
        ),
        "queries": [
            "Cristiano Ronaldo Sporting academy young",
            "Sporting CP academy Lisbon",
            "Cristiano Ronaldo youth academy",
            "Sporting Lisbon training ground"
        ],
    },

    {
        "text": (
            "لكن رونالدو ما راح هناك عشان يكون لاعب عادي. "
            "كان يتدرب، ويتطور، وكل يوم يحاول يثبت إنه يستاهل فرصته."
        ),
        "queries": [
            "Cristiano Ronaldo Sporting training",
            "Cristiano Ronaldo training young",
            "Sporting CP training Ronaldo",
            "Cristiano Ronaldo academy training"
        ],
    },

    {
        "text": (
            "وبعمر سبعة عشر سنة، جاءت لحظة مهمة جدًا. "
            "رونالدو لعب مع الفريق الأول لسبورتينغ، وبدأ اسمه يلفت الأنظار."
        ),
        "queries": [
            "Cristiano Ronaldo Sporting first team 2002",
            "Cristiano Ronaldo Sporting 2002",
            "Ronaldo Sporting debut",
            "Cristiano Ronaldo Sporting CP match"
        ],
    },

    {
        "text": (
            "وبعدها بسنة تقريبًا، تغير كل شيء. "
            "في مباراة ودية أمام مانشستر يونايتد، اللاعبون والمدرب شافوا شيء مختلف تمامًا."
        ),
        "queries": [
            "Cristiano Ronaldo Manchester United Sporting 2003",
            "Ronaldo Sporting Manchester United 2003",
            "Cristiano Ronaldo 2003 Manchester United",
            "Ronaldo first Manchester United match"
        ],
    },

    {
        "text": (
            "السير أليكس فيرغسون اقتنع إنه قدامه موهبة تستاهل الاستثمار. "
            "وهنا بدأ فصل جديد في حياة رونالدو."
        ),
        "queries": [
            "Alex Ferguson Cristiano Ronaldo 2003",
            "Cristiano Ronaldo Ferguson Manchester United",
            "Ronaldo Manchester United signing",
            "Cristiano Ronaldo Manchester United young"
        ],
    },

    {
        "text": (
            "راح رونالدو إلى مانشستر يونايتد، وهناك لبس القميص رقم سبعة. "
            "رقم كان له وزن كبير، وكان لازم يثبت إنه يستحقه."
        ),
        "queries": [
            "Cristiano Ronaldo Manchester United number 7",
            "Ronaldo Manchester United 2003 number 7",
            "Cristiano Ronaldo Manchester United young 7",
            "Ronaldo Old Trafford 2003"
        ],
    },

    {
        "text": (
            "في البداية، كان عنده مهارة وسرعة، لكن جسمه كان يحتاج وقت عشان يتطور. "
            "وفِرغسون وفريقه اشتغلوا معه خطوة خطوة."
        ),
        "queries": [
            "Cristiano Ronaldo Manchester United training",
            "Cristiano Ronaldo gym Manchester United",
            "Ronaldo training Ferguson",
            "Cristiano Ronaldo early Manchester United"
        ],
    },

    {
        "text": (
            "وبعدين بدأ الانفجار الحقيقي. "
            "رونالدو صار أقوى، أسرع، وأخطر قدام المرمى."
        ),
        "queries": [
            "Cristiano Ronaldo Manchester United goal",
            "Ronaldo Manchester United 2007",
            "Cristiano Ronaldo 2008 Manchester United",
            "Ronaldo Old Trafford goal"
        ],
    },

    {
        "text": (
            "في موسم ألفين وسبعة إلى ألفين وثمانية، وصل لمستوى مختلف تمامًا. "
            "أهداف كثيرة، مباريات كبيرة، وحضور يخليك تعرف إن اللاعب هذا مو عادي."
        ),
        "queries": [
            "Cristiano Ronaldo 2007 2008 Manchester United",
            "Ronaldo 2008 Champions League",
            "Cristiano Ronaldo 2008 trophy",
            "Ronaldo Manchester United 2008 celebration"
        ],
    },

    {
        "text": (
            "فاز بدوري أبطال أوروبا مع مانشستر يونايتد، "
            "وفاز بالكرة الذهبية لأول مرة في مسيرته."
        ),
        "queries": [
            "Cristiano Ronaldo 2008 Ballon d'Or",
            "Cristiano Ronaldo 2008 Champions League trophy",
            "Ronaldo Manchester United Champions League 2008",
            "Cristiano Ronaldo Ballon d'Or 2008"
        ],
    },

    {
        "text": (
            "لكن طموحه ما وقف هنا. "
            "في ألفين وتسعة، انتقل لريال مدريد، وبدأت واحدة من أعظم مراحل مسيرته."
        ),
        "queries": [
            "Cristiano Ronaldo Real Madrid presentation 2009",
            "Ronaldo Real Madrid 2009",
            "Cristiano Ronaldo Santiago Bernabeu 2009",
            "Ronaldo Real Madrid signing 2009"
        ],
    },

    {
        "text": (
            "في مدريد، رونالدو ما اكتفى إنه يحافظ على مستواه. "
            "كان كل موسم تقريبًا يحاول يكسر رقم جديد، ويسجل أكثر، ويفوز أكثر."
        ),
        "queries": [
            "Cristiano Ronaldo Real Madrid goal",
            "Cristiano Ronaldo Real Madrid celebration",
            "Ronaldo Real Madrid Champions League",
            "Cristiano Ronaldo Real Madrid training"
        ],
    },

    {
        "text": (
            "صار هداف، وصار رمز للفريق، وصار واحد من أكثر اللاعبين تأثيرًا في تاريخ النادي."
        ),
        "queries": [
            "Cristiano Ronaldo Real Madrid captain",
            "Cristiano Ronaldo Real Madrid legend",
            "Ronaldo Real Madrid trophy",
            "Cristiano Ronaldo Real Madrid celebration"
        ],
    },

    {
        "text": (
            "لكن السر الحقيقي في قصة رونالدو مو بس الموهبة. "
            "السر في التدريب، والانضباط، والقدرة على الاستمرار حتى بعد ما يوصل للقمة."
        ),
        "queries": [
            "Cristiano Ronaldo training Real Madrid",
            "Cristiano Ronaldo gym training",
            "Ronaldo workout training",
            "Cristiano Ronaldo fitness"
        ],
    },

    {
        "text": (
            "من طفل في ماديرا، إلى لاعب صغير في سبورتينغ، "
            "إلى نجم في مانشستر يونايتد، وبعدها أسطورة في ريال مدريد."
        ),
        "queries": [
            "Cristiano Ronaldo Madeira Sporting Manchester Real Madrid",
            "Cristiano Ronaldo career montage",
            "Cristiano Ronaldo career",
            "Ronaldo Manchester United Real Madrid"
        ],
    },

    {
        "text": (
            "قصة رونالدو تذكرنا بشيء بسيط جدًا: "
            "الموهبة ممكن تفتح لك الباب، لكن الاستمرار هو اللي يخليك تبقى في القمة."
        ),
        "queries": [
            "Cristiano Ronaldo celebration",
            "Cristiano Ronaldo trophy celebration",
            "Cristiano Ronaldo football stadium",
            "Cristiano Ronaldo iconic"
        ],
    },

    {
        "text": (
            "وهذا هو رونالدو... "
            "طفل كان يحلم، وكبر وهو يطارد حلمه، لين صار اسمه واحد من أشهر الأسماء في تاريخ كرة القدم."
        ),
        "queries": [
            "Cristiano Ronaldo iconic celebration",
            "Cristiano Ronaldo Portugal",
            "Cristiano Ronaldo football legend",
            "Cristiano Ronaldo portrait"
        ],
    },
]


# ============================================================
# UTILITIES
# ============================================================

def run(cmd, check=True, capture=False):
    print("\nRUN:", " ".join(str(x) for x in cmd))

    return subprocess.run(
        [str(x) for x in cmd],
        check=check,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.STDOUT if capture else None,
    )


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
    text = text.replace("…", "...")
    return text.strip()


# ============================================================
# VOICE
# ============================================================

async def make_voice_async(text, output):
    communicate = edge_tts.Communicate(
        text=clean_text(text),
        voice=VOICE,
        rate=VOICE_RATE,
        pitch=VOICE_PITCH,
    )

    await communicate.save(str(output))


def make_voice(text, output):
    print("\nCREATING SAUDI ARABIC VOICE...")
    print(text)

    asyncio.run(
        make_voice_async(text, output)
    )

    if not output.exists() or output.stat().st_size < 5000:
        raise RuntimeError("Voice generation failed.")

    duration = ffprobe_duration(output)

    print(f"VOICE DURATION: {duration:.2f}s")

    return duration


# ============================================================
# WIKIMEDIA SEARCH
# ============================================================

def search_wikimedia(query, limit=12):
    api = "https://commons.wikimedia.org/w/api.php"

    params = {
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrsearch": query,
        "gsrnamespace": 6,
        "gsrlimit": limit,
        "prop": "imageinfo",
        "iiprop": "url|size|mime",
        "iiurlwidth": 1600,
    }

    try:
        response = SESSION.get(
            api,
            params=params,
            timeout=IMAGE_TIMEOUT,
        )

        response.raise_for_status()

        data = response.json()

        pages = data.get("query", {}).get("pages", {})

        results = []

        for page in pages.values():

            title = page.get("title", "")

            info = page.get("imageinfo", [])

            if not info:
                continue

            image = info[0]

            url = (
                image.get("thumburl")
                or image.get("url")
            )

            if not url:
                continue

            mime = image.get("mime", "")

            if not mime.startswith("image/"):
                continue

            lower_title = title.lower()

            blocked = [
                ".svg",
                ".gif",
                "logo",
                "flag",
                "icon",
                "jersey",
                "card",
                "illustration",
                "painting",
                "poster",
                "statue",
                "sculpture",
            ]

            if any(x in lower_title for x in blocked):
                continue

            width = image.get("width", 0) or 0
            height = image.get("height", 0) or 0

            if width < 500 or height < 400:
                continue

            results.append({
                "title": title,
                "url": url,
                "width": width,
                "height": height,
            })

        return results

    except Exception as e:
        print("WIKIMEDIA SEARCH ERROR:", e)
        return []


# ============================================================
# IMAGE DOWNLOAD
# ============================================================

def download_image(url, output):

    try:

        response = SESSION.get(
            url,
            headers={
                "User-Agent": USER_AGENT,
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

        if not content_type.startswith("image/"):
            raise RuntimeError(
                f"Invalid content type: {content_type}"
            )

        content_length = response.headers.get(
            "Content-Length"
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

        with Image.open(output) as img:
            img.verify()

        with Image.open(output) as img:
            img.load()

            width, height = img.size

            if width < 300 or height < 300:
                raise RuntimeError(
                    "Image resolution too small."
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
# IMAGE RELEVANCE
# ============================================================

def score_image(title, query):

    title_l = title.lower()
    query_words = [
        x.lower()
        for x in re.findall(
            r"[A-Za-z0-9]+",
            query
        )
        if len(x) > 2
    ]

    score = 0

    for word in query_words:

        if word in title_l:
            score += 5

    important = [
        "ronaldo",
        "cristiano",
        "sporting",
        "madrid",
        "united",
        "football",
        "soccer",
        "manchester",
        "portugal",
        "madeira",
        "champions",
        "ballon",
        "real madrid",
    ]

    for word in important:

        if word in title_l:
            score += 4

    bad = [
        "logo",
        "flag",
        "poster",
        "illustration",
        "painting",
        "statue",
    ]

    for word in bad:

        if word in title_l:
            score -= 20

    return score


# ============================================================
# FIND MULTIPLE UNIQUE VISUALS
# ============================================================

def find_visuals(queries, count, scene_index):

    print(
        f"\nSEARCHING {count} VISUALS "
        f"FOR SCENE {scene_index}..."
    )

    candidates = []

    for query in queries:

        print("SEARCH:", query)

        results = search_wikimedia(
            query,
            limit=15
        )

        for item in results:

            item["score"] = score_image(
                item["title"],
                query
            )

            candidates.append(item)

    # Deduplicate URLs
    unique = {}

    for item in candidates:

        url = item["url"]

        if url not in unique:

            unique[url] = item

    candidates = list(
        unique.values()
    )

    candidates.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    selected = []

    # First pass: never-used images
    for item in candidates:

        url = item["url"]

        if url in USED_IMAGE_URLS:
            continue

        selected.append(item)

        if len(selected) >= count:
            break

    # Second pass if not enough
    if len(selected) < count:

        for item in candidates:

            url = item["url"]

            if any(
                x["url"] == url
                for x in selected
            ):
                continue

            selected.append(item)

            if len(selected) >= count:
                break

    print(
        f"SELECTED {len(selected)} "
        f"VISUALS FOR SCENE {scene_index}"
    )

    return selected[:count]


# ============================================================
# PREP IMAGE
# ============================================================

def prepare_image(input_path, output_path):

    with Image.open(input_path) as img:

        img = img.convert("RGB")

        # Crop intelligently to 16:9
        img = ImageOps.fit(
            img,
            (
                VIDEO_WIDTH,
                VIDEO_HEIGHT,
            ),
            method=Image.Resampling.LANCZOS,
            centering=(0.5, 0.5),
        )

        # Very subtle sharpening
        img = img.filter(
            ImageFilter.UnsharpMask(
                radius=1.0,
                percent=90,
                threshold=3,
            )
        )

        img.save(
            output_path,
            "JPEG",
            quality=94,
            optimize=True,
        )


# ============================================================
# CREATE DYNAMIC IMAGE CLIP
# ============================================================

def create_motion_clip(
    image_path,
    output_path,
    duration,
    motion_index,
):

    frames = max(
        1,
        int(math.ceil(duration * FPS))
    )

    # Different movement for every image
    patterns = [

        (
            "min(zoom+0.0018,1.10)",
            "iw/2-(iw/zoom/2)+sin(on/18)*35",
            "ih/2-(ih/zoom/2)"
        ),

        (
            "min(zoom+0.0016,1.09)",
            "iw/2-(iw/zoom/2)",
            "ih/2-(ih/zoom/2)+cos(on/20)*28"
        ),

        (
            "min(zoom+0.0015,1.08)",
            "iw/2-(iw/zoom/2)-sin(on/22)*32",
            "ih/2-(ih/zoom/2)"
        ),

        (
            "min(zoom+0.0017,1.09)",
            "iw/2-(iw/zoom/2)",
            "ih/2-(ih/zoom/2)-sin(on/19)*30"
        ),
    ]

    z, x, y = patterns[
        motion_index % len(patterns)
    ]

    filter_complex = (
        f"scale=2400:-2,"
        f"zoompan="
        f"z='{z}':"
        f"x='{x}':"
        f"y='{y}':"
        f"d=1:"
        f"s={VIDEO_WIDTH}x{VIDEO_HEIGHT}:"
        f"fps={FPS},"
        f"setsar=1,"
        f"format=yuv420p"
    )

    run([
        "ffmpeg",
        "-y",
        "-loop",
        "1",
        "-i",
        image_path,
        "-vf",
        filter_complex,
        "-t",
        f"{duration:.3f}",
        "-r",
        str(FPS),
        "-an",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "23",
        "-pix_fmt",
        "yuv420p",
        output_path,
    ])


# ============================================================
# CREATE SCENE
# ============================================================

def create_scene(
    scene_index,
    scene,
):

    scene_dir = WORK_DIR / (
        f"scene_{scene_index:02d}"
    )

    scene_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    text_file = (
        scene_dir / "script.txt"
    )

    text_file.write_text(
        scene["text"],
        encoding="utf-8"
    )

    audio_file = (
        scene_dir / "voice.mp3"
    )

    duration = make_voice(
        scene["text"],
        audio_file
    )

    # Number of images based on speech length
    image_count = max(
        2,
        min(
            4,
            int(math.ceil(duration / 2.0))
        )
    )

    visuals = find_visuals(
        scene["queries"],
        image_count,
        scene_index
    )

    if len(visuals) < 2:

        raise RuntimeError(
            f"Not enough relevant visuals "
            f"for scene {scene_index}."
        )

    image_files = []

    for index, item in enumerate(visuals):

        raw_file = (
            scene_dir /
            f"raw_{index:02d}.jpg"
        )

        prepared_file = (
            scene_dir /
            f"image_{index:02d}.jpg"
        )

        ok = download_image(
            item["url"],
            raw_file
        )

        if not ok:
            continue

        try:

            prepare_image(
                raw_file,
                prepared_file
            )

            image_files.append(
                prepared_file
            )

            USED_IMAGE_URLS.add(
                item["url"]
            )

            print(
                f"VISUAL {index + 1}: "
                f"{item['title']}"
            )

        except Exception as e:

            print(
                "IMAGE PREP ERROR:",
                e
            )

    if len(image_files) < 2:

        raise RuntimeError(
            f"Could not prepare enough "
            f"visuals for scene {scene_index}."
        )

    # Divide speech duration over visuals
    per_image = duration / len(
        image_files
    )

    clip_files = []

    remaining = duration

    for index, image_file in enumerate(
        image_files
    ):

        if index == len(image_files) - 1:
            clip_duration = remaining
        else:
            clip_duration = per_image

        clip_duration = max(
            1.35,
            clip_duration
        )

        clip_file = (
            scene_dir /
            f"clip_{index:02d}.mp4"
        )

        create_motion_clip(
            image_file,
            clip_file,
            clip_duration,
            index + scene_index
        )

        clip_files.append(
            clip_file
        )

        remaining -= clip_duration

    # Concatenate scene visuals
    concat_file = (
        scene_dir /
        "concat.txt"
    )

    with concat_file.open(
        "w",
        encoding="utf-8"
    ) as f:

        for clip in clip_files:

            f.write(
                f"file '{clip.resolve()}'\n"
            )

    silent_scene = (
        scene_dir /
        "visual.mp4"
    )

    run([
        "ffmpeg",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        concat_file,
        "-c",
        "copy",
        "-movflags",
        "+faststart",
        silent_scene,
    ])

    # Attach scene audio
    scene_video = (
        scene_dir /
        "scene.mp4"
    )

    run([
        "ffmpeg",
        "-y",
        "-i",
        silent_scene,
        "-i",
        audio_file,
        "-map",
        "0:v:0",
        "-map",
        "1:a:0",
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        "-b:a",
        "160k",
        "-shortest",
        "-movflags",
        "+faststart",
        scene_video,
    ])

    print(
        f"SCENE {scene_index} READY."
    )

    return scene_video


# ============================================================
# BUILD ALL SCENES
# ============================================================

def build_scenes():

    scenes = []

    for index, scene in enumerate(
        STORY,
        start=1
    ):

        print(
            "\n"
            + "=" * 70
        )

        print(
            f"BUILDING SCENE {index}/{len(STORY)}"
        )

        print(
            "=" * 70
        )

        scene_video = create_scene(
            index,
            scene
        )

        scenes.append(
            scene_video
        )

    return scenes


# ============================================================
# CONCATENATE ALL SCENES
# ============================================================

def concatenate_scenes(
    scenes,
    output
):

    concat_file = (
        WORK_DIR /
        "all_scenes.txt"
    )

    with concat_file.open(
        "w",
        encoding="utf-8"
    ) as f:

        for scene in scenes:

            f.write(
                f"file '{scene.resolve()}'\n"
            )

    run([
        "ffmpeg",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        concat_file,
        "-c",
        "copy",
        "-movflags",
        "+faststart",
        output,
    ])


# ============================================================
# MASTER AUDIO
# ============================================================

def master_audio(
    input_video,
    output_video
):

    print(
        "\nMASTERING AUDIO..."
    )

    audio_filter = (
        "highpass=f=60,"
        "lowpass=f=15000,"
        "acompressor="
        "threshold=-18dB:"
        "ratio=2.5:"
        "attack=10:"
        "release=180,"
        "volume=1.35,"
        "aecho=0.88:0.05:55:0.025,"
        "loudnorm="
        "I=-13:"
        "TP=-1.5:"
        "LRA=7"
    )

    run([
        "ffmpeg",
        "-y",
        "-i",
        input_video,
        "-vf",
        (
            "scale="
            f"{VIDEO_WIDTH}:"
            f"{VIDEO_HEIGHT}:"
            "force_original_aspect_ratio=decrease,"
            f"pad={VIDEO_WIDTH}:"
            f"{VIDEO_HEIGHT}:"
            "(ow-iw)/2:"
            "(oh-ih)/2,"
            "format=yuv420p"
        ),
        "-af",
        audio_filter,
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "25",
        "-maxrate",
        "2500k",
        "-bufsize",
        "5000k",
        "-c:a",
        "aac",
        "-b:a",
        "160k",
        "-ar",
        "48000",
        "-movflags",
        "+faststart",
        output_video,
    ])


# ============================================================
# COMPRESS IF TOO LARGE
# ============================================================

def compress_if_needed(video):

    size_mb = (
        video.stat().st_size
        / 1024
        / 1024
    )

    print(
        f"\nFINAL SIZE: {size_mb:.2f} MB"
    )

    if size_mb <= MAX_VIDEO_MB:

        return video

    print(
        "VIDEO TOO LARGE."
    )

    compressed = (
        WORK_DIR /
        "compressed.mp4"
    )

    run([
        "ffmpeg",
        "-y",
        "-i",
        video,
        "-c:v",
        "libx264",
        "-preset",
        "slow",
        "-crf",
        "29",
        "-maxrate",
        "1800k",
        "-bufsize",
        "3600k",
        "-c:a",
        "aac",
        "-b:a",
        "128k",
        "-movflags",
        "+faststart",
        compressed,
    ])

    new_size = (
        compressed.stat().st_size
        / 1024
        / 1024
    )

    print(
        f"COMPRESSED SIZE: "
        f"{new_size:.2f} MB"
    )

    if new_size > MAX_VIDEO_MB:

        print(
            "SECOND COMPRESSION PASS..."
        )

        compressed2 = (
            WORK_DIR /
            "compressed_final.mp4"
        )

        run([
            "ffmpeg",
            "-y",
            "-i",
            compressed,
            "-c:v",
            "libx264",
            "-preset",
            "slow",
            "-crf",
            "31",
            "-maxrate",
            "1400k",
            "-bufsize",
            "2800k",
            "-c:a",
            "aac",
            "-b:a",
            "112k",
            "-movflags",
            "+faststart",
            compressed2,
        ])

        compressed = compressed2

        new_size = (
            compressed.stat().st_size
            / 1024
            / 1024
        )

        print(
            f"FINAL COMPRESSED SIZE: "
            f"{new_size:.2f} MB"
        )

    shutil.copy2(
        compressed,
        video
    )

    return video


# ============================================================
# VALIDATE VIDEO
# ============================================================

def validate_video(video):

    print(
        "\nVALIDATING FINAL VIDEO..."
    )

    duration = ffprobe_duration(
        video
    )

    if duration < 30:

        raise RuntimeError(
            "Final video is unexpectedly short."
        )

    size_mb = (
        video.stat().st_size
        / 1024
        / 1024
    )

    if size_mb > MAX_VIDEO_MB:

        raise RuntimeError(
            f"Final video is still too large: "
            f"{size_mb:.2f} MB"
        )

    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height,r_frame_rate",
            "-of",
            "json",
            str(video),
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    print(
        result.stdout
    )

    print(
        f"FINAL DURATION: {duration:.2f}s"
    )

    print(
        f"FINAL SIZE: {size_mb:.2f} MB"
    )

    print(
        "VIDEO VALIDATION: PASS"
    )


# ============================================================
# CLEAN OLD WORK
# ============================================================

def clean_work():

    if WORK_DIR.exists():

        for item in WORK_DIR.iterdir():

            try:

                if item.is_dir():
                    shutil.rmtree(item)

                else:
                    item.unlink()

            except Exception as e:

                print(
                    "CLEAN ERROR:",
                    e
                )


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "\n"
        + "=" * 70
    )

    print(
        "ACURIVO VIDEO FACTORY"
    )

    print(
        "RONALDO — SAUDI ARABIC / DYNAMIC VISUAL ENGINE"
    )

    print(
        "=" * 70
    )

    clean_work()

    FINAL_VIDEO.unlink(
        missing_ok=True
    )

    scenes = build_scenes()

    print(
        "\nALL SCENES CREATED:",
        len(scenes)
    )

    raw_video = (
        WORK_DIR /
        "raw_complete.mp4"
    )

    concatenate_scenes(
        scenes,
        raw_video
    )

    mastered_video = (
        WORK_DIR /
        "mastered.mp4"
    )

    master_audio(
        raw_video,
        mastered_video
    )

    shutil.copy2(
        mastered_video,
        FINAL_VIDEO
    )

    compress_if_needed(
        FINAL_VIDEO
    )

    validate_video(
        FINAL_VIDEO
    )

    print(
        "\n"
        + "=" * 70
    )

    print(
        "ACURIVO VIDEO READY"
    )

    print(
        f"FILE: {FINAL_VIDEO}"
    )

    print(
        "=" * 70
    )


if __name__ == "__main__":
    try:
        main()

    except Exception as e:

        print(
            "\n"
            + "=" * 70
        )

        print(
            "FATAL ERROR:"
        )

        print(
            str(e)
        )

        print(
            "=" * 70
        )

        sys.exit(1)