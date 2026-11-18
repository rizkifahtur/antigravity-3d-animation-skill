#!/usr/bin/env python3
"""Generate a character card, scene card, or keyframe with Nano Banana Pro (Gemini image model).

Use when Antigravity's built-in image tool is unavailable, or when you need to condition on
existing card images (--ref) to keep identity locked in keyframes.

Requires: pip install google-genai ; export GEMINI_API_KEY=...

Example
  python3 gen_image.py --prompt-file S03-keyframe.txt \
      --ref animation/x/03-characters/mia-card.png --ref animation/x/04-scenes/kitchen-card.png \
      --aspect 16:9 --size 2K --out animation/x/07-keyframes/S03-start.png

Env overrides: IMAGE_MODEL (default gemini-3-pro-image-preview).
"""
import argparse
import mimetypes
import os
import sys
from pathlib import Path

DEFAULT_MODEL = os.environ.get("IMAGE_MODEL", "gemini-3-pro-image-preview")


def main():
    ap = argparse.ArgumentParser()
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--prompt")
    src.add_argument("--prompt-file")
    ap.add_argument("--out", required=True)
    ap.add_argument("--ref", action="append", default=[], help="reference image(s)")
    ap.add_argument("--aspect", default="16:9")
    ap.add_argument("--size", default="2K", choices=["1K", "2K", "4K"])
    ap.add_argument("--model", default=DEFAULT_MODEL)
    a = ap.parse_args()

    if not os.environ.get("GEMINI_API_KEY") and not os.environ.get("GOOGLE_API_KEY"):
        sys.exit("GEMINI_API_KEY is not set. Export it in your shell (do not paste it into chat).")
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        sys.exit("Missing SDK: pip install google-genai")

    prompt = a.prompt if a.prompt else Path(a.prompt_file).read_text()
    parts = []
    for r in a.ref:
        p = Path(r)
        parts.append(types.Part.from_bytes(data=p.read_bytes(),
                                           mime_type=mimetypes.guess_type(p.name)[0] or "image/png"))
    parts.append(prompt)

    client = genai.Client()
    try:
        resp = client.models.generate_content(
            model=a.model,
            contents=parts,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=types.ImageConfig(aspect_ratio=a.aspect, image_size=a.size),
            ),
        )
    except Exception as e:
        sys.exit(f"Image API error: {e}")

    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    for cand in resp.candidates or []:
        for part in (cand.content.parts if cand.content else []):
            if getattr(part, "inline_data", None) and part.inline_data.data:
                out.write_bytes(part.inline_data.data)
                out.with_suffix(".prompt.txt").write_text(prompt)
                print(f"saved {out}")
                return
    sys.exit(f"No image returned (possibly safety-filtered). Response: {resp}")


if __name__ == "__main__":
    main()
