# Everything I Built in fenestr — End-to-End Explanation

Personal reference. Use this to answer any interview question about this project.

---

## 1. What is CI/CD? (The Big Picture)

**CI = Continuous Integration**
Every time you push code, a robot automatically runs your tests.
The goal: catch bugs *before* they reach users, not after.

**CD = Continuous Delivery / Deployment**
After tests pass, the robot can automatically ship your code —
to PyPI, a server, an app store, wherever.

**The mental model:**
```
You push code
    → Robot wakes up
    → Robot runs all your tests
    → Robot tells you: green (safe) or red (you broke something)
    → If green + it's a release → Robot ships to PyPI automatically
```

Without CI/CD you'd have to remember to run tests manually every time,
and remember to run the full test suite before publishing. Humans forget.
CI/CD never forgets.

---

## 2. GitHub Actions — The Engine

GitHub Actions is GitHub's built-in CI/CD system.
You describe *what to do* in a YAML file. GitHub runs it on their servers.

### Key vocabulary

| Term | What it is | Analogy |
|---|---|---|
| **Workflow** | One YAML file = one automated process | A recipe |
| **Trigger (`on:`)** | What starts the workflow | "Bake when the oven is ready" |
| **Job** | A group of steps that run on one machine | One chef doing their part |
| **Step** | One command inside a job | One line of the recipe |
| **Runner** | The virtual machine that runs jobs | The kitchen |
| **Action** | A reusable step someone else wrote | A kitchen appliance |
| **Matrix** | Run the same job N times with different inputs | Baking in 3 ovens at once |
| **Secret** | An encrypted value stored in GitHub settings | Your PIN, not written in the recipe |

### How they nest:

```
Workflow (.github/workflows/ci.yml)
└── Job: test
│   ├── Step: checkout code
│   ├── Step: set up Python
│   ├── Step: pip install tox
│   └── Step: run tox
└── Job: lint
│   └── ...
└── Job: typecheck
    └── ...
```

Jobs run **in parallel** by default (all at the same time).
Steps inside a job run **sequentially** (one after another).

---

## 3. Our CI Workflow — ci.yml Explained Line by Line

```yaml
name: CI                          # just a display name on GitHub

on:
  push:
    branches: [main]              # runs when you push to main
  pull_request:
    branches: [main]              # runs when someone opens a PR to main
```

### The test job with matrix:

```yaml
jobs:
  test:
    runs-on: ubuntu-latest        # use a fresh Ubuntu VM
    strategy:
      fail-fast: false            # if py38 fails, still run py39 and py310
      matrix:
        include:
          - python-version: "3.8"
            tox-env: py38         # maps to [testenv] in tox.ini
          - python-version: "3.9"
            tox-env: py39
          - python-version: "3.10"
            tox-env: py310
```

This creates **3 identical jobs**, each with a different Python version.
GitHub runs all 3 in parallel on 3 separate virtual machines simultaneously.

```yaml
    steps:
      - uses: actions/checkout@v4         # downloads your repo code onto the VM
      - uses: actions/setup-python@v5     # installs the right Python version
        with:
          python-version: ${{ matrix.python-version }}
      - run: pip install tox              # installs tox
      - run: tox -e ${{ matrix.tox-env }} # runs e.g. "tox -e py38"
```

`${{ matrix.tox-env }}` is GitHub Actions template syntax — it fills in
the value from the current matrix row (py38, py39, or py310).

### The lint and typecheck jobs:

These are simpler — no matrix, just one Python version:

```yaml
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.10"
      - run: pip install tox
      - run: tox -e lint            # runs flake8
```

All 5 jobs (py38, py39, py310, lint, typecheck) run at the same time.
The commit on GitHub shows red if any one of them fails.

---

## 4. Our Publish Workflow — publish.yml Explained

This workflow only fires when you push a **version tag** (e.g. `v0.1.0`).
Normal commits to main do NOT trigger it.

```yaml
on:
  push:
    tags:
      - "v*"          # matches v0.1.0, v1.0.0, v2.3.1 etc.
```

### The steps:

```yaml
- run: pip install build twine

- run: python -m build
# Creates:
#   dist/fenestr-0.1.0.tar.gz          (source distribution)
#   dist/fenestr-0.1.0-py3-none-any.whl (wheel = pre-built package)

- run: twine check dist/*
# Validates README renders correctly on PyPI, metadata is valid

- run: twine upload dist/*
  env:
    TWINE_USERNAME: __token__
    TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
# Uploads both files to PyPI using your API token
```

### How the secret works:

`secrets.PYPI_API_TOKEN` is a GitHub Secret — you set it in:
`GitHub repo → Settings → Secrets and variables → Actions`

GitHub **encrypts** it. It never appears in logs (GitHub masks it with `***`).
The workflow can read it but a human reading the logs cannot.

### The full publish flow we used:

```
1. git tag v0.1.0
2. git push origin v0.1.0
        ↓
3. GitHub sees a v* tag pushed
4. GitHub spins up an ubuntu-latest VM
5. VM checks out your code
6. VM runs: python -m build → creates dist/ files
7. VM runs: twine check → validates
8. VM runs: twine upload → sends to PyPI using your token
        ↓
9. fenestr appears at https://pypi.org/project/fenestr/
10. Anyone can now: pip install fenestr
```

