"""Render stage.html frame by frame and encode the MP4.

    python video/render.py --work DIR                 # all frames, then encode
    python video/render.py --work DIR --from 214      # re-render frames from t=214 s (the end card), then encode
    python video/render.py --work DIR --encode-only   # re-mux after replacing narration.wav
    python video/render.py --work DIR --stills 2,60,120 --no-encode   # QA stills only

Frames are pure functions of time: stage.html exposes renderAt(t), so any range
can be re-rendered and dropped into the frame folder. Team names are read from
data/team.json at render time, if it exists.
"""
import argparse
import asyncio
import json
import math
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
OUT = os.path.join(REPO, "assets", "video")


def load_team():
    p = os.path.join(REPO, "data", "team.json")
    if os.path.exists(p):
        with open(p) as f:
            return json.load(f)
    return None


async def open_page(browser, team):
    page = await browser.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=1)
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    await page.goto("file://" + os.path.join(HERE, "stage.html") + "?t=0")
    await page.evaluate("document.fonts.ready")
    if team:
        await page.evaluate("t => window.setTeam(t)", team)
    missing = await page.evaluate("window.__missingWords")
    if errors or missing:
        raise SystemExit(f"stage errors: {errors} missing words: {missing}")
    return page


async def shoot(page, t, path, quality):
    await page.evaluate(f"window.renderAt({t:.5f})")
    await page.screenshot(path=path, type="jpeg", quality=quality)


async def render(args, frames):
    from playwright.async_api import async_playwright
    team = load_team()
    os.makedirs(args.frames, exist_ok=True)
    async with async_playwright() as p:
        exe = os.environ.get("CHROMIUM") or None   # e.g. /opt/pw-browsers/chromium-1194/chrome-linux/chrome
        browser = await p.chromium.launch(executable_path=exe, args=["--disable-gpu", "--font-render-hinting=none"])
        if args.stills:
            page = await open_page(browser, team)
            os.makedirs(os.path.join(args.work, "stills"), exist_ok=True)
            for t in args.stills:
                path = os.path.join(args.work, "stills", f"still_{t:07.2f}.jpg")
                await shoot(page, t, path, 90)
                print(path)
            if args.poster is not None:
                await shoot(page, args.poster, os.path.join(OUT, "poster.jpg"), 90)
            await browser.close()
            return
        chunks = [frames[k::args.workers] for k in range(args.workers)]
        done = [0]
        t0 = time.time()

        async def worker(idxs):
            page = await open_page(browser, team)
            for i in idxs:
                await shoot(page, i / args.fps, os.path.join(args.frames, f"{i:05d}.jpg"), args.quality)
                done[0] += 1
                if done[0] % 300 == 0:
                    el = time.time() - t0
                    print(f"  {done[0]}/{len(frames)} frames, {done[0] / el:.1f} fps", flush=True)
            await page.close()

        await asyncio.gather(*(worker(c) for c in chunks))
        if args.poster is not None:
            page = await open_page(browser, team)
            await shoot(page, args.poster, os.path.join(OUT, "poster.jpg"), 90)
        await browser.close()


def encode(args, n):
    os.makedirs(OUT, exist_ok=True)
    out = os.path.join(OUT, "surrogate-chain.mp4")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-nostats",
           "-framerate", str(args.fps), "-i", os.path.join(args.frames, "%05d.jpg"),
           "-i", os.path.join(args.work, "narration.wav"),
           "-frames:v", str(n),
           "-c:v", "libx264", "-preset", "slow", "-crf", str(args.crf), "-tune", "animation",
           "-pix_fmt", "yuv420p", "-r", str(args.fps),
           # speech to about -16 LUFS for web playback, peaks held under -1.5 dBTP
           "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "160k", "-ar", "48000",
           "-metadata", "title=How far can a chain of surrogates take us?",
           "-movflags", "+faststart", out]
    subprocess.run(cmd, check=True)
    print(out, f"{os.path.getsize(out) / 1e6:.1f} MB")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", default=os.environ.get("VIDEO_WORK", "/tmp/video-work"))
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--quality", type=int, default=92)
    ap.add_argument("--crf", type=int, default=23)
    ap.add_argument("--from", dest="t_from", type=float, default=0.0)
    ap.add_argument("--to", dest="t_to", type=float, default=None)
    ap.add_argument("--stills", type=lambda s: [float(x) for x in s.split(",")], default=None)
    ap.add_argument("--poster", type=float, default=1.9)
    ap.add_argument("--encode-only", action="store_true")
    ap.add_argument("--no-encode", action="store_true")
    args = ap.parse_args()
    args.frames = os.path.join(args.work, "frames")
    tl = json.load(open(os.path.join(HERE, "timeline.json")))
    n = int(math.ceil(tl["duration"] * args.fps))
    if not args.encode_only:
        i0 = int(args.t_from * args.fps)
        i1 = n if args.t_to is None else min(n, int(math.ceil(args.t_to * args.fps)))
        t = time.time()
        asyncio.run(render(args, list(range(i0, i1))))
        if not args.stills:
            print(f"rendered frames {i0}-{i1 - 1} in {time.time() - t:.0f} s")
    if not args.no_encode and not args.stills:
        missing = [i for i in range(n) if not os.path.exists(os.path.join(args.frames, f"{i:05d}.jpg"))]
        if missing:
            sys.exit(f"{len(missing)} frames missing (first {missing[0]}); render them first")
        encode(args, n)


if __name__ == "__main__":
    main()
