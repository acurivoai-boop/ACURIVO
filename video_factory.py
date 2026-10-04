import asyncio
import base64
import io
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
# RONALDO EDITION
# SAUDI ARABIC + DYNAMIC VISUAL ENGINE
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

WIDTH = 1920
HEIGHT = 1080
FPS = 30

MAX_VIDEO_MB = 45

IMAGE_TIMEOUT = 20
MAX_IMAGE_BYTES = 8 * 1024 * 1024
MIN_IMAGE_BYTES = 10 * 1024

USER_AGENT = (
    "Mozilla/5.0 "
    "(X11; Linux x86_64) "
    "AppleWebKit/537.36 "
    "(KHTML, like Gecko) "
    "Chrome/125 Safari/537.36 "
    "ACURIVO Video Factory"
)

SESSION = requests.Session()

SESSION.headers.update({
    "User-Agent": USER_AGENT,
    "Accept": "*/*",
})

USED_IMAGES = set()


# ============================================================
# STORY
# ============================================================

STORY = [

    {
        "text":
            "تخيل معاي طفل صغير في جزيرة ماديرا. "
            "ما عنده شهرة، ولا فلوس، ولا أحد يعرف اسمه. "
            "لكن عنده شيء واحد ما كان ينقصه أبدًا... الإصرار.",

        "queries": [
            "Cristiano Ronaldo childhood",
            "Cristiano Ronaldo young",
            "Cristiano Ronaldo Madeira",
            "Ronaldo youth football",
        ],
    },

    {
        "text":
            "هذا الطفل كان اسمه كريستيانو رونالدو. "
            "ومن وهو صغير، كان واضح إنه يتعامل مع الكورة بطريقة مختلفة عن الباقين.",

        "queries": [
            "Cristiano Ronaldo young football",
            "Cristiano Ronaldo childhood football",
            "Ronaldo young football Portugal",
            "Cristiano Ronaldo youth",
        ],
    },

    {
        "text":
            "وعمره تقريبًا إحدى عشر سنة، أخذ قرار صعب جدًا. "
            "ترك ماديرا وراح للبرتغال عشان يلعب ويتدرب في سبورتينغ لشبونة.",

        "queries": [
            "Cristiano Ronaldo Sporting Lisbon youth",
            "Cristiano Ronaldo Sporting CP academy",
            "Ronaldo Sporting Lisbon",
            "Sporting CP Ronaldo academy",
        ],
    },

    {
        "text":
            "القرار هذا كان يعني إنه يبعد عن أهله وحياته اللي يعرفها، "
            "ويبدأ من الصفر في مكان جديد.",

        "queries": [
            "Cristiano Ronaldo Sporting academy",
            "Sporting Lisbon academy",
            "Cristiano Ronaldo Lisbon young",
            "Ronaldo Sporting training",
        ],
    },

    {
        "text":
            "لكن رونالدو ما راح هناك عشان يكون لاعب عادي. "
            "كان يتدرب، ويتطور، وكل يوم يحاول يثبت إنه يستاهل فرصته.",

        "queries": [
            "Cristiano Ronaldo training young",
            "Cristiano Ronaldo Sporting training",
            "Ronaldo training football",
            "Cristiano Ronaldo academy",
        ],
    },

    {
        "text":
            "وبعمر سبعة عشر سنة، جاءت لحظة مهمة جدًا. "
            "رونالدو لعب مع الفريق الأول لسبورتينغ، وبدأ اسمه يلفت الأنظار.",

        "queries": [
            "Cristiano Ronaldo Sporting debut",
            "Cristiano Ronaldo Sporting 2002",
            "Ronaldo Sporting CP 2002",
            "Cristiano Ronaldo first team Sporting",
        ],
    },

    {
        "text":
            "وبعدها بسنة تقريبًا، تغير كل شيء. "
            "في مباراة ودية أمام مانشستر يونايتد، الناس شافوا شيء مختلف تمامًا.",

        "queries": [
            "Cristiano Ronaldo Sporting Manchester United 2003",
            "Ronaldo Manchester United 2003",
            "Cristiano Ronaldo Manchester United young",
            "Ronaldo Sporting Manchester United",
        ],
    },

    {
        "text":
            "السير أليكس فيرغسون اقتنع إنه قدامه موهبة تستاهل الاستثمار. "
            "وهنا بدأ فصل جديد في حياة رونالدو.",

        "queries": [
            "Alex Ferguson Cristiano Ronaldo",
            "Ferguson Ronaldo Manchester United",
            "Cristiano Ronaldo Ferguson 2003",
            "Ronaldo Manchester United signing",
        ],
    },

    {
        "text":
            "راح رونالدو إلى مانشستر يونايتد، وهناك لبس القميص رقم سبعة. "
            "رقم كان له وزن كبير، وكان لازم يثبت إنه يستحقه.",

        "queries": [
            "Cristiano Ronaldo Manchester United number 7",
            "Ronaldo Manchester United 7",
            "Cristiano Ronaldo Old Trafford",
            "Ronaldo Manchester United young",
        ],
    },

    {
        "text":
            "في البداية، كان عنده مهارة وسرعة، لكن جسمه كان يحتاج وقت عشان يتطور. "
            "وفِرغسون وفريقه اشتغلوا معه خطوة خطوة.",

        "queries": [
            "Cristiano Ronaldo Manchester United training",
            "Ronaldo Manchester United training",
            "Cristiano Ronaldo gym",
            "Ronaldo Ferguson training",
        ],
    },

    {
        "text":
            "وبعدين بدأ الانفجار الحقيقي. "
            "رونالدو صار أقوى، أسرع، وأخطر قدام المرمى.",

        "queries": [
            "Cristiano Ronaldo Manchester United goal",
            "Ronaldo Manchester United goal",
            "Cristiano Ronaldo 2007",
            "Ronaldo Old Trafford goal",
        ],
    },

    {
        "text":
            "في موسم ألفين وسبعة إلى ألفين وثمانية، وصل لمستوى مختلف تمامًا. "
            "أهداف كثيرة، مباريات كبيرة، وحضور يخليك تعرف إن اللاعب هذا مو عادي.",

        "queries": [
            "Cristiano Ronaldo 2007 2008",
            "Ronaldo Manchester United 2008",
            "Cristiano Ronaldo Champions League 2008",
            "Ronaldo 2008 football",
        ],
    },

    {
        "text":
            "فاز بدوري أبطال أوروبا مع مانشستر يونايتد، "
            "وفاز بالكرة الذهبية لأول مرة في مسيرته.",

        "queries": [
            "Cristiano Ronaldo Champions League 2008",
            "Cristiano Ronaldo Ballon d'Or 2008",
            "Ronaldo Manchester United trophy",
            "Ronaldo 2008 trophy",
        ],
    },

    {
        "text":
            "لكن طموحه ما وقف هنا. "
            "في ألفين وتسعة، انتقل لريال مدريد، وبدأت واحدة من أعظم مراحل مسيرته.",

        "queries": [
            "Cristiano Ronaldo Real Madrid 2009",
            "Ronaldo Real Madrid presentation",
            "Cristiano Ronaldo Real Madrid signing",
            "Ronaldo Santiago Bernabeu 2009",
        ],
    },

    {
        "text":
            "في مدريد، رونالدو ما اكتفى إنه يحافظ على مستواه. "
            "كان كل موسم تقريبًا يحاول يكسر رقم جديد، ويسجل أكثر، ويفوز أكثر.",

        "queries": [
            "Cristiano Ronaldo Real Madrid goal",
            "Cristiano Ronaldo Real Madrid celebration",
            "Ronaldo Real Madrid Champions League",
            "Cristiano Ronaldo Real Madrid match",
        ],
    },

    {
        "text":
            "صار هداف، وصار رمز للفريق، وصار واحد من أكثر اللاعبين تأثيرًا في تاريخ النادي.",

        "queries": [
            "Cristiano Ronaldo Real Madrid legend",
            "Cristiano Ronaldo Real Madrid trophy",
            "Ronaldo Real Madrid celebration",
            "Cristiano Ronaldo Real Madrid",
        ],
    },

    {
        "text":
            "لكن السر الحقيقي في قصة رونالدو مو بس الموهبة. "
            "السر في التدريب، والانضباط، والقدرة على الاستمرار حتى بعد ما يوصل للقمة.",

        "queries": [
            "Cristiano Ronaldo training",
            "Ronaldo gym training",
            "Cristiano Ronaldo workout",
            "Cristiano Ronaldo fitness",
        ],
    },

    {
        "text":
            "من طفل في ماديرا، إلى لاعب صغير في سبورتينغ، "
            "إلى نجم في مانشستر يونايتد، وبعدها أسطورة في ريال مدريد.",

        "queries": [
            "Cristiano Ronaldo career",
            "Cristiano Ronaldo Sporting Manchester Real Madrid",
            "Ronaldo career",
            "Cristiano Ronaldo football",
        ],
    },

    {
        "text":
            "قصة رونالدو تذكرنا بشيء بسيط جدًا. "
            "الموهبة ممكن تفتح لك الباب، لكن الاستمرار هو اللي يخليك تبقى في القمة.",

        "queries": [
            "Cristiano Ronaldo celebration",
            "Cristiano Ronaldo trophy",
            "Ronaldo football stadium",
            "Cristiano Ronaldo iconic",
        ],
    },

    {
        "text":
            "وهذا هو رونالدو. "
            "طفل كان يحلم، وكبر وهو يطارد حلمه، لين صار اسمه واحد من أشهر الأسماء في تاريخ كرة القدم.",

        "queries": [
            "Cristiano Ronaldo Portugal",
            "Cristiano Ronaldo legend",
            "Cristiano Ronaldo iconic",
            "Cristiano Ronaldo football",
        ],
    },
]


