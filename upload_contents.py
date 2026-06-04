import base64
import os
import subprocess
import pathlib
import sys

import requests

root = pathlib.Path.cwd()
owners = "erikmmmega-droid"
repo = "4.8Concurents_monitoring"
token = subprocess.check_output(["gh", "auth", "token"], text=True).strip()
headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github+json",
}

skip_dirs = {".venv", ".git", ".vscode", "competitor-monitor/desktop/build", "competitor-monitor/desktop/dist", "__pycache__"}
skip_files = {"test.txt"}

files = []
for dirpath, dirnames, filenames in os.walk(root):
    dir_rel = pathlib.Path(dirpath).relative_to(root)
    if any(part in skip_dirs for part in dir_rel.parts):
        dirnames[:] = []
        continue
    dirnames[:] = [d for d in dirnames if d not in skip_dirs and d != "__pycache__"]
    for filename in filenames:
        if filename in skip_files:
            continue
        rel_path = dir_rel / filename
        if any(part in skip_dirs for part in rel_path.parts):
            continue
        if filename.endswith(".pyc"):
            continue
        files.append(rel_path)

files.sort(key=lambda p: str(p))
print(f"Uploading {len(files)} files to {owners}/{repo}...")
for rel_path in files:
    path = "/".join(rel_path.parts)
    target = root / rel_path
    content = base64.b64encode(target.read_bytes()).decode()
    payload = {
        "message": f"Add {path}",
        "content": content,
        "branch": "main",
    }
    url = f"https://api.github.com/repos/{owners}/{repo}/contents/{path}"
    resp = requests.put(url, headers=headers, json=payload)
    if resp.status_code not in (200, 201):
        print("ERROR", path, resp.status_code, resp.text)
        sys.exit(1)
    print("OK", path)

# Remove temporary test file if exists
print("Removing temporary test file if present...")
url = f"https://api.github.com/repos/{owners}/{repo}/contents/test.txt"
resp = requests.get(url, headers=headers, params={"ref": "main"})
if resp.status_code == 200:
    sha = resp.json()["sha"]
    del_resp = requests.delete(url, headers=headers, json={"message": "Remove temporary test file", "sha": sha, "branch": "main"})
    if del_resp.status_code not in (200, 201):
        print("ERROR deleting test.txt", del_resp.status_code, del_resp.text)
        sys.exit(1)
    print("Removed test.txt")
else:
    print("No temporary test file to remove.")

print("Upload complete.")
