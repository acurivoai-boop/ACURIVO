import subprocess
from pathlib import Path
import urllib.request
import random

OUT = Path("output")
OUT.mkdir(exist_ok=True)

TOPICS = [
    "كيف سيغير الذكاء الاصطناعي حياتنا خلال السنوات القادمة؟",
    "7 وظائف قد يغيرها الذكاء الاصطناعي بشكل جذري",
    "لماذا يفشل بعض الناس رغم أنهم يعملون بجد؟",
    "كيف تتحكم الشركات الكبرى في قرارات المستهلكين؟",
    "أغرب 10 حقائق عن العقل البشري",
    "ماذا يحدث لعقلك عندما تستخدم هاتفك لساعات طويلة؟",
    "كيف يمكن لقرار واحد أن يكلف شركة ملايين الدولارات؟",
    "5 تقنيات ستغير حياتنا في المستقبل القريب",
    "لماذا أصبح بعض الناس مدمنين على وسائل التواصل الاجتماعي؟",
    "أسرار نفسية تجعلك تتخذ قرارات دون أن تشعر",
    "كيف يفكر الأثرياء بطريقة مختلفة؟",
    "ماذا سيحدث إذا أصبح الذكاء الاصطناعي أفضل من البشر في معظم الأعمال؟"
]

topic = random.choice(TOPICS)

SCRIPT = f"""
هل تخيلت يومًا أن قرارًا واحدًا يمكن أن يغير حياتك بالكامل؟

موضوعنا اليوم هو:

{topic}

في السنوات الأخيرة تغير العالم بسرعة مذهلة.
تقنيات جديدة تظهر، وأساليب العمل تتغير،
والطريقة التي نتخذ بها قراراتنا لم تعد كما كانت.

لكن السؤال الحقيقي ليس فقط ماذا يحدث؟

السؤال هو:
لماذا يحدث ذلك؟
وكيف سيؤثر علينا؟

هناك أسباب كثيرة وراء هذه التحولات،
وبعضها قد يكون أقرب إلينا مما نتوقع.

ولهذا سنستعرض في هذا الفيديو أهم الأفكار والحقائق
المرتبطة بهذا الموضوع،
ونحاول أن نفهم الصورة بطريقة بسيطة وممتعة.

وفي النهاية قد تكتشف أن الشيء الذي يبدو عاديًا اليوم
يمكن أن يصبح أحد أكبر التحولات في المستقبل.

إذا أعجبك الموضوع، اشترك في القناة
وفعّل التنبيهات لمشاهدة المزيد من القصص والأفكار.
"""

def run(cmd):
    subprocess.run(cmd, check=True)

def make_voice():
    audio = OUT / "voice.mp3"

    run([
        "python",
        "-m",
        "edge_tts",
        "--voice",
        "ar-SA-HamedNeural",
        "--rate=+5%",
        "--text",
        SCRIPT,
        "--write-media",
        str(audio)
    ])

    return audio

def make_background():
    image = OUT / "background.jpg"

    url = (
        "https://picsum.photos/1920/1080"
        "?random=" + str(random.randint(1, 100000))
    )

    urllib.request.urlretrieve(url, image)

    return image

def make_video(image, audio):
    video = OUT / "ACURIVO_VIDEO.mp4"

    run([
        "ffmpeg",
        "-y",
        "-loop",
        "1",
        "-i",
        str(image),
        "-i",
        str(audio),
        "-vf",
        "scale=1920:1080,"
        "zoompan=z='min(zoom+0.0005,1.08)':"
        "d=1:s=1920x1080:fps=30",
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

def main():
    print("================================")
    print("ACURIVO VIRAL TOPIC FACTORY")
    print("================================")

    print("SELECTED TOPIC:")
    print(topic)

    audio = make_voice()
    image = make_background()
    video = make_video(image, audio)

    print("================================")
    print("VIDEO CREATED")
    print(video)
    print("================================")

if __name__ == "__main__":
    main()
