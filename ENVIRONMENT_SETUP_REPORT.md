# Environment setup report — November 16, 2026

**Status: dependencies installed successfully; tests, Streamlit workflows and localhost startup verified.**

Host: macOS/Darwin 27.2.0, Apple Silicon arm64, zsh. Existing isolated `.venv` uses Xcode Python **3.9.6**, with system-site-packages disabled. No global packages were modified. Python 3.12/3.13 was not found in standard Homebrew, framework, pyenv or uv locations. The resolver selected compatible releases. A supported Python refresh remains recommended.

## Verified environment

Direct requirements: Streamlit **1.50.0**, pandas **2.3.3**, pytest **8.4.2**. NumPy **2.0.2** and PyArrow **21.0.0** are installed as dependencies. `pip check` reports **No broken requirements found**. Pip remains 21.2.4; an upgrade is not required for the successful current installation. Complete tested pins are recorded in `requirements-lock.txt` (Python 3.9/macOS environment); machine-readable inventory: `outputs/installed_packages.json`.

- altair 5.5.0
- attrs 26.1.0
- blinker 1.9.0
- cachetools 6.2.6
- certifi 2026.10.23
- charset-normalizer 3.5.2
- click 8.1.8
- exceptiongroup 1.3.1
- gitdb 4.0.12
- GitPython 3.2.1
- idna 3.20
- iniconfig 2.1.0
- Jinja2 3.1.6
- jsonschema 4.25.1
- jsonschema-specifications 2025.9.1
- MarkupSafe 3.0.4
- narwhals 2.21.0
- numpy 2.0.2
- packaging 25.0
- pandas 2.3.3
- pillow 11.3.0
- pip 21.2.4
- pluggy 1.6.0
- protobuf 6.33.6
- pyarrow 21.0.0
- pydeck 0.9.3
- Pygments 2.21.0
- pytest 8.4.2
- python-dateutil 3.0.0
- pytz 2026.6
- referencing 0.36.2
- requests 2.32.5
- rpds-py 0.27.1
- setuptools 58.0.4
- six 1.17.0
- smmap 5.0.3
- streamlit 1.50.0
- tenacity 9.1.2
- toml 0.10.2
- tomli 2.5.0
- tornado 6.5.10
- typing_extensions 4.16.0
- tzdata 2026.6
- urllib3 2.6.3

## Installation and resolution

Multiple earlier attempts failed DNS resolution inside the sandbox, timed out, reset connections, or returned incomplete wheels rejected by SHA-256 verification. No package hash checks were bypassed. The successful attempt used network escalation, a writable cache at `/private/tmp/bancinc-pip-cache`, a 180-second timeout and five retries. Pip then verified and installed all required dependencies. Full installation output: `outputs/dependency_install_retry.log`.

```sh
.venv/bin/python -m pip install --cache-dir /private/tmp/bancinc-pip-cache --timeout 180 --retries 5 --progress-bar off --disable-pip-version-check -r requirements.txt
.venv/bin/python -m pip check
.venv/bin/python -m pytest -v --junitxml=outputs/tests.xml
.venv/bin/python scripts/verify_ui.py
.venv/bin/python -m streamlit run app.py --server.address 127.0.0.1 --server.headless true --browser.gatherUsageStats false
```

The application is running at **http://127.0.0.1:8501** in the setup session. The health endpoint returned `ok`. Socket binding and localhost requests required sandbox escalation. Startup evidence: `outputs/startup_verification.txt`.

## Validation

- Full pytest suite: **24 passed in 8.09 seconds**, including all nine original tests.
- All five prepared AppTest workflow groups passed.
- Fresh feature rebuild from the authorized original ZIP completed at cutoff **2026-07-01**, processing **1,048,575 transactions / 50,000 customers**, with zero invalid links/dates and duplicate transaction IDs reported.
- Rebuilt and supplied features match across all 50,000 customer keys and all 16 non-key columns. Original features were preserved; rebuilt sensitive artifacts are in ignored `outputs/rebuild_verification/`.

## Configuration and remaining limits

`.gitignore` excludes environments, datasets, generated outputs, secrets and local databases. `BANCINC_FEATURES_PATH` controls the input feature location; `.env.example` documents it. The app gives missing-file/schema guidance. No Git repository is initialized and no dataset was committed. Source syntax was checked using AST parsing after a compileall attempt hit an external bytecode-cache permission error.

No browser visual acceptance was performed. Audit remains session-only. Historical model metrics remain reported rather than reproduced because evaluation code and explicit experiment definitions are absent. The installed Streamlit emits non-fatal `use_container_width` deprecation messages; these do not prevent tested workflows. See the prototype report and development priorities.
