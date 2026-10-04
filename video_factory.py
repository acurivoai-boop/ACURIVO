import asyncio
import hashlib
import os
import random
import shutil
import subprocess
import sys
from pathlib import Path

import requests
from PIL import Image, ImageOps, ImageEnhance, ImageFilter
import edge_tts
from ddgs import DDGS


# ============================================================
# ACURIVO VIDEO FACTORY
# V11.1 — FIXED DYNAMIC VISUAL ENGINE
# ============================================================

ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "output"
WORK_DIR = ROOT / "work"

OUTPUT_DIR.mkdir(exist_ok=True)
WORK_DIR.mkdir(exist_ok=True)

VIDEO_FILE = OUTPUT_DIR / "ACURIVO_VIDEO.mp4"
AUDIO_RAW = WORK_DIR / "voice_raw.mp3"
AUDIO_FINAL = WORK_DIR / "voice_final.m4a"
CONCAT_FILE = WORK_DIR / "concat.txt"

WIDTH = 1920
HEIGHT = 1080
FPS = 30

MAX_VIDEO_MB = 45

VOICE = "ar-SA-HamedNeural"
VOICE_RATE = "-6%"
VOICE_PITCH = "-1Hz"

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/128.0 Safari/537.36"
)

IMAGE_TIMEOUT = 18
MAX_IMAGE_BYTES = 10 * 1024 * 1024
MIN_IMAGE_BYTES = 20 * 1024

USED_IMAGE_HASHES = set()
USED_IMAGE_URLS = set()

random.seed(42)


# ============================================================
# TITLE
# ============================================================

TITLE = "رونالدو... الطفل الذي رفض أن يكون عاديًا"


# ============================================================
# SCENES
# ============================================================

