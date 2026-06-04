# Competitor Monitor — Desktop build & publish guide

This repository contains the Competitor Monitor backend and a simple PyQt6 desktop client in competitor-monitor/desktop/.

What I added:
- competitor-monitor/desktop/main.py — PyQt6 minimal desktop app that calls backend endpoints.
- competitor-monitor/desktop/build.py — build script using PyInstaller to create a single .exe.
- .env template and .gitignore updated to ignore .env and build artifacts.

How to build locally (Windows):

1. Activate your virtualenv and install dependencies:
   pip install -r competitor-monitor/requirements.txt
   pip install pyqt6 pyinstaller requests

2. Configure secrets: copy .env and fill PROXY_API_KEY.

3. Run backend (in project root):
   uvicorn competitor-monitor.backend.main:app --reload --host 0.0.0.0 --port 8000

4. Build the desktop app:
   cd competitor-monitor/desktop
   python build.py

Result: dist/CompetitionMonitor.exe (one-file bundle). Run it and point to backend URL.

Publishing to GitHub:
- I cannot create or publish the repo from this environment. To publish locally:
  1) Create a new repo on GitHub (via web UI or GitHub CLI).
  2) Run locally:
     git init
     git add .
     git commit -m "Add desktop client and build script"
     git branch -M main
     git remote add origin https://github.com/<your-username>/<repo-name>.git
     git push -u origin main

Security: do NOT commit your real .env with secrets.

If you want, I can create a GitHub Actions workflow to build the exe, or help prepare a release PR. You will need to run the final push locally (or provide credentials).
