# Frame-grid video understanding: evidence and next steps

Reviewed2026-09-10. Scope: related research and engineering hypotheses, not a systematic literature review or reproduced benchmark. arXiv API metadata and full HTML methods/discussion were inspected for the four papers below. No paper code or weights integrated. Public paper text is not copied into this repository. Initial self-hosted collector was unavailable (connection refused); official arXiv API/HTML used instead.

## Closest prior art: IG-VLM

[An Image Grid Can Be Worth a Video: Zero-shot Video Question Answering Using a VLM](https://arxiv.org/abs/2403.18406),2024. Sections3,5,6 discuss image-grid conversion, grid prompting, shape/order/frame-count ablations, and spatial-temporal trade-offs. This is directly related to composing frames into one image and asking an image VLM to interpret a sequence. Therefore grid packaging is prior art, not our new research contribution. Its results concern its selected models/benchmarks, not Luna or our shorts dataset.

Engineering implication: preserve chronological order, explicit cell boundaries/identifiers, and enough pixels per frame. Test layout and frame count under a fixed pixel budget. More cells reduce per-frame detail. Our observed “two people” error is a concrete warning, not a failure demonstrated by this paper on our model.

## Thumbnail plus sampled tokens: TS-LLaVA

[TS-LLaVA: Constructing Visual Tokens through Thumbnail-and-Sampling for Training-Free Video Large Language Models](https://arxiv.org/abs/2411.11066),2024. Method sections compare concatenation, pooling, grid/grids and sampling. A few equidistant frames form a thumbnail, complemented by sampled visual tokens across input frames. It explicitly discusses grid resolution/frame-count limitations.

This is NOT merely a JPEG contact-sheet CLI: visual-token construction needs access to the model pipeline. We cannot reproduce this by setting a Luna CLI flag. A practical analogy—not an implementation of the paper—is overview sheet plus selected larger detail images or a dense short interval.

## Tool-directed follow-up: VideoAgent

[VideoAgent: A Memory-augmented Multimodal Agent for Video Understanding](https://arxiv.org/abs/2403.11481),2024. Combines structured temporal/object memory with tools such as segment localization and object querying, using an LLM to iteratively solve video tasks. Designed for longer-horizon tasks; its reported gains should not be transferred to our short clips.

Applicable architecture: expose a reliable extract command; let the calling AI choose the next time range and budget. Avoid encoding a fixed summarization workflow into the extractor. Our new --start/--end and uniform mode enable this operation, but no autonomous research-agent loop has been added.

## Attention bias: LLaVA-MLB

[LLaVA-MLB: Mitigating and Leveraging Attention Bias for Training-Free Video LLMs](https://arxiv.org/abs/2503.11205),2025. Discusses positional attention bias, query-relevant token selection, Gridded Attention Pooling and a Visual Summarization Tail. It manipulates internal visual tokens/attention, so it is not directly portable to an opaque Luna endpoint. It suggests testing early/middle/late evidence recovery rather than judging only fluent summaries; it does not establish the cause of our model's particular errors.

## Recommended improvement experiments

1. **Temporal conflation:** fixed budget, compare numbered gutters vs individual timestamped images; score incorrect simultaneous-person claims and frame attribution. Keep output uncertainty, do not force a desired answer.
2. **Running vs walking:** request a dense interval around the action (e.g.10–14s). Preserve order and timestamps, avoid motion-dedup on that interval. Judge against actual full-speed video, not selected poses. If ambiguous, use video-capable models or human review. Sparse frames alone do not prove speed.
3. **Optical-flow waste:** camera rotation/parallax can dominate motion residual. The prior10s pass did not improve action recognition; keep it out of defaults. Query-directed focused extraction is a lower-scope alternative, not a proven quality gain yet.
4. **Detail loss:** fixed canvas area; compare6/8/12 cells and supplemental large images. Account for model image resizing. Larger JPEG compression ratios do not necessarily reduce billed image tokens.
5. **Efficiency:** cache by video content hash+arguments+extractor version in a future adapter. Measure decode, packaging, model latency separately; no repeated downloads. Current code does not implement a persistent cache.

Before claiming improvement, use a diverse labeled short-video set, freeze prompts/model settings, and include endpoint coverage, action correctness, chronology, hallucinations, input tokens and p50/p95 runtime. The current CLI smoke tests verify extraction behavior, NOT model understanding. No new model accuracy benchmark was run as part of this CLI update.

## Implemented follow-through: optional shorts analysis

The later shorts-analysis extension uses individual manifest frames for fine-grained object/text/layout records, separates cross-frame subject/camera motion and exposes evidence-linked follow-up intervals. The grid extractor remains separate for coarse overview. Any image-capable AI can use prepare/import; an optional Codex adapter can run the request. This is an engineering response to the observed limitations, **not** a reproduction of TS-LLaVA or LLaVA-MLB's internal algorithms.

A live three-sample synthetic text/motion fixture and a six-sample real-video run were checked. The synthetic title and gross styling/position changes were recovered; the coarse real-video sequence did not settle the walking/running question. A denser eight-frame real-video request also hit its 240-second timeout, and a four-frame request timed out at180s with requested max effort. The same four-frame task with requested low effort completed in70.2s but still had direction/camera ambiguities; no gait-recognition gain was established. These are not controlled latency trials. See [SHORTS_ANALYSIS.md](SHORTS_ANALYSIS.md) for the current result and reproducible fixture instructions. Earlier “no model accuracy benchmark” statements describe the extraction-only update; the new smoke checks are still not a diverse accuracy benchmark.