SCENES = [

    {
        "text": """
تخيل طفل صغير في جزيرة بعيدة، ما عنده ملايين ولا شهرة ولا أحد يعرف اسمه.
لكن عنده شيء أخطر من كل هذا...
إصرار ما يعرف كلمة مستحيل.
هذا هو كريستيانو رونالدو.
الولد اللي بدأ من ماديرا، وانتهى اسمه واحد من أشهر الأسماء في تاريخ كرة القدم.
""",
        "queries": [
            "Cristiano Ronaldo childhood Madeira",
            "Cristiano Ronaldo young childhood",
            "Cristiano Ronaldo Madeira boy football",
        ],
    },

    {
        "text": """
رونالدو ولد في الخامس من فبراير عام ألف وتسعمئة وخمسة وثمانين في جزيرة ماديرا البرتغالية.
ومن وهو صغير، كانت الكرة بالنسبة له أكثر من مجرد لعبة.
كان يلعب في الشوارع، ويتدرب باستمرار، وكان واضح إن عنده شغف مختلف عن اللي حوله.
""",
        "queries": [
            "Cristiano Ronaldo Madeira childhood",
            "Cristiano Ronaldo young boy football",
            "Ronaldo Madeira Portugal childhood",
        ],
    },

    {
        "text": """
ولما وصل عمره حوالي إحدى عشر سنة، اتخذ قرار غيّر حياته بالكامل.
ترك ماديرا وانتقل إلى البر الرئيسي في البرتغال عشان يلعب في أكاديمية سبورتينغ لشبونة.
تخيل طفل بهذا العمر يترك أهله وبيئته وكل شيء يعرفه، ويروح لمكان جديد عشان حلم واحد.
""",
        "queries": [
            "Cristiano Ronaldo Sporting Lisbon academy young",
            "Ronaldo Sporting CP youth",
            "Cristiano Ronaldo Sporting Lisbon teenager",
        ],
    },

    {
        "text": """
هناك بدأت المرحلة الحقيقية.
رونالدو ما كان مجرد موهبة.
كان يتدرب بشكل جنوني، ويركض أكثر، ويحاول يطور نفسه كل يوم.
وكان مستعد يدفع ثمن النجاح من وقته وراحته وحتى حياته الاجتماعية.
""",
        "queries": [
            "Cristiano Ronaldo Sporting training young",
            "Ronaldo Sporting CP training",
            "Cristiano Ronaldo teenager training",
        ],
    },

    {
        "text": """
وبعمر ستة عشر عاما تقريبا، بدأ اسمه يلفت الانتباه.
وبعدها ظهر مع الفريق الأول لسبورتينغ.
السرعة، المهارة، الجرأة...
كلها كانت موجودة.
لكن أهم شيء كان موجود فيه هو الثقة.
""",
        "queries": [
            "Cristiano Ronaldo Sporting CP debut",
            "Cristiano Ronaldo Sporting Lisbon 2002",
            "Ronaldo Sporting young footballer",
        ],
    },

    {
        "text": """
ثم جاء اليوم اللي قلب حياته.
مباراة ودية أمام مانشستر يونايتد.
رونالدو قدم أداء خلّى لاعبي مانشستر يونايتد أنفسهم يتكلمون عنه.
وسرعان ما جاء العرض.
النادي الإنجليزي العريق قرر ياخذ هذا الشاب البرتغالي إلى أولد ترافورد.
""",
        "queries": [
            "Cristiano Ronaldo Manchester United 2003",
            "Ronaldo Manchester United young 2003",
            "Cristiano Ronaldo Old Trafford 2003",
        ],
    },

    {
        "text": """
وهنا بدأت رحلة مختلفة تماما.
في مانشستر يونايتد، كان عنده موهبة كبيرة...
لكن كان يحتاج يتحول من لاعب موهوب إلى لاعب عالمي.
وتحت قيادة السير أليكس فيرغسون، بدأت عملية التحول.
""",
        "queries": [
            "Cristiano Ronaldo Alex Ferguson Manchester United",
            "Ronaldo Ferguson training",
            "Cristiano Ronaldo Manchester United training",
        ],
    },

    {
        "text": """
رونالدو زاد قوته.
طور تسديده.
طور سرعته.
طور لعبه الهوائي.
وتعلم كيف يكون حاسما في المباريات الكبيرة.
وبالتدريج، ما عاد مجرد جناح شاب يستعرض مهاراته...
صار ماكينة أهداف.
""",
        "queries": [
            "Cristiano Ronaldo Manchester United goal celebration",
            "Ronaldo Manchester United goals",
            "Cristiano Ronaldo 2007 2008 Manchester United",
        ],
    },

    {
        "text": """
وفي موسم ألفين وسبعة، ألفين وثمانية، انفجر رونالدو بشكل هائل.
سجل اثنين وأربعين هدفا مع مانشستر يونايتد.
وفاز بدوري أبطال أوروبا.
وفاز بالكرة الذهبية لأول مرة.
الولد اللي ترك ماديرا صار أفضل لاعب في العالم.
""",
        "queries": [
            "Cristiano Ronaldo Ballon d'Or 2008",
            "Ronaldo Champions League 2008 Manchester United",
            "Cristiano Ronaldo 2008 trophy",
        ],
    },

    {
        "text": """
لكن رونالدو ما وقف هنا.
في عام ألفين وتسعة، جاء الانتقال التاريخي إلى ريال مدريد.
صفقة ضخمة، وضغط أكبر، وتوقعات مستحيل ترضيها بسهولة.
لكن رونالدو كان يعرف شيء واحد...
إن المرحلة القادمة لازم تكون أكبر.
""",
        "queries": [
            "Cristiano Ronaldo Real Madrid presentation 2009",
            "Ronaldo Real Madrid 2009 presentation",
            "Cristiano Ronaldo Santiago Bernabeu 2009",
        ],
    },

    {
        "text": """
في ريال مدريد، دخل رونالدو مرحلة جديدة من مسيرته.
أهداف أكثر.
بطولات أكثر.
ليالي أوروبية تاريخية.
ومنافسة مستمرة على القمة.
صار اللاعب اللي الجماهير تنتظر منه شيئا واحدا في كل مباراة...
إنه يحسمها.
""",
        "queries": [
            "Cristiano Ronaldo Real Madrid goal celebration",
            "Ronaldo Real Madrid Champions League",
            "Cristiano Ronaldo Real Madrid trophy",
        ],
    },

    {
        "text": """
ومع السنوات، صار اسمه مرتبطا بدوري أبطال أوروبا.
أهداف حاسمة.
مباريات كبيرة.
ليال ما تنسى.
ورونالدو كان دائما يبحث عن المستوى الأعلى.
حتى لما يوصل للقمة، يبدأ يدور على قمة أعلى.
""",
        "queries": [
            "Cristiano Ronaldo Champions League celebration",
            "Ronaldo Champions League Real Madrid trophy",
            "Cristiano Ronaldo European night",
        ],
    },

    {
        "text": """
وفي عام ألفين وستة عشر، جاء إنجاز مختلف مع منتخب البرتغال.
رونالدو قاد بلاده في بطولة أوروبا، وحقق اللقب القاري.
وهنا اكتملت واحدة من أهم الصور في قصته...
نجم عالمي، وبطل مع ناديه، وبطل مع منتخب بلاده.
""",
        "queries": [
            "Cristiano Ronaldo Portugal Euro 2016",
            "Ronaldo Portugal Euro 2016 trophy",
            "Cristiano Ronaldo Portugal celebration",
        ],
    },

    {
        "text": """
لكن أكثر شيء يميز قصة رونالدو مو عدد الأهداف ولا عدد البطولات.
اللي يميزه هو عقلية المنافسة.
هو دائما يتصرف وكأن عنده شيء لازم يثبته.
حتى بعد كل الإنجازات، التدريب مستمر.
الاهتمام بالتفاصيل مستمر.
والرغبة في الفوز مستمرة.
""",
        "queries": [
            "Cristiano Ronaldo training gym",
            "Cristiano Ronaldo workout",
            "Ronaldo training fitness",
        ],
    },

    {
        "text": """
وهذا بالضبط هو الفرق بين الموهبة والنجاح الحقيقي.
الموهبة ممكن تفتح لك الباب.
لكن الانضباط هو اللي يخليك تستمر داخله.
رونالدو ما اعتمد على موهبته فقط.
كل سنة كان يحاول يصير نسخة أفضل من نفسه.
""",
        "queries": [
            "Cristiano Ronaldo intense training",
            "Ronaldo football training focus",
            "Cristiano Ronaldo gym training",
        ],
    },

    {
        "text": """
من طفل في ماديرا...
إلى أكاديمية سبورتينغ...
إلى مانشستر يونايتد...
إلى ريال مدريد...
إلى قيادة البرتغال.
رحلة طويلة، مليانة ضغط وفشل ونجاح وإصابات وانتقادات.
لكن في كل مرحلة كان يرجع أقوى.
""",
        "queries": [
            "Cristiano Ronaldo career Manchester United Real Madrid Portugal",
            "Cristiano Ronaldo career highlights",
            "Ronaldo football career",
        ],
    },

    {
        "text": """
يمكن عشان كذا قصة رونالدو ما هي مجرد قصة لاعب كرة قدم.
هي قصة شخص قرر من بدري إنه ما يبغى يعيش حياة عادية.
ما كان عنده ضمان إنه راح يوصل.
لكن كان عنده استعداد إنه يحاول مرة ومرتين ومئة مرة.
""",
        "queries": [
            "Cristiano Ronaldo portrait",
            "Cristiano Ronaldo serious portrait",
            "Cristiano Ronaldo stadium portrait",
        ],
    },

    {
        "text": """
واليوم، مهما اختلف الناس عليه، فيه شيء صعب يختلفون عليه.
كريستيانو رونالدو ترك بصمة ضخمة في تاريخ كرة القدم.
بدأ من جزيرة صغيرة...
ووصل إلى أكبر ملاعب العالم.
والقصة كلها بدأت بطفل كان عنده حلم...
ورفض يكون عاديا.
""",
        "queries": [
            "Cristiano Ronaldo iconic celebration",
            "Cristiano Ronaldo stadium celebration",
            "Cristiano Ronaldo iconic portrait",
        ],
    },
]


