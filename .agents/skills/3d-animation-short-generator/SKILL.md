---
name: 3d-animation-short-generator
description: |
  Create complete stylized 3D animated shorts (Pixar-style) from a story idea through an ordered production workflow: project brief, story outline, character and environment cards (Nano Banana Pro), standardized six-column shot table, text storyboards, Veo 3.1 single-shot clips, ffmpeg assembly, BGM, and final review. Use when the user wants an end-to-end narrative animation with strong character consistency, scene continuity, timing, camera, performance, and audio control. Not for single images, simple edits, photorealistic live action, or one standalone clip.
---

# 3D Animation Short Generator — Antigravity Edition

Port of MiniMax Hub's `3d-animation-short-generator` (v0.5.4) for **Google Antigravity**. The story/shot/storyboard methodology is unchanged; the platform layer is replaced:

| MiniMax Hub original | Antigravity edition |
|---|---|
| Canvas nodes | Files in `animation/<slug>/` inside the workspace |
| Choice cards | Numbered option list in chat → **STOP and wait** for the user's reply |
| `hub_generate_image` | Antigravity built-in image generation (Nano Banana Pro). Fallback: `scripts/gen_image.py` |
| `hub_generate_video` with H3 / Seedance 2.0 | `scripts/veo_generate.py` → **Veo 3.1** (final) / **Veo 3.1 Fast** (draft) via Gemini API |
| Hub assembly + BGM | `scripts/assemble.sh` (ffmpeg, BGM ducking, aspect-ratio crop) |

Talk to the user in the language they write in (e.g. Bahasa Indonesia). Keep file names and prompts to video/image models in English.

Core rule: **story first → choice prompt for aspect ratio + total duration right after intake → ordered project files → every required confirmation via a choice prompt → after character/scene cards, fixed order: six-column shot table with per-second directives + audio cues + spatial anchor chain → Step 5.5 self-check → one text storyboards document (one section per shot) → video-model + resolution choice → keyframe + Veo clip per shot → assembly with BGM. The final video must contain no storyboard artifacts.**

## Antigravity Setup (check once per project)

1. **Agent model** (Antigravity model dropdown): use the strongest reasoning model available — Gemini Pro tier (High thinking) or Claude Opus/Sonnet — for Steps 1–6 (story, shot table, storyboards). A Flash-tier model is fine for Step 7–8 file/script work. See `references/model-selection.md`.
2. **Mode**: use *Planning* mode (not Fast) so the agent writes plans/artifacts and pauses for review.
3. **Video/API prerequisites** (needed from Step 7): ask the user to confirm, or check in the terminal:
   - `GEMINI_API_KEY` exported in the shell (from Google AI Studio, billing enabled — Veo is paid).
   - `pip install google-genai` and `ffmpeg` on PATH.
   - Never print, log, or write the API key into project files.
4. If prerequisites are missing, Steps 0–6 can still run; stop before Step 7 and tell the user what to install.

## Choice Prompt Format (replaces choice cards)

Whenever this skill says "choice prompt", output exactly this shape and then **end your turn**:

```
**[Gate name]** — pilih satu (balas angka):
1. Option A (recommended)
2. Option B
3. Option C
0. Other / custom — tulis sendiri
```

Never auto-select, never continue past a gate in the same turn, never replace a gate with prose. The user may answer with a number or free text.

## Project Folder Layout (replaces canvas)

Create `animation/<slug>/` in the workspace (slug = kebab-case working title). Write every durable artifact to disk in this order — do not dump long production content only in chat:

```
animation/<slug>/
  00-project.json            # approved settings: aspect, duration, resolution, video_model, style, language
  01-brief.md                # Project Brief
  02-story-outline.md        # Story Outline
  03-characters/             # <name>-card.png + <name>-card.md (visual-ID note + prompt used)
  04-scenes/                 # <scene>-card.png + <scene>-card.md (landmarks, light states, prompt)
  05-shot-table.md           # six-column table; first line "shot-table self-check: passed" once passed
  06-storyboards/
     text-storyboards.md     # one "## S01" section per shot (authoritative)
     S05-extracted.md        # only for shots flagged for heavy iteration
     pencil/S01.png          # only in visualization mode
  07-keyframes/S01-start.png # first frames generated from cards (keyframe mode)
  08-clips/S01_v1.mp4        # versioned; highest version = current
  09-assembly/main.mp4, bgm.*, final.mp4
  10-review.md
```

