# Model Selection and Prompt Shaping (Antigravity Edition)

> Model IDs below were current when this port was written (Nov 2026). Google renames preview models often. If a call fails with "model not found", list models with `python3 -c "from google import genai; [print(m.name) for m in genai.Client().models.list()]"` and update `00-project.json` / env vars instead of editing the scripts.

## 1. Agent model inside Antigravity (the "brain")

Pick in Antigravity's model dropdown; it is not set by this skill.

| Steps | Recommended | Why |
|---|---|---|
| 0–2 Brief, story | Gemini Pro tier (High thinking) or Claude Opus | Causal story logic, gate checks |
| 3–4 Cards (prompt writing) | Gemini Pro tier | Uses built-in Nano Banana Pro image tool natively |
| 5–6 Shot table, storyboards | Gemini Pro tier (High) or Claude Opus/Sonnet | Long structured output, per-second precision, self-check |
| 7–8 Scripts, ffmpeg, file ops | Gemini Flash tier or Claude Sonnet | Cheap/fast, mechanical work |

If quota runs out on one model, switching mid-project is safe because all state lives in `animation/<slug>/`.

## 2. Image model (cards, keyframes, optional pencil boards)

- **Primary:** Antigravity built-in image generation (Nano Banana Pro = Gemini 3 Pro Image). Ask the agent to "generate an image" and save into the right folder.
- **Script fallback / for reference-image conditioning:** `scripts/gen_image.py`, env `IMAGE_MODEL` (default `gemini-3-pro-image-preview`). Pass the character/scene card PNGs with `--ref` to lock identity — this is how keyframes stay on-model.

## 3. Video model choice prompt (mandatory before any clip render)

```
**Video model** — pilih satu:
1. Veo 3.1 (recommended for final) — best quality, native audio (dialogue/SFX/ambience), 4/6/8 s clips, 720p or 1080p
2. Veo 3.1 Fast — cheaper/faster, good for drafts and animatic passes; re-render hero shots with Veo 3.1 later
3. Draft-then-final — every shot first in Fast at 720p, then approved shots re-rendered in Veo 3.1
0. Other
```

Env/flag: `--model veo-3.1-generate-preview` or `veo-3.1-fast-generate-preview` (override with `VEO_MODEL`).

Per-shot override: a row whose `Shot Description` contains `video_model: veo-3.1-fast` uses that model; unmarked rows use the project default.

## 4. Resolution choice prompt (after video model)

```
**Resolution** — pilih satu:
1. 720p (recommended for first pass; all durations)
2. 1080p (final quality; Veo only supports it for 8 s clips — 4/6 s shots fall back to 720p)
0. Other
```

## 5. Render modes

- **keyframe (default, best consistency):** Nano Banana Pro makes `07-keyframes/SXX-start.png` from character card(s) + scene card + the 0–1 s directive, in the project aspect ratio. Veo animates from it (`--image`). Optionally also make `SXX-end.png` and pass `--last-frame` when the next shot must start from an exact pose (continuity handoff).
- **reference:** no keyframe; pass up to 3 card images with `--ref` (Veo "asset" references). Faster to set up, weaker scene-layout control. Veo may restrict reference mode to 8 s / 16:9 — the script reports the API error if so.

## 6. Clip rendering rules

For each approved row:
- Authoritative sources: storyboard section (or extracted file) for narrative, composition, camera, staging, timing; character card `.md` for identity; scene card `.md` for environment, landmarks, lighting.
- Strip storyboard labels and any panel/arrow/timing notes.
- Output: clean full-color Pixar-style 3D animation in the approved aspect ratio and resolution, no text, no watermark, no sketch texture.
- Write the exact prompt used to `08-clips/SXX_vN.prompt.txt` (the script does this) so re-renders are reproducible.

## 7. Veo prompt shaping

Build the prompt in this order (Veo follows earlier text more strongly):

1. Style line: `Pixar-inspired 3D cartoon animation, C4D + Octane look, stylized Q-version proportions, warm subsurface-scattering skin, sculpted hair with fine flyaways, elastic squash-and-stretch performance, Disney-style anticipation and overshoot.`
2. Shot framing + lens + camera move (`medium close-up, 35mm, slow push-in`).
3. Identity lock (verbatim from character `.md`) and environment + landmark positions + lighting baseline.
4. Timed action: compress per-second directives into `0–2s: …; 2–4s: …; 4–6s: …`.
5. Audio: `Dialogue (Mia, excited whisper): "…"` / `SFX: …` / `Ambience: …` / `No music.` (keep BGM out of clips — it is added in assembly). For an off-screen narrator write `no lip movement`.
6. Negative prompt via `--negative`: `photorealistic, live action, 2D anime, sketch lines, storyboard, text, subtitles, watermark, logo, plastic skin, extra fingers, distorted face`.

## 8. Cost control

- Always render S01 first and get approval before batch rendering.
- Tell the user the clip count and that Veo is billed per second of output; suggest Draft-then-final for >10 shots.

## 9. Clip approval choice prompt

```
**Clip review** — pilih satu:
1. Approve clips and assemble full film (recommended)
2. Re-render selected clip(s) (same or other model)
3. Fix character mismatch
4. Fix scene mismatch
5. Fix spatial anchor drift across clips
6. Upgrade draft clips to Veo 3.1 / 1080p
0. Other
```