---

## 5. tox — What It Is and Why We Use It

**tox** is a tool that creates isolated virtual environments and runs
commands inside them. It ensures tests run the same way locally and in CI.

### Our tox.ini:

```ini
[tox]
envlist = py38, py39, py310, lint, type

[testenv]           # default: used by py38, py39, py310
deps = pytest>=7.0.0
commands = pytest {posargs:tests}

[testenv:lint]
deps = flake8>=5.0.0
commands = flake8 src/fenestr tests

[testenv:type]
deps = mypy>=1.0.0
commands = mypy src/fenestr
```

When you run `tox -e py38`:
1. tox creates a fresh venv with Python 3.8
2. tox installs pytest into it
3. tox runs `pytest tests/`
4. tox destroys the venv

The key benefit: **every environment is isolated and reproducible**.
No "works on my machine" — tox guarantees the same environment everywhere.

---

## 6. The Project Structure — Why It Looks This Way

```
fenestr/
├── src/fenestr/      ← src-layout (modern PyPI standard)
│   ├── __init__.py   ← public API + __version__
│   ├── core.py       ← Fenestr class + module-level functions
│   ├── youtube.py    ← render_youtube(), render_youtube_playlist()
│   ├── site.py       ← render_site(), render_html(), KNOWN_BLOCKED
│   ├── validators.py ← is_valid_url(), is_youtube_url(), extract_video_id()
│   ├── exceptions.py ← FenestrError, InvalidURLError, RenderError, UnsupportedPlatformError
│   ├── logger.py     ← get_logger(), set_debug_mode()
│   └── py.typed      ← PEP 561 marker (tells mypy: this package has type hints)
├── tests/            ← pytest test suite (95 tests)
├── setup.cfg         ← package metadata + flake8/mypy config
├── pyproject.toml    ← declares the build system (setuptools)
├── tox.ini           ← test automation
└── .github/
    └── workflows/
        ├── ci.yml        ← runs on every push to main
        └── publish.yml   ← runs on every v* tag
```

**Why src-layout?** Putting code under `src/` prevents accidentally
importing from the local directory instead of the installed package.
It forces the installed version to be tested, not the raw source.

---

## 7. setup.cfg vs pyproject.toml — What Each Does

**pyproject.toml** — tells pip HOW to build the package:
```toml
[build-system]
requires = ["setuptools>=65.0", "wheel"]
build-backend = "setuptools.build_meta"
```
This is mandatory for any modern Python package. It says: "use setuptools to build me."

**setup.cfg** — tells setuptools WHAT to build (the metadata):
- Package name, version, author, description
- Which Python versions are supported
- What dependencies to install (`install_requires`)
- PyPI classifiers (searchable tags on pypi.org)
- Flake8 and mypy configuration

**Separation of concerns:** pyproject.toml = build machinery, setup.cfg = package data.

---

## 8. The Two Types of Distributions We Built

```
dist/fenestr-0.1.0.tar.gz           ← sdist (source distribution)
dist/fenestr-0.1.0-py3-none-any.whl ← wheel (binary distribution)
```

**sdist** = raw source code + build instructions. The user's machine builds it.
**wheel** = pre-built. pip installs it directly without building.

The filename `py3-none-any` means:
- `py3` = pure Python 3 (no C extensions)
- `none` = no specific ABI (no compiled binaries)
- `any` = works on any operating system (Windows, Mac, Linux)

---

## 9. What flake8 and mypy Check

**flake8** = style + syntax checker:
- Line length (we set max 99 chars)
- Unused imports
- Syntax errors
- PEP 8 violations (spacing, naming)
- Does NOT check logic or types

**mypy** = static type checker:
- Reads the type hints (`def foo(x: int) -> str:`)
- Proves that types are consistent without running the code
- We used `strict = true` which enables the strictest checks
- `py.typed` marker tells mypy our package ships type information

---

## 10. PyPI API Token — How It Works

A PyPI API token is like a password for uploading packages, but:
- Scoped: can be limited to one project only
- Revocable: deleting it immediately blocks all access
- Never shown again after creation

**"Entire account" scope** = can upload any package under your account.
Used for first upload because the project doesn't exist yet on PyPI.

**Project scope** = can only upload `fenestr`. Safer for ongoing use.

**The twine authentication flow:**
```
twine upload dist/*
    → reads TWINE_USERNAME (__token__) and TWINE_PASSWORD (your token)
    → sends POST request to https://upload.pypi.org/legacy/
    → PyPI validates the token, accepts the files
    → package appears on pypi.org
```

---

## 11. Bugs We Hit and What They Taught Us

### Bug 1: `str.removeprefix()` is Python 3.9+
We wrote `.removeprefix("www.")` in site.py.
This method didn't exist until Python 3.9.
Our package claims to support Python 3.8 → CI failed on py38.

