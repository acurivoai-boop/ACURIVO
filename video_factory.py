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

# المجالات التي يراقبها ACURIVO يوميًا
SEARCHES = [
    "artificial intelligence future",
    "AI tools productivity",
    "business secrets",
    "psychology facts",
    "money business",
    "technology future",
    "science facts",
    "human behavior",
    "success habits",
    "future technology"
]


def run(cmd):
    print("RUN:", " ".join(cmd))
    subprocess.run(cmd, check=True)


def discover_videos():
    print("================================")
    print("ACURIVO TOPIC SCOUT")
    print("================================")

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
                views = item.get("view_count") or 0

                if not title:
                    continue

                results.append({
                    "title": title,
                    "views": int(views),
                    "query": query
                })

        except Exception as e:
            print("SEARCH ERROR:", e)

    if not results:
        raise RuntimeError("لم يتم العثور على نتائج YouTube.")

    # ترتيب حسب المشاهدات
    results.sort(
        key=lambda x: x["views"],
        reverse=True
    )

    return results


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

    return title.strip()


def choose_topic(results):

    # نأخذ أفضل 20 نتيجة
    candidates = results[:20]

    # اختيار من أعلى النتائج مع تنويع بسيط
    top = candidates[:8]

    selected = random.choice(top)

    topic = clean_title(
        selected["title"]
    )

    print("================================")
    print("SELECTED TOPIC")
    print(topic)
    print("VIEWS:", selected["views"])
    print("SOURCE SEARCH:", selected["query"])
    print("================================")

    return topic, selected


def build_script(topic):

    return f"""
تخيل أن هناك فكرة واحدة فقط يمكن أن تغير
طريقة نظرتك إلى العالم.

موضوع اليوم هو:

{topic}

لكن القصة الحقيقية ليست في العنوان فقط.

خلال السنوات الأخيرة ظهرت تغيرات كبيرة
في طريقة تفكير الناس وعمل الشركات
واتخاذ القرارات.

والأمر المثير للاهتمام أن بعض هذه التغيرات
بدأت تظهر أمامنا بالفعل.

في هذا الفيديو سنفهم الفكرة بطريقة بسيطة،
وسنستعرض أهم الأسباب والنتائج،
ثم نصل إلى السؤال الأهم:

ماذا يعني هذا بالنسبة لنا في المستقبل؟

السبب الأول هو أن العالم يتغير بسرعة أكبر
من قدرتنا أحيانًا على ملاحظة ذلك.

والسبب الثاني أن التقنية والمعلومات
أصبحت قادرة على تغيير سلوك ملايين الأشخاص
في وقت قصير جدًا.

أما السبب الثالث،
فهو أن الأشياء التي تبدو صغيرة اليوم
قد تتحول إلى اتجاهات ضخمة غدًا.

ولهذا فإن فهم هذه التحولات مبكرًا
قد يكون أهم بكثير من انتظار حدوثها.

والأهم من كل ذلك:

لا تحاول فقط أن تعرف ماذا يحدث.

حاول أن تفهم لماذا يحدث،
وإلى أين يمكن أن يقودنا.

إذا أعجبك هذا النوع من المحتوى،
اشترك في القناة،
لأننا كل يوم نكتشف فكرة جديدة
قد تغير طريقة رؤيتك للعالم.
"""


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

    encoded = urllib.parse.quote(
        prompt,
        safe=""
    )

    url = (
        "https://image.pollinations.ai/prompt/"
        + encoded
        + "?width=1920&height=1080&nologo=true"
    )

    try:
        urllib.request.urlretrieve(
            url,
            filename
        )

        return filename

    except Exception as e:

        print(
            "IMAGE ERROR:",
            e
        )

        return None


def make_scenes(topic):

    prompts = [
        f"cinematic documentary scene about {topic}, futuristic world, dramatic lighting, ultra realistic, 16:9",
        f"professional documentary visualization of {topic}, modern technology, cinematic photography, 16:9",
        f"people experiencing the impact of {topic}, realistic cinematic scene, dramatic atmosphere, 16:9",
        f"future world related to {topic}, advanced technology, spectacular cinematic environment, 16:9",
        f"conceptual visualization of {topic}, premium documentary style, realistic, cinematic, 16:9"
    ]

    images = []

    for i, prompt in enumerate(prompts, 1):

        print(
            f"GENERATING SCENE {i}/5"
        )

        image = make_ai_image(
            prompt,
            i
        )

        if image:
            images.append(image)

        time.sleep(2)

    if not images:
        raise RuntimeError(
            "لم يتم إنشاء أي مشهد."
        )

    return images


def make_video(images, audio):

    video = OUT / "ACURIVO_VIDEO.mp4"

    # إنشاء ملف concat
    concat = OUT / "images.txt"

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
        "scale=1920:1080,"
        "zoompan=z='min(zoom+0.0004,1.08)':"
        "d=240:s=1920x1080:fps=30",
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
        f"SOURCE VIEWS: {source['views']}\n",
        encoding="utf-8"
    )


def main():

    print("")
    print("======================================")
    print("       ACURIVO DAILY AI FACTORY")
    print("======================================")

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

    print("SCRIPT CREATED")

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
    print("======================================")
    print("        ACURIVO VIDEO CREATED")
    print("======================================")
    print("TOPIC:", topic)
    print("VIDEO:", video)
    print("======================================")


if __name__ == "__main__":
    main()