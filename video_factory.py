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
]

BLOCKED = [
    "life update", "vlog", "my life", "we moved", "my family",
    "wedding", "birthday", "personal", "daily vlog", "house tour"
]

def run(cmd):
    subprocess.run(cmd, check=True)

def discover_videos():
    results = []

    for query in SEARCHES:
        try:
            out = subprocess.check_output(
                [
                    "python", "-m", "yt_dlp",
                    "--flat-playlist",
                    "--dump-single-json",
                    "--playlist-end", "10",
                    "ytsearch10:" + query
                ],
                text=True,
                stderr=subprocess.DEVNULL
            )

            data = json.loads(out)

            for item in data.get("entries", []):
                if not item:
                    continue

                title = item.get("title", "").strip()

                if not title:
                    continue

                low = title.lower()

                if any(x in low for x in BLOCKED):
                    continue

                results.append({
                    "title": title,
                    "id": item.get("id", ""),
                    "query": query
                })

        except Exception as e:
            print("SEARCH ERROR:", e)

    if not results:
        raise RuntimeError("لم يتم العثور على موضوع مناسب.")

    unique = {}

    for item in results:
        key = re.sub(r"\s+", " ", item["title"].lower()).strip()
        unique[key] = item

    results = list(unique.values())

    print("FOUND:", len(results), "VIDEOS")

    return results


def clean_title(title):
    title = re.sub(r"\[[^\]]*\]", "", title)
    title = re.sub(r"\([^)]*\)", "", title)
    title = re.sub(r"#\w+", "", title)
    title = re.sub(r"\s+", " ", title)
    return title.strip(" -|")


def choose_topic(results):
    # نفضل المواضيع التقنية والعلمية
    random.shuffle(results)

    for item in results:
        topic = clean_title(item["title"])

        if len(topic) >= 15:
            print("=" * 50)
            print("SELECTED TOPIC")
            print(topic)
            print("SOURCE:", item["query"])
            print("=" * 50)

            return topic, item

    return clean_title(results[0]["title"]), results[0]


def build_script(topic):
    return f"""
هناك اتجاه جديد يستحق الانتباه.

موضوعنا اليوم هو:

{topic}

لكن السؤال الأهم ليس فقط ماذا يحدث،
بل لماذا يحدث الآن؟

خلال السنوات الأخيرة أصبح العالم يتغير بسرعة
غير مسبوقة.

التقنية والعلوم والاقتصاد وسلوك الإنسان
أصبحت مترابطة بشكل أكبر.

وهذا يعني أن بعض التطورات التي تبدو صغيرة
اليوم يمكن أن يكون لها تأثير كبير غدًا.

في موضوع {topic}،
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
""".strip()


def make_voice(script):
    audio = OUT / "voice.mp3"

    run([
        "python", "-m", "edge_tts",
        "--voice", "ar-SA-HamedNeural",
        "--rate=+3%",
        "--text", script,
        "--write-media", str(audio)
    ])

    return audio


def make_image(prompt, index):
    filename = IMG / f"scene_{index}.jpg"

    url = (
        "https://loremflickr.com/1920/1080/"
        + urllib.parse.quote(prompt)
        + "?lock=" + str(random.randint(1, 999999))
    )

    try:
        urllib.request.urlretrieve(url, filename)

        if filename.exists() and filename.stat().st_size > 10000:
            return filename

    except Exception as e:
        print("IMAGE ERROR:", e)

    return None


def make_scenes(topic):
    prompts = [
        f"{topic}, technology, futuristic, cinematic",
        f"{topic}, science, realistic documentary",
        f"{topic}, modern world, cinematic photography",
        f"{topic}, innovation, dramatic realistic scene",
        f"{topic}, future, premium documentary photography"
    ]

    images = []

    for i, prompt in enumerate(prompts, 1):
        print(f"GENERATING SCENE {i}/5")

        image = make_image(prompt, i)

        if image:
            images.append(image)

        time.sleep(2)

    if not images:
        raise RuntimeError("تعذر الحصول على أي صور مجانية.")

    return images


def make_video(images, audio):
    video = OUT / "ACURIVO_VIDEO.mp4"
    concat = OUT / "images.txt"

    with open(concat, "w", encoding="utf-8") as f:
        for image in images:
            f.write(f"file '{image.resolve()}'\n")
            f.write("duration 8\n")

        f.write(f"file '{images[-1].resolve()}'\n")

    run([
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat),
        "-i", str(audio),
        "-vf",
        "scale=1920:1080,"
        "zoompan=z='min(zoom+0.0004,1.08)':"
        "d=240:s=1920x1080:fps=30",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        str(video)
    ])

    return video


def main():
    print("=" * 60)
    print("ACURIVO DAILY AI FACTORY")
    print("=" * 60)

    results = discover_videos()

    topic, source = choose_topic(results)

    script = build_script(topic)

    audio = make_voice(script)

    images = make_scenes(topic)

    video = make_video(images, audio)

    print("=" * 60)
    print("VIDEO CREATED SUCCESSFULLY")
    print("TOPIC:", topic)
    print("VIDEO:", video)
    print("=" * 60)


if __name__ == "__main__":
    main()