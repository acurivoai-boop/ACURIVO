import subprocess
from pathlib import Path
import urllib.request
import urllib.parse
import json
import random
import re
import time
import shutil

OUT = Path("output")
IMG = OUT / "images"

OUT.mkdir(exist_ok=True)
IMG.mkdir(exist_ok=True)

# المجالات التي يراقبها المصنع
SEARCHES = [
    "AI technology",
    "future technology",
    "business",
    "money",
    "psychology",
    "science",
    "space",
    "health science",
    "human behavior",
    "productivity",
    "innovation",
    "future",
]

def run(cmd):
    print("RUN:", " ".join(cmd))
    subprocess.run(cmd, check=True)

def discover_videos():
    print("=" * 50)
    print("ACURIVO TOPIC SCOUT")
    print("=" * 50)

    results = []

    for query in SEARCHES:
        print("SEARCH:", query)

        try:
            command = [
                "python",
                "-m",
                "yt_dlp",
                "--flat-playlist",
                "--dump-single-json",
                "--playlist-end",
                "10",
                "ytsearch10:" + query
            ]

            output = subprocess.check_output(
                command,
                text=True,
                stderr=subprocess.DEVNULL
            )

            data = json.loads(output)

            for item in data.get("entries", []):
                if not item:
                    continue

                title = item.get("title", "")
                video_id = item.get("id", "")

                if not title:
                    continue

                results.append({
                    "title": title,
                    "id": video_id,
                    "query": query
                })

        except Exception as e:
            print("SEARCH ERROR:", e)

    if not results:
        raise RuntimeError("لم يتم العثور على نتائج YouTube.")

    # إزالة العناوين المتكررة
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
    # نأخذ مجموعة من النتائج القوية ونختار منها عشوائيًا
    # حتى لا ينتج المصنع نفس الموضوع كل يوم.
    candidates = results[:30]

    selected = random.choice(candidates)

    topic = clean_title(selected["title"])

    print("=" * 50)
    print("SELECTED TOPIC")
    print(topic)
    print("SOURCE SEARCH:", selected["query"])
    print("=" * 50)

    return topic, selected


def build_script(topic):
    # سيناريو جديد في كل تشغيل.
    # لا ينسخ الفيديو المصدر ولا يعتمد على نصه.

    openings = [
        f"هناك شيء غريب يحدث الآن حول {topic}...",
        f"قد يبدو {topic} مجرد موضوع عادي، لكن الحقيقة مختلفة تمامًا.",
        f"خلال الفترة الأخيرة بدأ {topic} يجذب اهتمامًا كبيرًا حول العالم.",
        f"تخيل أن ما تعرفه عن {topic} قد يتغير خلال السنوات القادمة.",
        f"لماذا أصبح {topic} موضوعًا يستحق كل هذا الاهتمام؟"
    ]

    angles = [
        "التأثير الحقيقي على حياتنا اليومية",
        "السبب الذي يقف خلف هذا التحول",
        "ما الذي قد يحدث خلال السنوات القادمة",
        "الجانب الذي لا يتحدث عنه الناس كثيرًا",
        "كيف يمكن أن يغير هذا الموضوع طريقة عمل العالم"
    ]

    opening = random.choice(openings)
    angle = random.choice(angles)

    script = f"""
{opening}

موضوعنا اليوم هو:

{topic}

لكننا لن نكتفي بتعريف الموضوع.

سننظر إلى {angle}.

في البداية، يجب أن نفهم لماذا أصبح هذا الموضوع
مهمًا في هذا الوقت تحديدًا.

العالم يتغير بسرعة.
والتقنية والمعلومات والاقتصاد وسلوك الإنسان
أصبحت مترابطة أكثر من أي وقت مضى.

ولهذا فإن بعض الأفكار التي تبدو صغيرة اليوم
يمكن أن تتحول إلى تغييرات كبيرة جدًا غدًا.

في حالة {topic}،
هناك عدة عوامل تستحق الانتباه.

العامل الأول هو سرعة التطور.

العامل الثاني هو حجم التأثير المحتمل
على الأفراد والشركات والمجتمع.

أما العامل الثالث،
فهو أن النتائج قد لا تكون واضحة بالكامل الآن.

وهنا تصبح الصورة أكثر إثارة.

فبدلًا من السؤال:
ماذا يحدث؟

السؤال الأهم هو:

إلى أين يمكن أن يقودنا هذا الاتجاه؟

إذا استمر التطور بنفس السرعة،
فقد نشهد تغيرات كبيرة في طريقة
عمل الناس وتعلمهم واتخاذهم للقرارات.

لكن هناك نقطة مهمة.

لا يعني انتشار فكرة ما أنها ستنجح بالضرورة.

التغيير الحقيقي يحتاج إلى وقت،
وتجربة،
ودليل واضح على القيمة.

ولهذا من المهم ألا ننظر إلى المستقبل
بخوف أو مبالغة.

بل أن نفهم الاتجاه،
ونراقب الأدلة،
ونستعد للفرص والمخاطر.

وفي النهاية،
قد لا يكون السؤال الحقيقي هو:

هل سيتغير العالم؟

بل:

هل سنكون مستعدين عندما يتغير؟

تابع القناة للمزيد من القصص والأفكار
التي تستحق أن تعرفها.
"""

    return script.strip()


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


