#!/usr/bin/env python3
"""Render one shot clip with Veo 3.1 via the Gemini API.

Requires: pip install google-genai ; export GEMINI_API_KEY=...

Examples
  # keyframe mode (default in the skill)
  python3 veo_generate.py --prompt-file animation/x/08-clips/S01.prompt.txt \
      --image animation/x/07-keyframes/S01-start.png --duration 6 --aspect 16:9 \
      --out animation/x/08-clips/S01_v1.mp4

  # reference mode (up to 3 card images)
  python3 veo_generate.py --prompt "..." --ref char.png --ref scene.png --duration 8 --out S02_v1.mp4

Env overrides: VEO_MODEL (default veo-3.1-generate-preview).
"""
import argparse
import mimetypes
import os
import sys
import time
from pathlib import Path

DEFAULT_MODEL = os.environ.get("VEO_MODEL", "veo-3.1-generate-preview")
DEFAULT_NEGATIVE = ("photorealistic, live action, 2D anime, sketch lines, storyboard, text, "
                    "subtitles, watermark, logo, plastic skin, extra fingers, distorted face")


def load_image(types, path):
    p = Path(path)
    mime = mimetypes.guess_type(p.name)[0] or "image/png"
    return types.Image(image_bytes=p.read_bytes(), mime_type=mime)


def main():
    ap = argparse.ArgumentParser()
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--prompt")
    src.add_argument("--prompt-file")
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--duration", type=int, default=8, choices=[4, 6, 8])
    ap.add_argument("--aspect", default="16:9", choices=["16:9", "9:16"])
    ap.add_argument("--resolution", default="720p", choices=["720p", "1080p"])
    ap.add_argument("--image", help="first-frame keyframe (keyframe mode)")
    ap.add_argument("--last-frame", help="optional last-frame image for continuity handoff")
    ap.add_argument("--ref", action="append", default=[], help="reference image (max 3)")
    ap.add_argument("--negative", default=DEFAULT_NEGATIVE)
    ap.add_argument("--seed", type=int)
    ap.add_argument("--poll", type=int, default=10)
    a = ap.parse_args()

    if not os.environ.get("GEMINI_API_KEY") and not os.environ.get("GOOGLE_API_KEY"):
        sys.exit("GEMINI_API_KEY is not set. Export it in your shell (do not paste it into chat).")
    if len(a.ref) > 3:
        sys.exit("Veo accepts at most 3 reference images.")
    if a.resolution == "1080p" and a.duration != 8:
        print("note: 1080p requires 8s clips; falling back to 720p", file=sys.stderr)
        a.resolution = "720p"

    try:
        from google import genai
        from google.genai import types
    except ImportError:
        sys.exit("Missing SDK: pip install google-genai")

    prompt = a.prompt if a.prompt else Path(a.prompt_file).read_text()
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.with_suffix(".prompt.txt").write_text(prompt)

    cfg = dict(aspect_ratio=a.aspect, resolution=a.resolution,
               duration_seconds=a.duration, negative_prompt=a.negative)
    if a.seed is not None:
        cfg["seed"] = a.seed
    if a.last_frame:
        cfg["last_frame"] = load_image(types, a.last_frame)
    if a.ref:
        cfg["reference_images"] = [
            types.VideoGenerationReferenceImage(image=load_image(types, r), reference_type="asset")
            for r in a.ref
        ]

    client = genai.Client()
    kwargs = dict(model=a.model, prompt=prompt, config=types.GenerateVideosConfig(**cfg))
    if a.image:
        kwargs["image"] = load_image(types, a.image)

    print(f"rendering {out.name} with {a.model} ({a.duration}s {a.aspect} {a.resolution})...")
    try:
        op = client.models.generate_videos(**kwargs)
        while not op.done:
            time.sleep(a.poll)
            op = client.operations.get(op)
    except Exception as e:  # surface API errors verbatim for the fallback ladder
        sys.exit(f"Veo API error: {e}")

    if getattr(op, "error", None):
        sys.exit(f"Veo operation error: {op.error}")
    vids = getattr(op.response, "generated_videos", None) if op.response else None
    if not vids:
        sys.exit(f"No video returned (possibly safety-filtered). Response: {op.response}")
    video = vids[0].video
    client.files.download(file=video)
    video.save(str(out))
    print(f"saved {out}")


if __name__ == "__main__":
    main()
