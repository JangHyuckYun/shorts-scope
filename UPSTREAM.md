# Origin and retained attribution

ShortsScope is a community fork of [bradautomates/claude-video](https://github.com/bradautomates/claude-video), originally authored by Bradley Bonanno. Reused source is covered by the original [MIT LICENSE](LICENSE), retained verbatim. [Original project history and changelog](https://github.com/bradautomates/claude-video/blob/83da59fa78c3eee9e20f515fe75c438bb5166efd/CHANGELOG.md).

The fork reuses fast frame extraction/configuration utilities. Python files remain under the historical `skills/watch/scripts/` path to preserve imports and compatibility. Retained upstream download/transcription/setup utilities are source compatibility material, not the advertised ShortsScope workflow or automatic installation hooks.

ShortsScope distributes its own `extract` / `measure` / `analyze` CLI and the exported `shorts-scope` skill. The inherited `/watch` skill registration, marketplaces, plugin branding, automatic setup hooks, development cache sync, old skill packager and tag-triggered release workflow were removed. Those installation/release paths described a different product. Upstream version tags were removed from this fork; upstream itself and its tags were not modified. Git ancestry and the GitHub fork relationship are preserved.

Keeping attribution is a license requirement, not stale branding. No affiliation with the named agent/model providers is implied. See [LICENSE_REVIEW.md](docs/LICENSE_REVIEW.md) for optional dependencies and external assets.
