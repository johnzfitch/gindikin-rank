#!/usr/bin/env python3
"""Regenerate MANIFEST.md digests. Run from the archive root."""
import hashlib, os, sys
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(root)
for dirpath, dirs, files in os.walk("."):
    dirs[:] = [d for d in dirs if d not in ("__pycache__", ".git")]
    for f in sorted(files):
        p = os.path.join(dirpath, f).replace("./", "")
        if p in ("MANIFEST.md",):
            continue
        h = hashlib.sha256(open(p, "rb").read()).hexdigest()
        print(f"{h}  {p}")