When regenerating, bump the version suffix (`_v2`) — never overwrite — and state which version is current. `00-project.json` is the single source of truth for settings; update it after each gate.

## Global Visual Style Lock

Unless the user explicitly requests another visual style, all character cards, scene cards, shot tables, storyboards, keyframes, clips, and final composites use this style:

- Rendering: Pixar-inspired 3D cartoon rendering, C4D + Octane renderer look, high-end animated feature quality.
- Character design: exaggerated geometric simplification balanced with excellent material detail; large readable silhouettes; Q-version proportions when appropriate (2.5–3 heads tall for cute/childlike characters).
- Hair/fur: sculpted clumps and clean block shapes plus fine flyaway edge hairs / fuzzy rim detail.
- Skin/material: warm subsurface scattering, soft translucent red through ears, cheeks, nose, fingertips; no hard plastic skin.
- Acting: exaggerated, lively Disney/Pixar performance — squash and stretch, strong brows, eye corners, pupils, lips, cheeks.
- Motion: high-energy poses, clear line of action, anticipation, fast-but-readable timing, elastic body mechanics, vivid micro-expressions.

Negative style: no photorealistic live action, no flat 2D anime, no plastic toy skin, no stiff mannequin posing, no lifeless faces.

## STEP 0: Intake and Project Plan

Capture: one-line idea; desired output depth (blueprint only / assets only / shot table / storyboards / clips / assembled / final with BGM); approximate length; aspect ratio; tone (default warm stylized 3D); dialogue mode (dialogue / voiceover / no speech); dialogue language **only if the user states it** — do not default to English.

Immediately after intake, before anything else, show two choice prompts in one message (user answers both):

Aspect ratio:
1. 16:9 landscape (recommended — native Veo)
2. 9:16 vertical short (native Veo)
3. 1:1 square (rendered 16:9, center-cropped in assembly)
4. 4:5 social portrait (rendered 9:16, cropped in assembly)
0. Custom

Total duration:
1. 30–60 s (recommended)
2. 15–30 s
3. 60–90 s
4. 90–180 s (many clips → higher Veo cost; warn the user)
0. Custom

Proceed only after both are answered. Save to `00-project.json` and reuse everywhere.

## STEP 1: Project Brief → `01-brief.md`

Include: working title, one-line What-if, emotional premise, target audience feeling, deliverables, approved aspect ratio, approved duration, estimated shot count (duration ÷ ~6 s), dialogue mode and language (`language not specified` if not given), initial risks, dialogue intent.

Choice prompt: 1. Continue with this direction (recommended) · 2. Regenerate premise options · 3. Revise emotional premise · 4. Refine dialogue direction.

## STEP 2: Story Outline and Gates → `02-story-outline.md`

Include: protagonist Want / Need / flaw; core world rule; 8-beat causal story spine; emotional anchor and payoff; dialogue beats if requested; red-line checks.

Gate checks (write pass/fail per item in the file): protagonist is active · crisis intensified by protagonist's flaw · coincidence never solves the problem · ending reuses an earlier emotional anchor · antagonistic pressure is not a flat villain · dialogue reveals relationship change instead of explaining theme.

Choice prompt: 1. Approve story and continue (recommended) · 2. Revise beats · 3. Revise emotion curve · 4. Revise dialogue beats · 5. Return to premise.

## STEP 3: Character Cards → `03-characters/`

Generate with Antigravity's image generation (Nano Banana Pro). Order: protagonist → contrast/pressure character → optional supporting. Each card is a 16:9 production reference sheet with readable labels:

- Name label + role label; main 3/4 view; front / side / back views; expression row; costume/material/prop details with prop labels.
- Write `<name>-card.md` next to the PNG: age range, body type, hairstyle, outfit colors, signature props, do-not-change traits, and the exact prompt used (identity lock, reused verbatim later).

If built-in image generation is unavailable or saves elsewhere, run `python3 scripts/gen_image.py` (see script header) or copy the output into this folder.