# ============================================================
# COMMAND
# ============================================================

def run(cmd, check=True, capture=False):

    print("\nRUN:", " ".join(map(str, cmd)))

    return subprocess.run(
        [str(x) for x in cmd],
        check=check,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.STDOUT if capture else None,
    )


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
        capture_output=True,
        text=True,
        check=True,
    )

    return float(result.stdout.strip())


# ============================================================
# VOICE
# ============================================================

async def make_voice_async(text, output):

    communicate = edge_tts.Communicate(
        text=text,
        voice=VOICE,
        rate=VOICE_RATE,
        pitch=VOICE_PITCH,
    )

    await communicate.save(
        str(output)
    )


def make_voice(text, output):

    print("\nVOICE:")
    print(text)

    asyncio.run(
        make_voice_async(
            text,
            output
        )
    )

    if (
        not output.exists()
        or output.stat().st_size < 5000
    ):
        raise RuntimeError(
            "Voice generation failed."
        )

    d = duration(output)

    print(
        f"VOICE DURATION: {d:.2f}s"
    )

    return d


# ============================================================
# WIKIMEDIA
# ============================================================

def wikimedia_search(query, limit=20):

    url = (
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
        "iiprop": "url|size|mime",
        "iiurlwidth": 1600,
    }

    try:

        response = SESSION.get(
            url,
            params=params,
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

            title = page.get(
                "title",
                ""
            )

            infos = page.get(
                "imageinfo",
                []
            )

            if not infos:
                continue

            info = infos[0]

            image_url = (
                info.get("thumburl")
                or info.get("url")
            )

            if not image_url:
                continue

            mime = (
                info.get("mime", "")
                .lower()
            )

            if not mime.startswith(
                "image/"
            ):
                continue

            lower = title.lower()

            forbidden = [
                ".svg",
                ".gif",
                "logo",
                "flag",
                "icon",
                "poster",
                "jersey",
                "illustration",
                "painting",
                "statue",
                "sculpture",
            ]

            if any(
                word in lower
                for word in forbidden
            ):
                continue

            width = info.get(
                "width",
                0
            ) or 0

            height = info.get(
                "height",
                0
            ) or 0

            if width < 400 or height < 300:
                continue

            results.append({
                "title": title,
                "url": image_url,
                "width": width,
                "height": height,
            })

        return results

    except Exception as e:

        print(
            "WIKIMEDIA ERROR:",
            e
        )

        return []


# ============================================================
# WIKIPEDIA PAGE IMAGE FALLBACK
# ============================================================

def wikipedia_image():

    url = (
        "https://en.wikipedia.org/"
        "w/api.php"
    )

    params = {
        "action": "query",
        "format": "json",
        "prop": "pageimages",
        "piprop": "original",
        "titles": "Cristiano Ronaldo",
    }

    try:

        response = SESSION.get(
            url,
            params=params,
            timeout=IMAGE_TIMEOUT,
        )

        response.raise_for_status()

        pages = (
            response.json()
            .get("query", {})
            .get("pages", {})
        )

        for page in pages.values():

            original = page.get(
                "original"
            )

            if original:

                return {
                    "title":
                        "Cristiano Ronaldo Wikipedia",
                    "url":
                        original.get("source"),
                }

    except Exception as e:

        print(
            "WIKIPEDIA ERROR:",
            e
        )

    return None


# ============================================================
# SCORE
# ============================================================

def score_result(
    title,
    query
):

    title = title.lower()

    words = re.findall(
        r"[a-z0-9]+",
        query.lower()
    )

    score = 0

    for word in words:

        if len(word) > 2 and word in title:
            score += 4

    strong_words = [
        "ronaldo",
        "cristiano",
        "sporting",
        "madrid",
        "united",
        "manchester",
        "portugal",
        "madeira",
        "football",
        "soccer",
        "champions",
        "ballon",
    ]

    for word in strong_words:

        if word in title:
            score += 3

    return score


# ============================================================
# DOWNLOAD
# ============================================================

def download_image(
    url,
    output
):

    try:

        response = SESSION.get(
            url,
            timeout=(5, IMAGE_TIMEOUT),
            stream=True,
            allow_redirects=True,
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

        if (
            content_type
            and not content_type.startswith(
                "image/"
            )
        ):

            raise RuntimeError(
                "Not an image."
            )

        data = bytearray()

        for chunk in response.iter_content(
            chunk_size=65536
        ):

            if not chunk:
                continue

            data.extend(chunk)

            if len(data) > MAX_IMAGE_BYTES:

                raise RuntimeError(
                    "Image too large."
                )

        if len(data) < MIN_IMAGE_BYTES:

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

            w, h = img.size

            if w < 300 or h < 250:

                raise RuntimeError(
                    "Resolution too small."
                )

        print(
            "IMAGE OK:",
            f"{len(data)/1024/1024:.2f} MB"
        )

        return True

    except Exception as e:

        print(
            "IMAGE FAILED:",
            e
        )

        output.unlink(
            missing_ok=True
        )

        return False


# ============================================================
# FIND VISUALS
# ============================================================

def find_visuals(
    queries,
    count,
    scene_index
):

    print(
        "\n"
        + "-" * 60
    )

    print(
        f"VISUAL SEARCH — SCENE {scene_index}"
    )

    print(
        "-" * 60
    )

    candidates = []

    # --------------------------------------------------------
    # Search every query
    # --------------------------------------------------------

    for query in queries:

        print(
            "SEARCH:",
            query
        )

        results = wikimedia_search(
            query,
            limit=20
        )

        print(
            "RESULTS:",
            len(results)
        )

        for result in results:

            result["score"] = score_result(
                result["title"],
                query
            )

            candidates.append(
                result
            )

    # --------------------------------------------------------
    # If specific searches fail,
    # broaden search automatically
    # --------------------------------------------------------

    if len(candidates) < count:

        print(
            "SPECIFIC SEARCH WEAK."
        )

        fallback_queries = [
            "Cristiano Ronaldo",
            "Ronaldo football",
            "Cristiano Ronaldo Portugal",
            "Cristiano Ronaldo Real Madrid",
            "Cristiano Ronaldo Manchester United",
        ]

        for query in fallback_queries:

            print(
                "FALLBACK SEARCH:",
                query
            )

            results = wikimedia_search(
                query,
                limit=25
            )

            for result in results:

                result["score"] = score_result(
                    result["title"],
                    query
                )

                candidates.append(
                    result
                )

    # --------------------------------------------------------
    # Deduplicate
    # --------------------------------------------------------

    unique = {}

    for item in candidates:

        url = item["url"]

        if url not in unique:

            unique[url] = item

    candidates = list(
        unique.values()
    )

    candidates.sort(
        key=lambda x:
            x.get("score", 0),
        reverse=True
    )

    # --------------------------------------------------------
    # First pass: never used
    # --------------------------------------------------------

    selected = []

    for item in candidates:

        if item["url"] in USED_IMAGES:

            continue

        selected.append(
            item
        )

        if len(selected) >= count:

            break

    # --------------------------------------------------------
    # Second pass: permit old image
    # --------------------------------------------------------

    if len(selected) < count:

        for item in candidates:

            if any(
                x["url"]
                == item["url"]
                for x in selected
            ):

                continue

            selected.append(
                item
            )

            if len(selected) >= count:

                break

    # --------------------------------------------------------
    # Wikipedia fallback
    # --------------------------------------------------------

    if len(selected) < count:

        wiki = wikipedia_image()

        if wiki:

            if not any(
                x["url"]
                == wiki["url"]
                for x in selected
            ):

                selected.append(
                    wiki
                )

    print(
        "SELECTED VISUALS:",
        len(selected)
    )

    return selected[:count]


# ============================================================
# PREP IMAGE
# ============================================================

def prepare_image(
    input_path,
    output_path
):

    with Image.open(
        input_path
    ) as img:

        img = img.convert(
            "RGB"
        )

        img = ImageOps.fit(
            img,
            (
                WIDTH,
                HEIGHT
            ),
            method=Image.Resampling.LANCZOS,
            centering=(0.5, 0.5),
        )

        img = img.filter(
            ImageFilter.UnsharpMask(
                radius=1.0,
                percent=80,
                threshold=3,
            )
        )

        img.save(
            output_path,
            "JPEG",
            quality=93,
            optimize=True,
        )


# ============================================================
# MOTION CLIP
# ============================================================

def create_motion_clip(
    image,
    output,
    clip_duration,
    motion_index
):

    patterns = [

        (
            "min(zoom+0.0018,1.10)",
            "iw/2-(iw/zoom/2)+sin(on/18)*45",
            "ih/2-(ih/zoom/2)"
        ),

        (
            "min(zoom+0.0017,1.09)",
            "iw/2-(iw/zoom/2)",
            "ih/2-(ih/zoom/2)+cos(on/20)*40"
        ),

        (
            "min(zoom+0.0016,1.09)",
            "iw/2-(iw/zoom/2)-sin(on/21)*45",
            "ih/2-(ih/zoom/2)"
        ),

        (
            "min(zoom+0.0018,1.10)",
            "iw/2-(iw/zoom/2)",
            "ih/2-(ih/zoom/2)-cos(on/19)*38"
        ),
    ]

    z, x, y = patterns[
        motion_index % len(patterns)
    ]

    vf = (
        "scale=2400:-2,"
        "zoompan="
        f"z='{z}':"
        f"x='{x}':"
        f"y='{y}':"
        "d=1:"
        f"s={WIDTH}x{HEIGHT}:"
        f"fps={FPS},"
        "setsar=1,"
        "format=yuv420p"
    )

    run([
        "ffmpeg",
        "-y",
        "-loop",
        "1",
        "-i",
        image,
        "-vf",
        vf,
        "-t",
        f"{clip_duration:.3f}",
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
        output,
    ])


# ============================================================
# SCENE
# ============================================================

def create_scene(
    index,
    scene
):

    scene_dir = (
        WORK_DIR /
        f"scene_{index:02d}"
    )

    scene_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    audio = (
        scene_dir /
        "voice.mp3"
    )

    speech_duration = make_voice(
        scene["text"],
        audio
    )

    image_count = max(
        2,
        min(
            4,
            math.ceil(
                speech_duration / 1.9
            )
        )
    )

    visuals = find_visuals(
        scene["queries"],
        image_count,
        index
    )

    # --------------------------------------------------------
    # IMPORTANT:
    # NEVER FAIL THE WHOLE VIDEO BECAUSE
    # ONE SEARCH RETURNED ZERO.
    # --------------------------------------------------------

    if not visuals:

        raise RuntimeError(
            f"No visual source available "
            f"for scene {index}."
        )

    prepared = []

    for n, visual in enumerate(
        visuals
    ):

        raw = (
            scene_dir /
            f"raw_{n:02d}.jpg"
        )

        final_image = (
            scene_dir /
            f"image_{n:02d}.jpg"
        )

        if not download_image(
            visual["url"],
            raw
        ):

            continue

        try:

            prepare_image(
                raw,
                final_image
            )

            prepared.append(
                final_image
            )

            USED_IMAGES.add(
                visual["url"]
            )

            print(
                "VISUAL:",
                visual.get(
                    "title",
                    ""
                )
            )

        except Exception as e:

            print(
                "PREP ERROR:",
                e
            )

    # --------------------------------------------------------
    # Last resort:
    # if one image succeeded, reuse it
    # inside the scene with different motion.
    # --------------------------------------------------------

    if len(prepared) == 0:

        raise RuntimeError(
            f"Could not download any valid "
            f"visual for scene {index}."
        )

    if len(prepared) == 1:

        print(
            "ONLY ONE IMAGE AVAILABLE."
        )

        prepared.append(
            prepared[0]
        )

    # --------------------------------------------------------
    # Create motion clips
    # --------------------------------------------------------

    clips = []

    per_image = (
        speech_duration
        / len(prepared)
    )

    for n, image in enumerate(
        prepared
    ):

        clip = (
            scene_dir /
            f"clip_{n:02d}.mp4"
        )

        create_motion_clip(
            image,
            clip,
            per_image,
            index + n
        )

        clips.append(
            clip
        )

    # --------------------------------------------------------
    # CONCAT VISUALS
    # --------------------------------------------------------

    concat_file = (
        scene_dir /
        "visuals.txt"
    )

    with concat_file.open(
        "w",
        encoding="utf-8"
    ) as f:

        for clip in clips:

            f.write(
                "file '"
                + str(
                    clip.resolve()
                )
                + "'\n"
            )

    visual_video = (
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
        visual_video,
    ])

    # --------------------------------------------------------
    # ATTACH VOICE
    # --------------------------------------------------------

    scene_video = (
        scene_dir /
        "scene.mp4"
    )

    run([
        "ffmpeg",
        "-y",
        "-i",
        visual_video,
        "-i",
        audio,
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
        f"SCENE {index} READY"
    )

    return scene_video


# ============================================================
# BUILD
# ============================================================

def build_all_scenes():

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
            f"SCENE {index}/{len(STORY)}"
        )

        print(
            "=" * 70
        )

        scenes.append(
            create_scene(
                index,
                scene
            )
        )

    return scenes


# ============================================================
# CONCAT ALL
# ============================================================

def concat_all(
    scenes,
    output
):

    concat_file = (
        WORK_DIR /
        "all.txt"
    )

    with concat_file.open(
        "w",
        encoding="utf-8"
    ) as f:

        for scene in scenes:

            f.write(
                "file '"
                + str(
                    scene.resolve()
                )
                + "'\n"
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

    video_filter = (
        f"scale={WIDTH}:{HEIGHT}:"
        "force_original_aspect_ratio=decrease,"
        f"pad={WIDTH}:{HEIGHT}:"
        "(ow-iw)/2:"
        "(oh-ih)/2,"
        "format=yuv420p"
    )

    run([
        "ffmpeg",
        "-y",
        "-i",
        input_video,
        "-vf",
        video_filter,
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
# SIZE
# ============================================================

def compress_if_needed(
    video
):

    size = (
        video.stat().st_size
        / 1024
        / 1024
    )

    print(
        f"VIDEO SIZE: {size:.2f} MB"
    )

    if size <= MAX_VIDEO_MB:

        return

    compressed = (
        WORK_DIR /
        "compressed.mp4"
    )

    print(
        "COMPRESSING..."
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

    shutil.copy2(
        compressed,
        video
    )

    size = (
        video.stat().st_size
        / 1024
        / 1024
    )

    print(
        f"COMPRESSED SIZE: {size:.2f} MB"
    )

    if size > MAX_VIDEO_MB:

        compressed2 = (
            WORK_DIR /
            "compressed2.mp4"
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

        shutil.copy2(
            compressed2,
            video
        )


# ============================================================
# VALIDATE
# ============================================================

def validate(
    video
):

    if not video.exists():

        raise RuntimeError(
            "Final video does not exist."
        )

    d = duration(
        video
    )

    size = (
        video.stat().st_size
        / 1024
        / 1024
    )

    if d < 30:

        raise RuntimeError(
            "Final video is too short."
        )

    if size > MAX_VIDEO_MB:

        raise RuntimeError(
            f"Video exceeds 45 MB: "
            f"{size:.2f} MB"
        )

    print(
        "\n"
        + "=" * 70
    )

    print(
        "FINAL VIDEO VALIDATION: PASS"
    )

    print(
        f"DURATION: {d:.2f}s"
    )

    print(
        f"SIZE: {size:.2f} MB"
    )

    print(
        f"FILE: {video}"
    )

    print(
        "=" * 70
    )


# ============================================================
# CLEAN
# ============================================================

def clean():

    if WORK_DIR.exists():

        shutil.rmtree(
            WORK_DIR
        )

    WORK_DIR.mkdir(
        exist_ok=True
    )

    FINAL_VIDEO.unlink(
        missing_ok=True
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
        "RONALDO — SAUDI ARABIC"
    )

    print(
        "DYNAMIC VISUAL ENGINE"
    )

    print(
        "=" * 70
    )

    clean()

    scenes = build_all_scenes()

    raw = (
        WORK_DIR /
        "complete_raw.mp4"
    )

    concat_all(
        scenes,
        raw
    )

    mastered = (
        WORK_DIR /
        "mastered.mp4"
    )

    master_audio(
        raw,
        mastered
    )

    shutil.copy2(
        mastered,
        FINAL_VIDEO
    )

    compress_if_needed(
        FINAL_VIDEO
    )

    validate(
        FINAL_VIDEO
    )

    print(
        "\n"
        "ACURIVO VIDEO READY."
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