# Video

`assets/video/surrogate-chain.mp4` (3:43, 1920×1080, 30 fps, H.264 + AAC), with burned-in captions,
a matching WebVTT file (`assets/video/surrogate-chain.vtt`) and a poster frame (`poster.jpg`).

Every frame is drawn by `stage.html` as a pure function of time, `renderAt(t)`, from a timeline
built out of the narration audio. Change the words and everything re-times itself.

| File | Role |
| --- | --- |
| `narration.json` | The script, one entry per sentence: `cap` is the caption text, `say` is how the TTS should pronounce it ("AMPL" → "ample", "KcsA" → "K C S A"). `phoneme_fixes` patches the two words the G2P gets wrong (the A in "VDSAI", the stress in "gramicidin"). |
| `script.md` | The same script for reading, with scene notes. Keep it in step with `narration.json`. |
| `tts.py` | Synthesises each sentence (Kokoro, voice `af_heart`, speed 1.0), lays it out with fixed pauses, and writes `timeline.json`, `data.js`, `<work>/narration.wav` and the `.vtt`. |
| `stage.html` | 1920×1080 animated stage. Reads `data.js` (timeline + KcsA data). Open it in a browser with `?t=120` to see any moment. |
| `kcsa.json` | KcsA I–V, Nernst scan and filter landscape, computed from the team code by `tools/kcsa_data.py`. |
| `render.py` | Screenshots every frame with Playwright/Chromium and encodes the MP4 with ffmpeg (audio normalised to about −16 LUFS). |

## Rebuild

```sh
pip install kokoro-onnx soundfile numpy playwright      # plus ffmpeg on PATH
# Kokoro model files: kokoro-v1.0.onnx and voices-v1.0.bin (github.com/thewh1teagle/kokoro-onnx releases)
export VIDEO_WORK=/tmp/video-work                       # scratch: wavs and ~1.3 GB of JPEG frames
python video/tts.py --models /path/to/kokoro            # add --kcsa path/to/kcsa.json to refresh the plot data
CHROMIUM=/path/to/chrome python video/render.py         # CHROMIUM is optional if `playwright install chromium` has been run
```

`tts.py` prints the total length and per-scene timing. Keep it under 4:00. Sentences are cached by
text, so re-running after a small edit only re-synthesises what changed.

Partial re-renders, because frames are pure functions of time:

```sh
python video/render.py --from 214           # only the end card (e.g. after editing data/team.json), then re-encode
python video/render.py --from 100 --to 156  # one scene
python video/render.py --stills 2,60,150 --no-encode   # QA stills into $VIDEO_WORK/stills
python video/render.py --encode-only        # re-mux after replacing narration.wav
```

If the narration is re-timed, every frame moves, so run the full render.

The end card reads `data/team.json` at render time: `{"team": [{"name", "affiliation"?, "rung"?}], "affiliations"?: [...]}`.
Names alone go in a centred grid. With per-person affiliation strings, each shows under the name. With
numeric affiliations, superscripts point into `affiliations`. A `rung` of 1 or 2 adds a colour key.

## Swapping in a human voiceover

1. Record one take per sentence, following the `cap` text in `narration.json` (or one take per scene,
   then cut it at sentence boundaries). Natural pace; trim long silences but leave the words alone.
2. Save each as 24 kHz mono WAV named `<scene>-<n>.wav` in `$VIDEO_WORK/wav/override/`, where `n` is the
   sentence's zero-based index within its scene, e.g. `screening-5.wav`. Convert with
   `ffmpeg -i take.m4a -ac 1 -ar 24000 screening-5.wav`.
3. Run `python video/tts.py`. Overrides replace the synthetic takes, and the timeline, captions and
   VTT follow the real durations. Sentences without an override keep the Kokoro voice, so you can do
   this a few sentences at a time.
4. Run `python video/render.py` (full render, since the timing changes).

If the reader changes the wording, edit `cap` (and `say`) in `narration.json` and `script.md` to match,
so the captions stay word for word.
