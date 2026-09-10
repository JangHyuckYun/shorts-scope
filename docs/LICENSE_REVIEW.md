# License review (2026-09-10)

Scope: code actually reused or required by this fork, not a blanket legal clearance for content/platform use.

- claude-video: upstream root LICENSE at83da59fa78c3eee9e20f515fe75c438bb5166efd is MIT, copyright2026 Bradley Bonanno. Original notice and full license retained unchanged. MIT permits copying, modifying, publishing, selling and commercial use; retain notice and disclaimer. Our compact adapter is distributed under the same MIT license.
- Pillow: optional installed dependency; installed12.3.0 metadata identifies MIT-CMU. Permissive commercial use, with applicable notice requirements when redistributing. No Pillow binaries or source bundled. https://github.com/python-pillow/Pillow/blob/main/LICENSE
- FFmpeg/ffprobe: external executables, not bundled. FFmpeg is principally LGPL2.1-or-later, but configured components can make a build GPL or non-redistributable. This fork does not imply every binary is redistributable; check your build before bundling. https://ffmpeg.org/legal.html
- yt-dlp: used by unchanged upstream URL flow, not required for local compact adapter. Source is Unlicense; packaged binaries/dependencies can carry additional licenses. Do not assume a bundled binary inherits only the source license. https://github.com/yt-dlp/yt-dlp#license
- PySceneDetect (installed metadata BSD-3-Clause), OpenCV (installed metadata Apache2.0), NumPy (mixed permissive metadata): used only in separate earlier experiments, NOT dependencies or copied code of this adapter. No binaries, experiment scripts or test media from those experiments are included here.
- TransNetV2, Qwen3-VL, VideoLLaMA3, Decord and claude-real-video: discussed as candidates but no code/weights copied into this fork; their licenses are not cleared for future integration by this review.

No incompatibility identified for publishing this MIT fork with an optional Pillow dependency and external FFmpeg. This is a repository-level license review, not a warranty of third-party authorship, patent rights or compliance for every commercial deployment. MIT provides no warranty. Video/music copyright, personal-data processing, site terms and model-provider terms remain separate. Brand mentions describe compatibility and do not imply endorsement.

## Shorts-analysis extension

The analysis adapter, JSON schema, tests and synthetic-fixture generator are additions under this repository's MIT license. They do not copy paper implementations or bundle model weights. The optional Codex command is an external, separately installed/authenticated program; its service/account terms and any analysis charges remain separate from the fork's code license. No Codex binaries, credentials, font files or third-party reference media are included. The fixture generator takes a user's local font path; users retain responsibility for that font's applicable terms when distributing generated assets or bundling a font.
