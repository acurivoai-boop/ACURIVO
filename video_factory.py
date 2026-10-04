import subprocess
from pathlib import Path
import urllib.request
import urllib.parse
import json
import random
import re
import time

OUT = Path("output")
IMG = OUT / "images"

OUT.mkdir(exist_ok=True)
IMG.mkdir(exist_ok=True)

# ============================================================
# ACURIVO DAILY AI FACTORY
# ============================================================

SEARCHES = [
    "AI technology news",
    "future technology",
    "science discovery",
    "space discovery",
    "business innovation",
    "psychology science",
    "future of work",
    "medical technology",
    "energy technology",
    "robotics",
    "artificial intelligence",
    "future science",
    "technology explained",
    "science explained"
]

BLOCKED = [
    "life update",
    "vlog",
    "my life",
    "we moved",
    "my family",
    "wedding",
    "birthday",
    "personal",
    "daily vlog",
    "house tour",
    "room tour",
    "travel vlog",
    "reaction",
    "prank",
    "challenge",
    "celebrity gossip"
]


def run(cmd):
    print("RUN:", " ".join(str(x) for x in cmd))
    subprocess.run(cmd, check=True)


# ============================================================
# DISCOVER TOPICS
# ============================================================

def discover_videos():

    print("=" * 60)
    print("ACURIVO TOPIC SCOUT")
    print("=" * 60)

    results = []

    for query in SEARCHES:

        print("SEARCH:", query)

        try:

            output = subprocess.check_output(
                [
                    "python",
                    "-m",
                    "yt_dlp",
                    "--flat-playlist",
                    "--dump-single-json",
                    "--playlist-end",
                    "10",
                    "ytsearch10:" + query
                ],
                text=True,
                stderr=subprocess.DEVNULL
            )

            data = json.loads(output)

            for item in data.get("entries", []):

                if not item:
                    continue

                title = item.get("title", "").strip()

                if not title:
                    continue

                low = title.lower()

                if any(
                    word in low
                    for word in BLOCKED
                ):
                    continue

                results.append({
                    "title": title,
                    "id": item.get("id", ""),
                    "query": query
                })

        except Exception as e:

            print(
                "SEARCH ERROR:",
                e
            )

    if not results:

        raise RuntimeError(
            "لم يتم العثور على مواضيع مناسبة."
        )

    unique = {}

    for item in results:

        key = re.sub(
            r"\s+",
            " ",
            item["title"].lower()
        ).strip()

        unique[key] = item

    results = list(unique.values())

    print(
        "FOUND:",
        len(results),
        "VIDEOS"
    )

    return results


# ============================================================
# CLEAN TITLE
# ============================================================

def clean_title(title):

    title = re.sub(
        r"\[[^\]]*\]",
        "",
        title
    )

    title = re.sub(
        r"\([^)]*\)",
        "",
        title
    )

    title = re.sub(
        r"#\w+",
        "",
        title
    )

    title = re.sub(
        r"\s+",
        " ",
        title
    )

    return title.strip(" -|")


# ============================================================
# TRANSLATE TOPIC TO ARABIC
# ============================================================

def translate_to_arabic(text):

    print("")
    print(
        "TRANSLATING TOPIC TO ARABIC..."
    )

    print(
        "ORIGINAL:",
        text
    )

    try:

        params = urllib.parse.urlencode({
            "client": "gtx",
            "sl": "auto",
            "tl": "ar",
            "dt": "t",
            "q": text
        })

        url = (
            "https://translate.googleapis.com/"
            "translate_a/single?"
            + params
        )

        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        with urllib.request.urlopen(
            request,
            timeout=30
        ) as response:

            data = json.loads(
                response.read().decode(
                    "utf-8"
                )
            )

        translated = ""

        for part in data[0]:

            if part and part[0]:
                translated += part[0]

        translated = re.sub(
            r"\s+",
            " ",
            translated
        ).strip()

        if translated:

            print(
                "ARABIC TOPIC:",
                translated
            )

            return translated

    except Exception as e:

        print(
            "TRANSLATION ERROR:",
            e
        )

    return text


# ============================================================
# SELECT TOPIC
# ============================================================

def choose_topic(results):

    random.shuffle(results)

    for item in results:

        original = clean_title(
            item["title"]
        )

        if len(original) < 15:
            continue

        arabic = translate_to_arabic(
            original
        )

        if len(arabic) < 8:
            continue

        print("=" * 60)
        print("SELECTED TOPIC")
        print(
            "ORIGINAL:",
            original
        )
        print(
            "ARABIC:",
            arabic
        )
        print(
            "SOURCE:",
            item["query"]
        )
        print("=" * 60)

        return (
            arabic,
            original,
            item
        )

    item = results[0]

    original = clean_title(
        item["title"]
    )

    arabic = translate_to_arabic(
        original
    )

    return (
        arabic,
        original,
        item
    )