def make_ai_image(prompt, index):
    filename = IMG / f"scene_{index}.jpg"

    encoded = urllib.parse.quote(prompt, safe="")

    url = (
        "https://image.pollinations.ai/prompt/"
        + encoded
        + "?width=1920&height=1080&nologo=true"
    )

    try:
        urllib.request.urlretrieve(url, filename)

        if filename.exists() and filename.stat().st_size > 1000:
            return filename

    except Exception as e:
        print("IMAGE ERROR:", e)

    return None


def make_scenes(topic):

    visual_styles = [
        "cinematic documentary photography",
        "ultra realistic cinematic scene",
        "premium science documentary",
        "futuristic editorial photography",
        "dramatic realistic documentary"
    ]

    style = random.choice(visual_styles)

    prompts = [
        f"""
        {style},
        visual representation of {topic},
        realistic environment,
        dramatic natural lighting,
        highly detailed,
        professional documentary,
        no text,
        no logos,
        16:9
        """,

        f"""
        {style},
        people interacting with a world affected by {topic},
        realistic human expressions,
        sophisticated composition,
        cinematic lighting,
        no text,
        no logos,
        16:9
        """,

        f"""
        {style},
        conceptual visualization of {topic},
        advanced technology and modern environment,
        realistic details,
        visually spectacular,
        no text,
        no logos,
        16:9
        """,

        f"""
        {style},
        future scenario related to {topic},
        large-scale environment,
        realistic cinematic atmosphere,
        impressive composition,
        no text,
        no logos,
        16:9
        """,

        f"""
        {style},
        close cinematic visualization related to {topic},
        premium documentary quality,
        realistic textures,
        dramatic atmosphere,
        no text,
        no logos,
        16:9
        """
    ]

    images = []

    for i, prompt in enumerate(prompts, 1):

        print(f"GENERATING SCENE {i}/5")

        image = make_ai_image(
            prompt,
            i
        )

        if image:
            images.append(image)

        time.sleep(2)

    if not images:
        raise RuntimeError("لم يتم إنشاء أي مشاهد.")

    return images


def make_video(images, audio):

    video = OUT / "ACURIVO_VIDEO.mp4"
    concat = OUT / "images.txt"

    # مدة المشهد الأساسية
    duration = 8

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
                f"duration {duration}\n"
            )

        # مطلوب لملف concat
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


def clean_old_files():

    if IMG.exists():

        for file in IMG.iterdir():

            if file.is_file():
                try:
                    file.unlink()
                except Exception:
                    pass


def main():

    print("")
    print("=" * 60)
    print("          ACURIVO DAILY AI FACTORY")
    print("=" * 60)
    print("")

    clean_old_files()

    # 1 — اكتشاف مواضيع YouTube
    results = discover_videos()

    # 2 — اختيار موضوع
    topic, source = choose_topic(results)

    save_report(
        topic,
        source
    )

    # 3 — إنشاء سيناريو أصلي
    script = build_script(
        topic
    )

    print("")
    print("ORIGINAL SCRIPT CREATED")
    print("")

    # 4 — تحويل النص إلى صوت
    audio = make_voice(
        script
    )

    # 5 — إنشاء المشاهد
    images = make_scenes(
        topic
    )

    # 6 — إنتاج الفيديو النهائي
    video = make_video(
        images,
        audio
    )

    print("")
    print("=" * 60)
    print("          ACURIVO VIDEO CREATED")
    print("=" * 60)
    print("TOPIC:", topic)
    print("VIDEO:", video)
    print("=" * 60)


if __name__ == "__main__":
    main()