# fenestr

> A window into the web — render YouTube videos and websites inside Jupyter Notebook cells.

[![PyPI version](https://img.shields.io/pypi/v/fenestr.svg)](https://pypi.org/project/fenestr/)
[![Python versions](https://img.shields.io/pypi/pyversions/fenestr.svg)](https://pypi.org/project/fenestr/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Overview

**fenestr** (from Latin *fenestra*, meaning window) is a Python library that lets data scientists
embed YouTube videos and arbitrary websites directly inside Jupyter Notebook output cells —
no browser switching required.

## Installation

```bash
pip install fenestr
```

## Quick Start

```python
from fenestr import open_window

# Render a YouTube video
open_window("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

# Render a website
open_window("https://example.com", width=900, height=600)
```

## API

| Symbol | Description |
|---|---|
| `open_window(url, **kwargs)` | Smart dispatch — returns a `YouTubeWindow` or `SiteWindow` |
| `YouTubeWindow(url, ...)` | Embed a YouTube video via iframe |
| `SiteWindow(url, ...)` | Embed any website via iframe |

## Development

```bash
pip install -e ".[dev]"
tox          # run all checks (pytest + flake8 + mypy)
tox -e lint  # linting only
tox -e type  # type checking only
```

## License

MIT
