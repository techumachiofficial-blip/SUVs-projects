"""Turn a Techu Machi carousel into an Instagram Reel (1080x1920 MP4).

Usage: python3 tools/reel.py OUT.mp4 SLIDE1.jpg SLIDE2.jpg ... [--label "TECH NEWS"] [--sec 3.5]

Each 1080x1350 slide is centred on a blurred, darkened copy of itself, with a
label at the top and a follow line at the bottom, then joined with crossfades.
A silent audio track is included so Instagram treats it as a normal video;
add trending audio in the Instagram app if you want music.
"""
import os, sys, subprocess, tempfile, argparse
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import techumachi as tm

RW, RH = 1080, 1920
FADE = 0.5


def reel_frame(slide_path, label):
    s = Image.open(slide_path).convert("RGB").resize((tm.W, tm.H))
    # hide the carousel "Swipe >>" hint: it makes no sense in a video
    ImageDraw.Draw(s).rectangle([tm.W - 330, tm.H - 125, tm.W - 40, tm.H - 45], fill=s.getpixel((tm.W - 30, tm.H - 30)))
    # background: slide scaled to fill, blurred and darkened
    scale = RH / s.height
    bg = s.resize((int(s.width * scale), RH)).crop((0, 0, RW, RH)) if s.width * scale >= RW else s.resize((RW, RH))
    bg = ImageEnhance.Brightness(bg.filter(ImageFilter.GaussianBlur(40))).enhance(0.35)
    top = (RH - tm.H) // 2 - 60  # sit slightly above centre: Reels UI covers the bottom
    bg.paste(s, (0, top))
    d = ImageDraw.Draw(bg)
    tm.draw_line(d, label, 0, top - 70, 64, tm.YEL, align="center")
    tm.draw_line(d, "Follow @techumachi for daily tech news", 0, top + tm.H + 90, 40, tm.CYAN, "med", align="center")
    return bg


def make_reel(out, slides, label="TECH NEWS", sec=3.5):
    tmp = tempfile.mkdtemp()
    frames = []
    for i, p in enumerate(slides):
        f = os.path.join(tmp, f"f{i}.png")
        reel_frame(p, label).save(f)
        frames.append(f)
    n = len(frames)
    first = sec + 0.5  # give the hook slide a little longer
    durs = [first] + [sec] * (n - 1)
    durs[-1] += 1.0  # and the last (comment question) slide
    cmd = ["ffmpeg", "-y", "-loglevel", "error"]
    for f, dur in zip(frames, durs):
        cmd += ["-loop", "1", "-framerate", "30", "-t", f"{dur:.2f}", "-i", f]
    total = sum(durs) - FADE * (n - 1)
    cmd += ["-f", "lavfi", "-t", f"{total:.2f}", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100"]
    parts, prev, offset = [], "[0:v]", 0.0
    for i in range(1, n):
        offset += durs[i - 1] - FADE
        lab = f"[v{i}]"
        parts.append(f"{prev}[{i}:v]xfade=transition=fade:duration={FADE}:offset={offset:.2f}{lab}")
        prev = lab
    if n == 1:
        parts.append("[0:v]null[v0]"); prev = "[v0]"
    parts.append(f"{prev}format=yuv420p[vout]")
    cmd += ["-filter_complex", ";".join(parts), "-map", "[vout]", "-map", f"{n}:a",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-r", "30",
            "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", out]
    subprocess.run(cmd, check=True)
    # cover image = first reel frame (jpg) next to the video
    cover = os.path.splitext(out)[0] + "_cover.jpg"
    Image.open(frames[0]).convert("RGB").save(cover, quality=92)
    return out, cover, total


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("slides", nargs="+")
    ap.add_argument("--label", default="TECH NEWS")
    ap.add_argument("--sec", type=float, default=3.5)
    a = ap.parse_args()
    out, cover, total = make_reel(a.out, a.slides, a.label, a.sec)
    print(f"{out} ({total:.1f}s), cover {cover}")
