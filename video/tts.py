"""Narration -> per-sentence audio, timeline.json and data.js.

    python video/tts.py [--work DIR] [--kcsa PATH]

Reads video/narration.json. Each sentence is synthesised once with Kokoro
(cached by text + voice), then laid out on a timeline with fixed pauses. The
timeline drives both the captions and the scene animation in stage.html, so
re-running this after editing the script re-times everything.

To use a human voiceover instead, drop one WAV per sentence into
<work>/wav/override/<scene>-<n>.wav (24 kHz mono); those replace the synthetic
take and the timeline follows their real durations.
"""
import argparse
import hashlib
import json
import os
import re

import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 24000
TITLE_HOLD = 2.2      # silent title card before the first word
GAP_SENTENCE = 0.5
GAP_SCENE = 1.3
END_HOLD = 5.0        # end card after the last word (room to read team names)
CAP_LINGER = 0.45     # seconds a caption stays after its words end
MAX_CAP = 112         # characters per caption chunk before splitting


def vtt_time(x):
    ms = int(round(x * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d}.{ms % 1000:03d}"


def split_caption(text):
    """Split a long caption at the boundary nearest its middle."""
    if len(text) <= MAX_CAP:
        return [text]
    mid = len(text) / 2
    best = None
    for m in re.finditer(r"(?<=[.:?;,]) ", text):
        score = abs(m.start() - mid)
        if best is None or score < best[0]:
            best = (score, m.start())
    if best is None:
        return [text]
    a, b = text[:best[1]].strip(), text[best[1]:].strip()
    return split_caption(a) + split_caption(b)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", default=os.environ.get("VIDEO_WORK", "/tmp/video-work"))
    ap.add_argument("--kcsa", default=None, help="kcsa.json from the team code")
    ap.add_argument("--models", default=os.environ.get("KOKORO_DIR", "."))
    ap.add_argument("--vtt", default=os.path.join(HERE, "..", "assets", "video", "surrogate-chain.vtt"))
    args = ap.parse_args()

    spec = json.load(open(os.path.join(HERE, "narration.json")))
    wav_dir = os.path.join(args.work, "wav")
    os.makedirs(os.path.join(wav_dir, "override"), exist_ok=True)

    kokoro = None
    t = TITLE_HOLD
    timeline = {"fps": 30, "scenes": [], "sentences": []}
    pieces = [np.zeros(int(TITLE_HOLD * SR), np.float32)]
    words = 0
    for si, scene in enumerate(spec["scenes"]):
        if si > 0:
            t += GAP_SCENE - GAP_SENTENCE
            pieces.append(np.zeros(int(round((GAP_SCENE - GAP_SENTENCE) * SR)), np.float32))
        scene_start = t if si else 0.0
        for n, s in enumerate(scene["sentences"]):
            key = f"{scene['id']}-{n}"
            override = os.path.join(wav_dir, "override", key + ".wav")
            h = hashlib.sha1(f"{spec['voice']}|{spec['speed']}|{s['say']}".encode()).hexdigest()[:12]
            cached = os.path.join(wav_dir, f"{key}-{h}.wav")
            if os.path.exists(override):
                audio, sr = sf.read(override, dtype="float32")
                assert sr == SR, f"{override}: expected {SR} Hz"
            elif os.path.exists(cached):
                audio, _ = sf.read(cached, dtype="float32")
            else:
                if kokoro is None:
                    from kokoro_onnx import Kokoro
                    kokoro = Kokoro(os.path.join(args.models, "kokoro-v1.0.onnx"),
                                    os.path.join(args.models, "voices-v1.0.bin"))
                audio, sr = kokoro.create(s["say"], voice=spec["voice"],
                                          speed=spec["speed"], lang="en-us")
                audio = np.asarray(audio, np.float32)
                sf.write(cached, audio, sr)
            # trim leading/trailing near-silence so pauses are ours, not the model's
            nz = np.flatnonzero(np.abs(audio) > 0.01)
            if len(nz):
                audio = audio[max(nz[0] - int(0.03 * SR), 0): nz[-1] + int(0.08 * SR)]
            dur = len(audio) / SR
            chunks, c0 = [], t
            parts = split_caption(s["cap"])
            total = sum(len(p) for p in parts)
            for p in parts:
                d = dur * len(p) / total
                chunks.append({"start": round(c0, 3), "end": round(c0 + d, 3), "text": p})
                c0 += d
            timeline["sentences"].append({
                "id": key, "scene": scene["id"], "index": n,
                "start": round(t, 3), "end": round(t + dur, 3),
                "cap": s["cap"], "say": s["say"], "chunks": chunks})
            pieces.append(audio)
            pieces.append(np.zeros(int(GAP_SENTENCE * SR), np.float32))
            t += dur + GAP_SENTENCE
            words += len(s["say"].split())
        timeline["scenes"].append({"id": scene["id"], "label": scene["label"],
                                   "start": round(scene_start, 3), "end": round(t, 3)})
    t += END_HOLD - GAP_SENTENCE
    pieces.append(np.zeros(int((END_HOLD - GAP_SENTENCE) * SR), np.float32))
    timeline["scenes"][-1]["end"] = round(t, 3)
    timeline["duration"] = round(t, 3)

    # captions stay up briefly after the audio, never overlapping the next one
    chunks = [c for s in timeline["sentences"] for c in s["chunks"]]
    for c, nxt in zip(chunks, chunks[1:] + [None]):
        hold = c["end"] + CAP_LINGER
        c["show_end"] = round(min(hold, nxt["start"]) if nxt else hold, 3)
    vtt = ["WEBVTT", ""]
    for i, c in enumerate(chunks, 1):
        vtt += [str(i), f"{vtt_time(c['start'])} --> {vtt_time(c['show_end'])}", c["text"], ""]
    os.makedirs(os.path.dirname(args.vtt), exist_ok=True)
    with open(args.vtt, "w") as f:
        f.write("\n".join(vtt))

    audio = np.concatenate(pieces)
    peak = float(np.max(np.abs(audio)))
    if peak > 0:
        audio = audio * (0.89 / peak)
    sf.write(os.path.join(args.work, "narration.wav"), audio, SR)

    with open(os.path.join(HERE, "timeline.json"), "w") as f:
        json.dump(timeline, f, indent=1)
    kcsa = {}
    if args.kcsa:
        k = json.load(open(args.kcsa))
        kcsa = {key: k[key] for key in ("V_mV", "I", "reversal_mV", "nernst_mV",
                                         "nernst_scan", "landscape_z",
                                         "landscape_F_kJ", "sites", "conductance")}
        json.dump(kcsa, open(os.path.join(HERE, "kcsa.json"), "w"))
    elif os.path.exists(os.path.join(HERE, "kcsa.json")):
        kcsa = json.load(open(os.path.join(HERE, "kcsa.json")))
    with open(os.path.join(HERE, "data.js"), "w") as f:
        f.write("window.TIMELINE = " + json.dumps(timeline) + ";\n")
        f.write("window.KCSA = " + json.dumps(kcsa) + ";\n")

    print(f"duration {t:.1f} s ({int(t // 60)}:{t % 60:04.1f}), {words} spoken words, "
          f"{words / (t - TITLE_HOLD - END_HOLD) * 60:.0f} wpm incl. pauses, peak {peak:.2f}")
    for sc in timeline["scenes"]:
        print(f"  {sc['id']:<11} {sc['start']:7.1f} - {sc['end']:7.1f}  ({sc['end'] - sc['start']:.1f} s)")


if __name__ == "__main__":
    main()