**Lesson:** Always check the Python version compatibility of every method
you use. The Python docs show "New in version X.Y" for every addition.

**Fix:**
```python
# Before (Python 3.9+):
host = netloc.removeprefix("www.")
# After (Python 3.8 compatible):
host = netloc[4:] if netloc.startswith("www.") else netloc
```

### Bug 2: GitHub Actions ternary expression doesn't work
We tried:
```yaml
run: tox -e py${{ matrix.python-version == '3.10' && '310' || '38' }}
```
GitHub Actions expressions don't support JavaScript-style ternary chains.

**Fix:** Use `matrix.include` with explicit mappings instead of computing
values at template-expansion time.

### Bug 3: PyPI token had wrong scope
First upload always needs "Entire account" scope because the project
doesn't exist yet. Project-scoped tokens can't create new projects.

### Bug 4: Corporate SSL certificate
The corporate laptop intercepts TLS connections through a proxy CA.
Python's SSL stack rejected the self-signed corporate cert.

**Fix:** Upload from GitHub Actions servers (outside the corporate proxy).

---

## 12. Interview Questions You Should Be Able to Answer

**Q: What is CI/CD?**
CI = automated testing on every code push. CD = automated deployment
when tests pass. Together they ensure code is always tested before shipping
and releases happen through a consistent, repeatable process.

**Q: What is a GitHub Actions workflow?**
A YAML file in `.github/workflows/` that defines automated processes.
It has triggers (what starts it), jobs (groups of steps), and steps
(individual commands). Jobs run in parallel; steps run sequentially.

**Q: What is a matrix strategy in GitHub Actions?**
A way to run the same job multiple times with different inputs.
We used it to test fenestr on Python 3.8, 3.9, and 3.10 simultaneously —
3 VMs running in parallel, each with a different Python version.

**Q: How do you store secrets in GitHub Actions?**
In the repository Settings → Secrets and variables → Actions.
They're encrypted, never appear in logs, and are accessed in the workflow
as `${{ secrets.SECRET_NAME }}`.

**Q: What is the difference between a wheel and an sdist?**
An sdist is raw source code that gets built when installed.
A wheel is pre-built — pip installs it directly without a build step.
Wheels are faster to install and are the preferred format.

**Q: What is tox?**
A test automation tool that creates isolated virtual environments and
runs commands (pytest, flake8, mypy) inside them. Ensures tests run
identically locally and in CI regardless of what's installed globally.

**Q: What is the src-layout?**
Placing package code under `src/packagename/` instead of `packagename/`
at the root. Prevents accidentally importing the raw source instead of
the installed package during testing.

**Q: What does `py.typed` do?**
It's an empty marker file required by PEP 561. It tells mypy and
type-aware IDEs that this package ships inline type annotations —
no separate stub package needed.

**Q: What is PyPI and how do you publish to it?**
PyPI is the Python Package Index — the central repository where
`pip install` downloads packages from. You publish with twine:
build with `python -m build`, validate with `twine check`, upload
with `twine upload`. Authentication uses API tokens.

**Q: What is semantic versioning?**
Version numbers in the format MAJOR.MINOR.PATCH:
- PATCH (0.1.0 → 0.1.1): bug fixes, no API changes
- MINOR (0.1.0 → 0.2.0): new features, backward compatible
- MAJOR (0.1.0 → 1.0.0): breaking changes

**Q: What does flake8 check vs mypy?**
flake8 checks style and syntax (PEP 8, line length, unused imports).
mypy checks type correctness — it reads type hints and proves
at compile time that types are used consistently.

**Q: How does lazy importing work in fenestr?**
IPython is imported inside the function body, not at the top of the file.
This means `import fenestr` works even if IPython isn't installed.
The ImportError only happens if you actually call `render_youtube()` etc.

---

## 13. The Full Journey of fenestr From Code to PyPI

```
Phase 1: Scaffold
  → src-layout, setup.cfg, pyproject.toml, tox.ini

Phase 2: Exceptions + Logger
  → FenestrError hierarchy, named logger with NullHandler

Phase 3: Validators
  → is_valid_url, is_youtube_url, extract_video_id
  → 29 pytest tests

Phase 4: YouTube rendering
  → render_youtube(), render_youtube_playlist()
  → lazy IPython import, 17 tests

Phase 5: Site + HTML rendering
  → render_site(), render_html(), KNOWN_BLOCKED
  → 22 tests

Phase 6: Public API
  → Fenestr class, module-level show/youtube/site/html
  → __init__.py with __all__, __version__
  → 27 tests  →  95 total

Phase 7: Infrastructure
  → .github/workflows/ci.yml  (pytest × 3 Pythons + flake8 + mypy)
  → .github/workflows/publish.yml  (build + twine on v* tags)
  → README, CHANGELOG, demo notebook
  → py.typed PEP 561 marker

Phase 8: Publishing
  → python -m build → dist/ artifacts
  → PYPI_API_TOKEN secret in GitHub
  → git tag v0.1.0 && git push origin v0.1.0
  → GitHub Actions built and uploaded to PyPI
  → pip install fenestr works worldwide
```