# ============================================================
# COMMAND
# ============================================================

def run(cmd, check=True):
    print("RUN:", " ".join(str(x) for x in cmd))
    return subprocess.run(
        cmd,
        check=check,
    )


# ============================================================
# DURATION
# ============================================================

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

    return float(
        result.stdout.strip()
    )


# ============================================================
# CLEAN
# ============================================================

def clean_work():

    if WORK_DIR.exists():
        for item in WORK_DIR.iterdir():

            if item.is_dir():
                shutil.rmtree(
                    item,
                    ignore_errors=True,
                )

            else:
                try:
                    item.unlink()
                except Exception:
                    pass


# ============================================================
# VOICE
# ============================================================

async def make_voice(text, output):

    communicate = edge_tts.Communicate(
        text=text,
        voice=VOICE,
        rate=VOICE_RATE,
        pitch=VOICE_PITCH,
    )

    await communicate.save(
        str(output)
    )


def create_voice(text):

    print("CREATING SAUDI ARABIC VOICE...")

    asyncio.run(
        make_voice(
            text,
            AUDIO_RAW,
        )
    )

    if (
        not AUDIO_RAW.exists()
        or AUDIO_RAW.stat().st_size < 10000
    ):
        raise RuntimeError(
            "Voice generation failed."
        )

    print(
        "RAW VOICE SIZE:",
        f"{AUDIO_RAW.stat().st_size / 1024 / 1024:.2f} MB",
    )


