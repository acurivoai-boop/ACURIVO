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
# ACURIVO TOPIC ENGINE
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
    "future science"
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
    "travel vlog"
]


def run(cmd):
    print("RUN:", " ".join(str(x) for x in cmd))
    subprocess.run(cmd, check=True)


# ============================================================
# SEARCH YOUTUBE
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

                if any(word in low for word in BLOCKED):
                    continue

                results.append({
                    "title": title,
                    "id": item.get("id", ""),
                    "query": query
                })

        except Exception as e:

            print("SEARCH ERROR:", e)

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

    print("FOUND:", len(results), "VIDEOS")

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
# CHOOSE TOPIC
# ============================================================

def choose_topic(results):

    random.shuffle(results)

    for item in results:

        topic = clean_title(
            item["title"]
        )

        if len(topic) < 15:
            continue

        print("=" * 60)
        print("SELECTED TOPIC")
        print(topic)
        print("SOURCE:", item["query"])
        print("=" * 60)

        return topic, item

    item = results[0]

    return clean_title(
        item["title"]
    ), item


# ============================================================
# SCRIPT
# ============================================================

def build_script(topic):

    script = f"""
هناك اتجاه جديد يستحق الانتباه.

موضوعنا اليوم هو:

{topic}

لكن السؤال الأهم ليس فقط ماذا يحدث،
بل لماذا يحدث الآن؟

خلال السنوات الأخيرة أصبح العالم يتغير بسرعة
غير مسبوقة.

التقنية والعلوم والاقتصاد وسلوك الإنسان
أصبحت مترابطة أكثر من أي وقت مضى.

وفي موضوع {topic}،
هناك عدة نقاط تستحق التوقف عندها.

أولًا، سرعة التطور أصبحت عاملًا أساسيًا.

ثانيًا، حجم التأثير المحتمل أصبح أكبر.

وثالثًا، ما زالت هناك أسئلة كثيرة
لم تحصل على إجابات نهائية.

وهنا تبدأ القصة الحقيقية.

إذا استمر هذا الاتجاه،
فقد تتغير طريقة عملنا وتعلمنا
واتخاذنا للقرارات.

لكن من المهم أن نفرق بين التوقع
والحقيقة.

النجاح الحقيقي يحتاج إلى دليل،
وتجربة،
وقيمة يمكن قياسها.

لذلك لا يتعلق الأمر بالخوف من المستقبل،
بل بفهم الاتجاهات والاستعداد لها.

والسؤال الذي يستحق التفكير هو:

إلى أين يمكن أن يقودنا هذا التطور؟

تابع ACURIVO للمزيد من القصص
والأفكار التي تستحق أن تعرفها.
"""

    return script.strip()


# ============================================================
# VOICE
# ============================================================

def make_voice(script):

    audio = OUT / "voice.mp3"

    run([
        "python",
        "-m",
        "edge_tts",
        "--voice",
        "ar-SA-HamedNeural",
        "--rate=+3%",
        "--text",
        script,
        "--write-media",
        str(audio)
    ])

    return audio


# ============================================================
# FREE IMAGE SOURCE
# ============================================================

def make_image(prompt, index):

    filename = IMG / f"scene_{index}.jpg"

    # Picsum لا يحتاج API Key أو تسجيل دخول
    url = (
        "https://picsum.photos/1920/1080?random="
        + str(int(time.time() * 1000) + index)
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

        f"{topic} technology futuristic",

        f"{topic} science documentary",

        f"{topic} modern world",

        f"{topic} innovation",

        f"{topic} future technology"

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
# VIDEO
# ============================================================

def make_video(images, audio):

    video = OUT / "ACURIVO_VIDEO.mp4"

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
                "duration 8\n"
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

def save_report(topic, source):

    report = OUT / "topic_report.txt"

    report.write_text(
        "ACURIVO DAILY TOPIC\n\n"
        f"TOPIC: {topic}\n"
        f"SOURCE SEARCH: {source['query']}\n"
        f"SOURCE TITLE: {source['title']}\n"
        f"VIDEO ID: {source.get('id', '')}\n",
        encoding="utf-8"
    )


# ============================================================
# CLEAN OLD IMAGES
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

    topic, source = choose_topic(
        results
    )

    save_report(
        topic,
        source
    )

    script = build_script(
        topic
    )

    print("")
    print("ORIGINAL SCRIPT CREATED")
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
    print("TOPIC:", topic)
    print("VIDEO:", video)
    print("=" * 60)


if __name__ == "__main__":

    main()