# ============================================================
# ORIGINAL ARABIC SCRIPT
# ============================================================

def build_script(topic):

    script = f"""
هناك تطور جديد يستحق الانتباه.

موضوعنا اليوم هو:

{topic}

قد يبدو هذا الموضوع في البداية مجرد خبر أو فكرة جديدة،
لكن عند النظر إليه بصورة أعمق،
سنجد أن وراءه مجموعة من التغيرات المهمة.

خلال السنوات الأخيرة،
تسارعت وتيرة التغيير في العالم بشكل كبير.

التقنية تتطور،
والعلوم تتقدم،
والاقتصاد يتغير،
وطريقة تعامل الإنسان مع المعلومات أصبحت مختلفة.

ولهذا أصبحت بعض الموضوعات التي كانت تبدو بعيدة
عن حياتنا اليومية مرتبطة بنا أكثر مما نتوقع.

أما في موضوع {topic}،
فالسؤال المهم ليس فقط:

ماذا يحدث؟

بل السؤال الأهم:

لماذا يحدث هذا الآن؟

هناك عدة عوامل تساعد على فهم الصورة.

أول هذه العوامل هو التطور السريع.

فعندما تتطور المعرفة والتقنية بسرعة،
يمكن لفكرة صغيرة أن تتحول خلال فترة قصيرة
إلى اتجاه واسع له تأثير كبير.

العامل الثاني هو حجم التأثير.

فبعض التطورات لا تؤثر في مجال واحد فقط،
بل يمكن أن تمتد آثارها إلى الشركات،
والوظائف،
والتعليم،
والاقتصاد،
وحياة الناس اليومية.

أما العامل الثالث،
فهو أن النتائج النهائية لا تكون واضحة منذ البداية.

وهنا يجب أن نكون حذرين.

ليس كل اتجاه جديد يعني بالضرورة
أن العالم سيتغير بالطريقة التي يتوقعها الناس.

هناك فرق بين التوقع،
وبين ما تثبته التجارب والأدلة.

ولهذا فإن أفضل طريقة لفهم المستقبل
هي مراقبة التطورات،
ومقارنة النتائج،
والبحث عن الأدلة الحقيقية.

وفي حالة {topic}،
قد يكون التأثير الحقيقي أكبر من مجرد الخبر الحالي.

فإذا استمر هذا الاتجاه،
فقد نرى تغيرات جديدة خلال السنوات القادمة.

وقد تظهر فرص جديدة،
وفي الوقت نفسه قد تظهر تحديات لم تكن واضحة من قبل.

والأهم أن نفهم أن التغيير لا يحدث في لحظة واحدة.

غالبًا يبدأ بفكرة،
ثم تجربة،
ثم تطبيق محدود،
وبعد ذلك يبدأ التأثير في الانتشار.

وهذا ما يجعل متابعة التطورات العلمية والتقنية
أمرًا مهمًا لكل شخص يريد أن يفهم المستقبل.

فما نراه اليوم قد يكون مجرد بداية.

وقد تتغير طريقة عملنا،
وطريقة تعلمنا،
وطريقة اتخاذنا للقرارات،
بناءً على تطورات تبدو الآن في بدايتها.

لكن لا يمكننا معرفة المستقبل بشكل كامل.

ولهذا من الأفضل أن نفرق دائمًا بين الحقيقة،
والتوقع،
والاحتمال.

المعلومة الموثوقة تساعدنا على فهم الواقع،
أما التوقع فيعطينا سيناريوهات محتملة،
والقرار الذكي يحتاج إلى الجمع بين الاثنين.

وفي النهاية،
السؤال ليس:

هل سيتغير العالم؟

لأن العالم يتغير بالفعل.

السؤال الحقيقي هو:

إلى أي اتجاه يسير هذا التغيير؟

ومن سيكون مستعدًا عندما تظهر نتائجه؟

ربما تكون الإجابة أهم مما نتوقع.

تابع ACURIVO للمزيد من القصص
والأفكار والتطورات التي تستحق أن تعرفها.
"""

    return script.strip()


# ============================================================
# ARABIC VOICE
# ============================================================

def make_voice(script):

    audio = OUT / "voice.mp3"

    run([
        "python",
        "-m",
        "edge_tts",
        "--voice",
        "ar-SA-HamedNeural",
        "--rate=+0%",
        "--text",
        script,
        "--write-media",
        str(audio)
    ])

    return audio


# ============================================================
# AUDIO DURATION
# ============================================================

