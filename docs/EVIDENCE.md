# Local evidence: motion, text crops and pose availability

ShortsScope separates the **AI's visual interpretation** from independently calculated evidence. `measure` is optional and never calls a remote model/API. OpenCV/Tesseract/MediaPipe operate locally; the optional pose feature does run a local model. `model_called: false` means no remote LLM call, not absence of all machine learning.

## Setup

```sh
.venv/bin/python -m pip install -r requirements-evidence.txt
```

This adds NumPy and OpenCV alongside Pillow. The base `extract` and `analyze` prepare/import paths do not need these extras. Use one OpenCV wheel family in a clean venv; installing headless/contrib/non-contrib packages together can create conflicting `cv2` installations.

For OCR, separately install Tesseract and the language data you need; verify `tesseract --list-langs`. No executable or traineddata is bundled. For pose, optionally install `requirements-pose.txt` and supply a local compatible [MediaPipe Pose Landmarker](https://ai.google.dev/edge/mediapipe/solutions/vision/pose_landmarker/python) `.task` asset. Model files, fonts and their terms are the caller's responsibility; the tool never downloads them automatically.

## Focused motion measurement

```sh
# Dense local interval, not dense full-video model input
.venv/bin/python cli.py extract reference.mp4 --out output/motion \
  --start 9 --end 10.5 --sampler uniform --max-frames 16 \
  --width 320 --no-endpoint
.venv/bin/python cli.py measure output/motion/manifest.json --out output/motion-evidence \
  --motion-roi 0,0,1,0.35
.venv/bin/python cli.py analyze output/motion/manifest.json --out output/motion-request \
  --evidence output/motion-evidence/evidence.json --select-frames 1,5,9,13
```

Select a visibly textured **background** ROI when investigating camera motion. The example upper strip fits one reference, not every video. For object motion you can choose its ROI, but the result remains image-plane movement of that region, not automatically camera movement. Thin/tiny ROIs may lack enough feature support. Camera shake, moving backgrounds, parallax, occlusion and cuts can invalidate a simple affine model.

Forward/backward Lucas–Kanade feature tracks and RANSAC estimate a 2D partial affine transform. Results require at least 12 inliers, 60% agreement and support in at least three spatial cells. Weak/no-texture results are `unknown`, **not stable**. Dense samples can establish correspondences where widely spaced frames fail. The tool does not manufacture intermediate images or silently lower thresholds until a result appears.

A `moved` result indicates screen-plane translation/rotation/scale above heuristic thresholds, not measured camera extrinsics, physical speed or a guarantee of perceptually significant motion. `stable` is only evidence of a sufficiently supported small change in the supplied ROI.

## OCR and text detail

```sh
.venv/bin/python cli.py measure output/detail/manifest.json --out output/text-evidence \
  --ocr --ocr-lang eng --text-roi 0,0.65,1,1 \
  --font /path/to/candidate-bold.ttf --font /path/to/candidate-regular.ttf
.venv/bin/python cli.py analyze output/detail/manifest.json --out output/text-request \
  --evidence output/text-evidence/evidence.json --max-crops 4
```

OCR returns line text, Tesseract confidence, normalized boxes and padded detail crops. Crop boxes are relative to individual input images; they are back-projected from the OCR ROI/upscale, not contact-sheet coordinates. These are OCR estimates, not certified pixel-perfect text bounds. Tesseract uses one OpenMP thread by default to avoid oversubscription; an existing `OMP_THREAD_LIMIT` is respected.

The AI should receive `request.json` **images first, then detail_images**, together with prompt/schema. Filenames alone are not visual input. At most `--max-crops` additional images are attached; repeated text is deduplicated, so later styling changes of identical words may require selecting that interval separately. Supply the same selection/evidence options when importing the response to preserve provenance and expected IDs.

`palette_hex` describes quantized crop colors, not which pixels are foreground, outline or shadow. Candidate fonts are ranked by normalized glyph-shape overlap among **only your supplied files**, top three retained. Scores are similarity scores, not probabilities. Low resolution, different glyph rendering, layout, unknown fonts, gradients and overlapping outlines/shadows can defeat matching. `exact_font_name` remains null in AI output even if a supplied candidate ranks first.

For text appearance/weight/outline/shadow, inspect the crop and the full frame together. This release does not recover an editing application's exact font-size/weight/stroke/shadow settings. High-resolution crops supply better evidence; the final style description is still an AI estimate.

## Optional pose availability

```sh
.venv/bin/python -m pip install -r requirements-pose.txt
.venv/bin/python cli.py measure output/motion/manifest.json --out output/pose-evidence \
  --motion-roi 0,0,1,0.35 --pose-model /path/to/pose_landmarker.task
```

MediaPipe checks one detected person per image and records lower-body landmarks plus visibility. It is not multi-person identity tracking. `feet_sufficiently_visible` is an evidence-availability heuristic, **not** ground-truth visibility; `gait_class` remains `unknown`. Seeing/not seeing feet does not establish running/walking. Full lower-body consecutive footage and a separately evaluated temporal classifier would be needed for reliable gait labels; inventing those labels is not an improvement.

## Arguments and contract

- `manifest`, `--out`: extraction manifest and fresh/empty evidence output directory.
- `--motion-roi L,T,R,B`: normalized ROI, default whole frame.
- `--ocr`: opt in to Tesseract.
- `--tesseract PATH`, `--ocr-lang eng`, `--ocr-psm 11`: binary, installed language(s), PSM 3–13.
- `--text-roi L,T,R,B`: normalized OCR ROI, default whole frame.
- `--min-confidence 60`: retain OCR words at/above this engine score, 0–100.
- `--font FILE`: repeat up to 16 local font candidates; useful only with OCR.
- `--pose-model FILE`: opt in to a local model asset.

`evidence.json` (`shorts-evidence/1`) records image-content/timeline fingerprint, all frame IDs, motion pairs, OCR/pose evidence, method and runtime. Analysis rejects a fingerprint mismatch, including when pixels changed but the manifest text did not. A fingerprint prevents accidental mixing; it is not a signature or proof that measurements are truthful. Do not import untrusted executable/model/font assets casually. No failure is silently converted to a successful zero-motion/empty-OCR report.

`analyze --select-frames ID,ID,...` selects a subset of manifest IDs but retains all dense measurement context; output IDs remain chronological and must match the selected subset. `--max-crops 0..8` controls extra crop image inputs, default 4. More evidence/crops can increase token use; use this path for ambiguous intervals rather than every frame by default.

[Measured results and remaining failures](BENCHMARK.md) · [Analysis fields](SHORTS_ANALYSIS.md)