def master_voice():

    print("MASTERING VOICE...")

    audio_filter = (
        "highpass=f=65,"
        "lowpass=f=15500,"
        "acompressor="
        "threshold=-20dB:"
        "ratio=2.4:"
        "attack=12:"
        "release=160,"
        "aecho=0.88:0.08:55:0.035,"
        "volume=1.42"
    )

    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(AUDIO_RAW),
            "-af",
            audio_filter,
            "-ar",
            "48000",
            "-ac",
            "2",
            "-c:a",
            "aac",
            "-b:a",
            "160k",
            str(AUDIO_FINAL),
        ]
    )

    print("VOICE MASTERED.")


# ============================================================
# IMAGE SEARCH
# ============================================================

def ddgs_search(query, count=18):

    print(
        f"IMAGE SEARCH: {query}"
    )

    try:

        searcher = DDGS(
            timeout=15,
            verify=True,
        )

        results = searcher.images(
            query=query,
            region="us-en",
            safesearch="moderate",
            max_results=count,
        )

        results = list(results)

        print(
            f"FOUND {len(results)} IMAGE RESULTS"
        )

        return results

    except Exception as e:

        print(
            "DDGS ERROR:",
            str(e),
        )

        return []


# ============================================================
# IMAGE URLS
# ============================================================

def candidate_urls(result):

    urls = []

    for key in (
        "image",
        "thumbnail",
    ):

        value = result.get(key)

        if (
            isinstance(value, str)
            and value.startswith("http")
        ):
            urls.append(value)

    return urls


# ============================================================
# DOWNLOAD IMAGE
# ============================================================