def get_audio_duration(audio):

    output = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(audio)
        ],
        text=True
    )

    duration = float(
        output.strip()
    )

    print(
        "AUDIO DURATION:",
        round(duration, 2),
        "SECONDS"
    )

    return duration


# ============================================================
# FREE IMAGE SOURCE
# ============================================================

def make_image(prompt, index):

    filename = IMG / f"scene_{index}.jpg"

    url = (
        "https://picsum.photos/1920/1080?random="
        + str(
            int(time.time() * 1000)
            + index
        )
    )

    try:

        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        with urllib.request.urlopen(
            request,
            timeout=30
        ) as response:

            data = response.read()

        with open(
            filename,
            "wb"
        ) as f:

            f.write(data)

        if (
            filename.exists()
            and filename.stat().st_size > 10000
        ):

            print(
                "IMAGE READY:",
                filename
            )

            return filename

    except Exception as e:

        print(
            "IMAGE ERROR:",
            e
        )

    return None


# ============================================================
# CREATE SCENES
# ============================================================

def make_scenes(topic):

    prompts = [
        f"{topic} technology",
        f"{topic} science",
        f"{topic} modern world",
        f"{topic} innovation",
        f"{topic} future"
    ]

    images = []

    for i, prompt in enumerate(
        prompts,
        1
    ):

        print(
            f"GENERATING SCENE {i}/5"
        )

        image = make_image(
            prompt,
            i
        )

        if image:
            images.append(image)

        time.sleep(1)

    if not images:

        raise RuntimeError(
            "تعذر الحصول على صور مجانية."
        )

    print(
        "TOTAL IMAGES:",
        len(images)
    )

    return images


# ============================================================
# BUILD VIDEO
# ============================================================

def make_video(images, audio):

    video = OUT / "ACURIVO_VIDEO.mp4"

    audio_duration = get_audio_duration(
        audio
    )

    image_duration = (
        audio_duration / len(images)
    )

    print(
        "IMAGE DURATION:",
        round(
            image_duration,
            2
        ),
        "SECONDS"
    )

    concat = OUT / "images.txt"

    with open(
        concat,
        "w",
        encoding="utf-8"
    ) as f:

        for image in images:

            f.write(
                f"file '{image.resolve()}'\n"
            )

            f.write(
                f"duration {image_duration:.3f}\n"
            )

        f.write(
            f"file '{images[-1].resolve()}'\n"
        )

    run([
        "ffmpeg",
        "-y",

        "-f",
        "concat",

        "-safe",
        "0",

        "-i",
        str(concat),

        "-i",
        str(audio),

        "-vf",
        (
            "scale=1920:1080,"
            "zoompan="
            "z='min(zoom+0.0004,1.08)':"
            "d=240:"
            "s=1920x1080:"
            "fps=30"
        ),

        "-t",
        str(audio_duration + 0.5),

        "-c:v",
        "libx264",

        "-preset",
        "veryfast",

        "-pix_fmt",
        "yuv420p",

        "-c:a",
        "aac",

        "-b:a",
        "192k",

        "-shortest",

        str(video)
    ])

    return video


# ============================================================
# REPORT
# ============================================================

def save_report(
    topic,
    original,
    source
):

    report = OUT / "topic_report.txt"

    report.write_text(
        "ACURIVO DAILY TOPIC\n\n"
        f"ARABIC TOPIC: {topic}\n"
        f"ORIGINAL TOPIC: {original}\n"
        f"SOURCE SEARCH: {source['query']}\n"
        f"SOURCE TITLE: {source['title']}\n"
        f"VIDEO ID: {source.get('id', '')}\n",
        encoding="utf-8"
    )


# ============================================================
# CLEAN OLD FILES
# ============================================================

def clean_old_files():

    if IMG.exists():

        for file in IMG.iterdir():

            if file.is_file():

                try:
                    file.unlink()
                except Exception:
                    pass


# ============================================================
# MAIN
# ============================================================

def main():

    print("")
    print("=" * 60)
    print("          ACURIVO DAILY AI FACTORY")
    print("=" * 60)
    print("")

    clean_old_files()

    results = discover_videos()

    topic, original, source = choose_topic(
        results
    )

    save_report(
        topic,
        original,
        source
    )

    script = build_script(
        topic
    )

    print("")
    print(
        "ORIGINAL ARABIC SCRIPT CREATED"
    )
    print("")

    audio = make_voice(
        script
    )

    images = make_scenes(
        topic
    )

    video = make_video(
        images,
        audio
    )

    print("")
    print("=" * 60)
    print("       ACURIVO VIDEO CREATED")
    print("=" * 60)
    print(
        "TOPIC:",
        topic
    )
    print(
        "VIDEO:",
        video
    )
    print("=" * 60)


if __name__ == "__main__":

    main()