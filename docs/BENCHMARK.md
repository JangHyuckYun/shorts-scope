# Evidence checks — 2026-09-10

These are small development checks, **not** a public-dataset accuracy benchmark. Distinguish measured transforms, model descriptions and unsupported gait labels. Third-party reference media and raw provider logs are not redistributed.

## Synthetic image-plane motion (reproducible)

```sh
.venv/bin/python -m pip install -r requirements-evidence.txt
.venv/bin/python examples/evaluate_motion.py
```

The generator uses deterministic textured images and known translations/rotation, a static background with moving foreground, an untextured pair and unrelated frames. On OpenCV 5.0.0 / NumPy 2.5.3:

- 7 cases passed the fixed numerical/status criteria.
- Translation (7,−3) pixels: Euclidean error **0.0051px**; (−9,4): **0.0144px**; unchanged image: **0px**. Acceptance threshold <0.5px.
- 2° rotation: measured magnitude **1.995°**, within the 0.2° criterion.
- Static background ROI with changing foreground: `stable`.
- No texture and unrelated frames: `unknown`, not a false stationary conclusion.

These simple planar synthetic transforms do not prove subpixel accuracy on real footage, calibrated camera motion, object identity or action recognition.

## Real camera-description before/after

Same reference interval, same **four individual images** at requested sample positions 9.00, 9.38, 9.75 and 10.12 seconds, same base schema/prompt and `gpt-5.6-luna` requested effort `low`. The after request additionally received local evidence from 16 densely sampled frames over 9–10.5s, including a caller-selected upper background ROI and pose availability. No comments, audio or caption explanation supplied.

- **Before:** described similar background structures and said there was no large camera motion. Multiple per-frame poses were described as walking-like, including a high-confidence object record with a walking description.
- **After:** described consistent **screen-left background displacement**, said camera movement was possible and that the evidence was inconsistent with a fixed-camera interpretation. It explicitly left walking/running unresolved because feet were not sufficiently visible.
- Local motion: sparse four-image sampling failed consensus in all three pairs. Dense sampling established `moved` in **15/15 adjacent pairs**, all screen-left, with inlier ratios about **0.75–0.988**. Thresholds were unchanged.
- Measurement including pose availability: **1.90s**; dense extraction: **4.21s**, both local single runs.
- Model runtime: **73.79s → 69.82s**. Provider-reported input tokens **18,678 → 22,024** (+17.9%); output **3,593 → 3,358**. Context/harness tokens are included; this is not pure image-token accounting or a portable latency claim.

This establishes an evidence-supported correction in **one** camera-description trial, plus less unsupported gait labeling. It does not establish a dataset-level accuracy gain or successful running recognition. Exact pan versus translation, camera extrinsics, physical speed and subject-world trajectory remain unresolved. Both response wording and measurements need source inspection; adding an instruction to avoid gait guesses is not itself an action classifier. The crop/OCR evidence path was not used in this real-video A/B.

## Known-source text fixture

Use `examples/make_style_fixture.py` with your own appropriately licensed bold font, then extract three uniform samples at width 360 with `--no-endpoint`. Our fixture used DejaVuSans-Bold, 32px, white text, black 1px foreground stroke and a lower-right black shadow with 3px offset/stroke. Source renderer settings are ground truth, not fields the AI is promised to recover.

- Tesseract 5.3.4, English, lower-image ROI: **HELLO SHORTS in 3/3** samples. Engine confidence about 96.1–96.5 (not calibrated correctness probability).
- Boxes in all three: approximately `[0.11944, 0.77656, 0.86111, 0.81250]`, relative to the individual image. Crops and quantized colors were saved separately for inspection.
- Supplied candidate set: DejaVuSans-Bold / DejaVuSans / DejaVuSerif. The actual bold font ranked **first among three in all three samples**; shape-overlap scores 0.8455 / 0.6413 / 0.3354. This is a closed candidate check, not open-world exact font identification.
- Limiting Tesseract to one OpenMP thread preserved those OCR/box/ranking results and changed this three-frame measurement run **8.94s → 0.67s**. This is a single before/after timing on this machine, not a general speed guarantee.

The previous AI-only fixture run already recognized the words and broad white/bold/outline/shadow appearance. The new result adds measured geometry, crop evidence and bounded font candidate comparison; it does **not** prove better AI shadow or weight descriptions than that earlier run. Exact font identity, stroke width and shadow decomposition remain unsupported.

## Verification and next quality gate

109 offline tests passed, including synthetic motion ground truth, stale evidence rejection, image/crop path boundaries, chronological subset selection, existing model/schema failure handling, host install destinations, idempotency and overwrite refusal. These test counts measure software behavior, not model intelligence. Installer layout/launcher tests are isolated; live discovery across all four named products is not claimed.

Next accuracy work should use a labeled, redistributable set spanning full-body walking/running, camera pan versus subject motion, cuts/parallax, varied subtitles and overlapping text effects. Compare identical models/images/efforts, measure false camera-static assertions, action accuracy **and abstention coverage**, OCR character/box error and style-label error. Keep source renderer settings held out. Do not tune a gait claim on the single cropped reference until it says the expected word.
