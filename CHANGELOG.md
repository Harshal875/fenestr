# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-03-28

### Added

- `Fenestr` class — class-based API with configurable `default_width` / `default_height`
- `fenestr.show(url)` — smart dispatch: routes YouTube URLs to `render_youtube`, all
  other HTTPS URLs to `render_site`
- `fenestr.youtube(url, autoplay)` — render a YouTube video via IFrame
- `fenestr.site(url)` — render any HTTPS website via IFrame
- `fenestr.html(content)` — render a raw HTML string using `IPython.display.HTML`
- `render_youtube_playlist(playlist_id)` — embed a YouTube playlist
- `validators` module: `is_valid_url`, `is_https`, `is_youtube_url`, `extract_video_id`
- `exceptions` module: `FenestrError`, `InvalidURLError`, `RenderError`,
  `UnsupportedPlatformError`
- `logger` module: named `"fenestr"` logger with `NullHandler`; `set_debug_mode()` helper
- `KNOWN_BLOCKED` frozenset — warns when rendering known iframe-blocking domains
- Lazy IPython import — fenestr can be imported in non-Jupyter environments without error
- Full pytest test suite (95 tests) with mocked IPython
- GitHub Actions CI: pytest on Python 3.8 / 3.9 / 3.10, flake8, mypy
- `src`-layout with `setup.cfg` / `pyproject.toml` / `tox.ini`

[Unreleased]: https://github.com/your-username/fenestr/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/your-username/fenestr/releases/tag/v0.1.0