def download_image(url, output):

    try:

        if url in USED_IMAGE_URLS:
            return False

        response = requests.get(
            url,
            headers={
                "User-Agent": USER_AGENT,
                "Accept": (
                    "image/avif,image/webp,"
                    "image/apng,image/svg+xml,"
                    "image/*,*/*;q=0.8"
                ),
            },
            timeout=(
                6,
                IMAGE_TIMEOUT,
            ),
            stream=True,
            allow_redirects=True,
        )

        response.raise_for_status()

        content_type = (
            response.headers
            .get("Content-Type", "")
            .lower()
        )

        data = bytearray()

        for chunk in response.iter_content(
            chunk_size=64 * 1024
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

        digest = hashlib.sha256(
            bytes(data)
        ).hexdigest()

        if digest in USED_IMAGE_HASHES:

            raise RuntimeError(
                "Duplicate image."
            )

        output.write_bytes(
            bytes(data)
        )

        with Image.open(output) as img:
            img.verify()

        with Image.open(output) as img:

            img.load()

            width, height = img.size

            if (
                width < 300
                or height < 300
            ):
                raise RuntimeError(
                    "Image resolution too small."
                )

        USED_IMAGE_URLS.add(url)
        USED_IMAGE_HASHES.add(digest)

        print(
            "IMAGE OK:",
            f"{width}x{height}",
            f"{len(data)/1024/1024:.2f} MB",
        )

        return True

    except Exception as e:

        print(
            "IMAGE FAILED:",
            str(e),
        )

        try:
            output.unlink(
                missing_ok=True
            )
        except Exception:
            pass

        return False


# ============================================================
# DOWNLOAD SEARCH RESULT
# ============================================================

def download_from_result(
    result,
    output,
):

    for url in candidate_urls(result):

        if download_image(
            url,
            output,
        ):
            return True

    return False


# ============================================================
# SEARCH SCENE VISUALS
# ============================================================

def search_scene_images(
    scene_index,
    queries,
    wanted=3,
):

    scene_dir = (
        WORK_DIR /
        f"scene_{scene_index:02d}"
    )

    scene_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    selected = []

    # --------------------------------------------------------
    # Exact searches
    # --------------------------------------------------------

    for query in queries:

        if len(selected) >= wanted:
            break

        results = ddgs_search(
            query,
            18,
        )

        # Larger images first.
        results.sort(
            key=lambda item: (
                (item.get("width") or 0)
                *
                (item.get("height") or 0)
            ),
            reverse=True,
        )

        for result in results:

            if len(selected) >= wanted:
                break

            filename = (
                scene_dir /
                f"img_{len(selected)+1:02d}.jpg"
            )

            if download_from_result(
                result,
                filename,
            ):

                selected.append(
                    filename
                )

    # --------------------------------------------------------
    # General fallback
    # --------------------------------------------------------

    if len(selected) < wanted:

        fallback_queries = [
            "Cristiano Ronaldo football",
            "Cristiano Ronaldo stadium",
            "Cristiano Ronaldo Portugal",
        ]

        for query in fallback_queries:

            if len(selected) >= wanted:
                break

            results = ddgs_search(
                query,
                15,
            )

            for result in results:

                if len(selected) >= wanted:
                    break

                filename = (
                    scene_dir /
                    f"img_{len(selected)+1:02d}.jpg"
                )

                if download_from_result(
                    result,
                    filename,
                ):

                    selected.append(
                        filename
                    )

    print(
        f"SCENE {scene_index}: "
        f"{len(selected)} VISUALS SELECTED"
    )

    return selected


# ============================================================
# PREPARE IMAGE
# ============================================================

def prepare_image(
    source,
    destination,
):

    with Image.open(source) as img:

        img = img.convert("RGB")

        img = ImageOps.fit(
            img,
            (
                WIDTH,
                HEIGHT,
            ),
            method=Image.Resampling.LANCZOS,
            centering=(
                0.5,
                0.5,
            ),
        )

        img = ImageEnhance.Contrast(
            img
        ).enhance(1.06)

        img = ImageEnhance.Color(
            img
        ).enhance(1.04)

        img = img.filter(
            ImageFilter.UnsharpMask(
                radius=1,
                percent=105,
                threshold=3,
            )
        )

        img.save(
            destination,
            "JPEG",
            quality=94,
            optimize=True,
        )


# ============================================================
# DYNAMIC MOTION CLIP
# ============================================================

def create_motion_clip(
    image_path,
    output_path,
    duration,
    motion_index,
):

    prepared = (
        image_path.parent /
        f"prepared_{image_path.stem}.jpg"
    )

    prepare_image(
        image_path,
        prepared,
    )

    # IMPORTANT:
    # These are numeric values.
    # No string multiplication.
    motions = [
        {
            "zoom": 0.00035,
            "x": 0.00018,
            "y": 0.00000,
        },
        {
            "zoom": 0.00045,
            "x": -0.00018,
            "y": 0.00004,
        },
        {
            "zoom": -0.00030,
            "x": 0.00016,
            "y": -0.00005,
        },
        {
            "zoom": 0.00030,
            "x": -0.00016,
            "y": -0.00004,
        },
        {
            "zoom": -0.00025,
            "x": 0.00012,
            "y": 0.00005,
        },
        {
            "zoom": 0.00040,
            "x": -0.00012,
            "y": 0.00003,
        },
    ]

    motion = motions[
        motion_index % len(motions)
    ]

    frames = max(
        30,
        int(
            duration * FPS
        ),
    )

    zoom_step = motion["zoom"]
    x_step = motion["x"]
    y_step = motion["y"]

    # Build expressions as strings ONLY
    # for FFmpeg. Mathematical values
    # themselves remain numeric above.

    if zoom_step >= 0:

        zoom_expr = (
            f"min(zoom+{zoom_step},1.12)"
        )

    else:

        zoom_expr = (
            f"max(zoom{zoom_step},1.00)"
        )

    x_expr = (
        "iw/2-(iw/zoom/2)"
        f"+({x_step})*on*iw"
    )

    y_expr = (
        "ih/2-(ih/zoom/2)"
        f"+({y_step})*on*ih"
    )

    filter_complex = (
        "scale=2400:-2,"
        "zoompan="
        f"z='{zoom_expr}':"
        f"x='{x_expr}':"
        f"y='{y_expr}':"
        f"d={frames}:"
        f"s={WIDTH}x{HEIGHT}:"
        f"fps={FPS},"
        "format=yuv420p"
    )

    run(
        [
            "ffmpeg",
            "-y",
            "-loop",
            "1",
            "-i",
            str(prepared),
            "-vf",
            filter_complex,
            "-t",
            f"{duration:.3f}",
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "22",
            "-pix_fmt",
            "yuv420p",
            str(output_path),
        ]
    )


# ============================================================
# BUILD VIDEO
# ============================================================

def build_video():

    print(
        "ANALYZING AUDIO DURATION..."
    )

    audio_duration = (
        ffprobe_duration(
            AUDIO_FINAL
        )
    )

    print(
        f"AUDIO DURATION: "
        f"{audio_duration:.2f} seconds"
    )

    weights = [
        max(
            1,
            len(scene["text"]),
        )
        for scene in SCENES
    ]

    total_weight = sum(
        weights
    )

    scene_durations = [
        audio_duration
        * weight
        / total_weight
        for weight in weights
    ]

    all_clips = []

    for index, (
        scene,
        duration,
    ) in enumerate(
        zip(
            SCENES,
            scene_durations,
        ),
        start=1,
    ):

        print()
        print(
            "=" * 70
        )

        print(
            f"SCENE {index}/"
            f"{len(SCENES)} "
            f"DURATION "
            f"{duration:.2f}s"
        )

        print(
            "=" * 70
        )

        wanted = (
            3
            if duration >= 8
            else 2
        )

        images = search_scene_images(
            index,
            scene["queries"],
            wanted=wanted,
        )

        if not images:

            raise RuntimeError(
                "No usable visual found "
                f"for scene {index}."
            )

        # Never leave a scene completely static.
        if len(images) == 1:

            images = [
                images[0],
                images[0],
            ]

        image_duration = (
            duration /
            len(images)
        )

        for img_index, image in enumerate(
            images
        ):

            clip = (
                WORK_DIR /
                f"scene_{index:02d}_"
                f"clip_{img_index:02d}.mp4"
            )

            create_motion_clip(
                image,
                clip,
                image_duration,
                index + img_index,
            )

            all_clips.append(
                clip
            )

    print(
        "CREATING CONCAT LIST..."
    )

    with open(
        CONCAT_FILE,
        "w",
        encoding="utf-8",
    ) as f:

        for clip in all_clips:

            path = str(
                clip.resolve()
            )

            path = path.replace(
                "'",
                "'\\''",
            )

            f.write(
                f"file '{path}'\n"
            )

    silent_video = (
        WORK_DIR /
        "silent_video.mp4"
    )

    print(
        "JOINING VISUAL CLIPS..."
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
            str(CONCAT_FILE),
            "-c",
            "copy",
            "-movflags",
            "+faststart",
            str(silent_video),
        ]
    )

    print(
        "ADDING MASTERED VOICE..."
    )

    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(silent_video),
            "-i",
            str(AUDIO_FINAL),
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "25",
            "-maxrate",
            "2400k",
            "-bufsize",
            "4800k",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "160k",
            "-ar",
            "48000",
            "-shortest",
            "-movflags",
            "+faststart",
            str(VIDEO_FILE),
        ]
    )

    if not VIDEO_FILE.exists():

        raise RuntimeError(
            "Final video was not created."
        )

    size_mb = (
        VIDEO_FILE.stat().st_size
        / 1024
        / 1024
    )

    print(
        f"FINAL VIDEO SIZE: "
        f"{size_mb:.2f} MB"
    )

    # ========================================================
    # COMPRESS IF OVER 45 MB
    # ========================================================

    if size_mb > MAX_VIDEO_MB:

        print(
            "VIDEO ABOVE 45 MB — "
            "COMPRESSING..."
        )

        duration = (
            ffprobe_duration(
                VIDEO_FILE
            )
        )

        total_bps = (
            MAX_VIDEO_MB
            * 1024
            * 1024
            * 8
            / max(
                duration,
                1,
            )
        )

        video_bps = max(
            850000,
            int(
                total_bps * 0.82
            ),
        )

        compressed = (
            WORK_DIR /
            "ACURIVO_VIDEO_COMPRESSED.mp4"
        )

        run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(VIDEO_FILE),
                "-c:v",
                "libx264",
                "-preset",
                "medium",
                "-b:v",
                str(video_bps),
                "-maxrate",
                str(
                    int(
                        video_bps
                        * 1.15
                    )
                ),
                "-bufsize",
                str(
                    int(
                        video_bps
                        * 2.0
                    )
                ),
                "-pix_fmt",
                "yuv420p",
                "-c:a",
                "aac",
                "-b:a",
                "128k",
                "-movflags",
                "+faststart",
                str(compressed),
            ]
        )

        compressed.replace(
            VIDEO_FILE
        )

    final_size = (
        VIDEO_FILE.stat().st_size
        / 1024
        / 1024
    )

    print()
    print(
        "=" * 70
    )
    print(
        "ACURIVO VIDEO COMPLETE"
    )
    print(
        "=" * 70
    )
    print(
        f"TITLE: {TITLE}"
    )
    print(
        f"SIZE: {final_size:.2f} MB"
    )
    print(
        f"DURATION: "
        f"{ffprobe_duration(VIDEO_FILE):.2f} sec"
    )
    print(
        f"FILE: {VIDEO_FILE}"
    )
    print(
        "=" * 70
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print(
        "=" * 70
    )
    print(
        "ACURIVO VIDEO FACTORY V11.1"
    )
    print(
        "=" * 70
    )
    print(
        "TOPIC:",
        TITLE,
    )
    print(
        "=" * 70
    )

    clean_work()

    full_text = "\n\n".join(
        scene["text"].strip()
        for scene in SCENES
    )

    create_voice(
        full_text
    )

    master_voice()

    build_video()

    print()
    print(
        "ACURIVO FACTORY "
        "FINISHED SUCCESSFULLY."
    )


if __name__ == "__main__":

    try:

        main()

    except Exception as e:

        print()
        print(
            "FATAL ERROR:"
        )

        print(
            str(e)
        )

        sys.exit(1)