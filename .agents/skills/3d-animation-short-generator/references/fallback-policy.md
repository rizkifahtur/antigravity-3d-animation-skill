# Generation Failure and Drift Fallback Policy (Antigravity Edition)

## Video clip ladder (Veo 3.1 / Veo 3.1 Fast)

When a clip fails (API error, safety block) or drifts (wrong identity, landmark on the wrong side, wrong exit edge, flipped lighting):

1. **Retry 1 — strengthen prompt:** re-render with the exact `Reference Anchors` block from `05-shot-table.md` quoted in the prompt; move the identity lock earlier in the prompt.
2. **Retry 2 — fix the keyframe:** regenerate `07-keyframes/SXX-start.png` (pass all relevant cards with `--ref`), and if the end pose matters, add `SXX-end.png` as `--last-frame`. In reference mode, switch this shot to keyframe mode.
3. **Retry 3 — simplify the shot:** shorten to 4 s and move the dropped beat into a new adjacent row in Step 5; re-run the Step 5.5 self-check, then re-render. If using Fast, also try full Veo 3.1.
4. **After three failed attempts on the same shot**, choice prompt:
   1. Loosen the request (drop a prop, simplify action, reduce the hook)
   2. Split into two shorter shots (back to Step 5)
   3. Skip and insert `placeholder: missing clip` for later review
   4. User supplies their own reference clip/image to bind instead
   0. Other

Safety blocks: Veo may refuse children-in-peril, violence, or real-person likeness. Rephrase toward cartoon slapstick, remove realistic injury, never use real people's names/faces.

Never silently mix corrected and uncorrected clips into assembly.

## API / environment errors

- `GEMINI_API_KEY` missing or 401/403: stop, tell the user to export a valid key with billing enabled. Do not ask them to paste the key into chat.
- 429 / quota: wait and retry later; offer switching to Veo 3.1 Fast.
- "model not found": list available models (see `model-selection.md` header) and update `VEO_MODEL` / `IMAGE_MODEL`.
- Unsupported parameter combo (e.g. 1080p with 4 s, reference images with 9:16): the script prints the API error — adjust duration/resolution/mode and retry; do not loop more than twice on the same error.

## Storyboard visualization fallback (pencil mode only)

If a pencil storyboard image fails (layout collapse, illegible labels, merged panels, inconsistent character):

1. Retry with a tightened prompt naming the four-quadrant layout, the `[char:…] [scene:…] [shot:…]` labels, and per-panel rules.
2. Drop the bottom-right audio/anchor quadrant text (leave a blank cell with a small `♪`).
3. Reduce panel count by one and simplify camera icons to single arrows.
4. After three failures, choice prompt: block-color storyboard for this shot · drop the pencil image and rely on text · split the shot (Step 5) · user supplies a reference image.

In default text mode this fallback is unnecessary; if the text storyboard itself is incoherent, return to Step 5 and revise the row.