Choice prompt: 1. Lock character designs and continue (recommended) · 2. Regenerate protagonist card · 3. Adjust specific visual details · 4. Add another character card. Warn: changing locked designs later forces regeneration of the shot table onward.

## STEP 4: Scene Cards → `04-scenes/`

Environment only — no characters, people, silhouettes, hands, or faces. Include: main environment overview, key light states (day/night), emotional sub-spaces, continuity landmarks (fixed objects whose screen position must persist, e.g. door frame, sofa, tree), important props. Document landmarks and lighting in `<scene>-card.md`.

Choice prompt: 1. Lock scene design and continue (recommended) · 2. Regenerate scene card · 3. Add another scene angle · 4. Adjust lighting or layout.

## STEP 5: Standardized Shot Table (Six Columns) → `05-shot-table.md`

Mandatory; cannot be swapped with storyboard or video steps. **Read and follow `references/shot-table-spec.md`** for the exact schema, per-second directives, table rules, approval prompt, and the Step 5.5 self-check.

Antigravity/Veo constraints that override the original spec:
- Every shot duration is **4, 6, or 8 seconds** (Veo 3.1 clip lengths). Longer beats are split into multiple rows.
- In `Shot Description`, add `render_mode: keyframe | reference` (default keyframe) and optional `video_model: veo-3.1 | veo-3.1-fast`.
- Dialogue lines must fit inside one clip; Veo generates audio per clip, so do not let a sentence span two shots.

Run the Step 5.5 self-check. Do not enter Step 6 until it passes.

## STEP 6: Text Storyboards (default) + Pencil Storyboards (opt-in) → `06-storyboards/`

**Read and follow `references/storyboard-guidelines.md`.** Show the storyboard-mode choice prompt first. Default = one authoritative `text-storyboards.md` with one section per shot. Pencil images are opt-in, human-review only, and never override the text. Extract a shot to `S0X-extracted.md` only when the user flags it for heavy iteration.

## STEP 7: Video Model + Resolution Choice → Keyframes → Veo Clips

**Read `references/model-selection.md`** (models, modes, prompt shaping, cost) and **`references/fallback-policy.md`** (retry ladders, drift).

Minimum contract:
- Show the video-model choice prompt, then the resolution choice prompt. Store in `00-project.json`.
- Before rendering everything, render **S01 only** as a test, show it, and ask approval (cost control).
- Default render mode is **keyframe**: generate `07-keyframes/SXX-start.png` with Nano Banana Pro from the exact character card(s) + scene card + the shot's first-second directive, then call `scripts/veo_generate.py --image` with it.
- Build every clip prompt from the matching storyboard section (or extracted file), the identity lock text from the character `.md`, and the landmarks/lighting from the scene `.md`. Strip all storyboard labels (`[char:…]`, `[scene:…]`, `[shot:…]`, `[dur:…]`, `[hook:…]`), shot numbers, arrows, and notes.
- Clips must be clean full-color 3D animation: no sketch texture, no labels, no subtitles unless requested, no watermarks.
- On drift from `Reference Anchors`, follow `references/fallback-policy.md`; never silently assemble wrong clips.

After all clips render, list them in shot order with version numbers and show the clip-approval choice prompt from `references/model-selection.md`.

## STEP 8: Assembly, BGM, Final Output → `09-assembly/`

**Read `references/qc-checklist.md`** for assembly rules, BGM rules, final review checks, gate discipline, and latest-asset discipline.

- Assemble with `scripts/assemble.sh` (exact shot order from the approved table; latest approved version of each clip; crops to 1:1 / 4:5 if chosen).
- BGM: Veo produces per-clip audio only, so one continuous BGM track is either (a) a file the user provides, or (b) a track the user makes in a music tool (e.g. Lyria / Google Flow / any royalty-free library) — ask with a choice prompt. The script ducks BGM under clip audio (dialogue/SFX).
- No subtitles or text unless requested. Final video must contain no storyboard traces.
- Run the final review checks, write `10-review.md`, and deliver the path of `final.mp4`.

## Boundaries

Do not use this skill for a single image, a simple edit, a single clip, logo design, or pure prompt consultation.
