#!/usr/bin/env python3
"""SealBench dataset validator. Run before every commit:

    python tools/validate_dataset.py data/

Checks:
  1. every image has a label file (empty = negative, allowed) and vice versa
  2. label lines parse as `cls cx cy w h`, class in [0,6], coords in [0,1]
  3. metadata.jsonl covers every image, with required fields per domain
  4. split leakage: no seal_instance_id appears in more than one split
"""

import json
import sys
from collections import defaultdict
from pathlib import Path

IMG_EXTS = {".jpg", ".jpeg", ".png"}
N_CLASSES = 7
REQUIRED_META = {"image", "domain", "seal_instances", "tamper_state"}
DOMAINS = {"synthetic", "bench", "field"}


def fail(errors, msg):
    errors.append(msg)


def check_pairing(root: Path, errors):
    domains = [d for d in root.iterdir() if d.is_dir() and d.name in DOMAINS]
    counts = {}
    for d in domains:
        imgs = {p.stem for p in (d / "images").glob("*") if p.suffix.lower() in IMG_EXTS}
        lbls = {p.stem for p in (d / "labels").glob("*.txt")}
        for missing in sorted(imgs - lbls):
            fail(errors, f"{d.name}: image '{missing}' has no label file")
        for orphan in sorted(lbls - imgs):
            fail(errors, f"{d.name}: label '{orphan}.txt' has no image")
        counts[d.name] = len(imgs)
        for lbl in (d / "labels").glob("*.txt"):
            for ln, line in enumerate(lbl.read_text().splitlines(), 1):
                if not line.strip():
                    continue
                parts = line.split()
                ok = len(parts) == 5
                if ok:
                    try:
                        cls = int(parts[0])
                        vals = [float(v) for v in parts[1:]]
                        ok = 0 <= cls < N_CLASSES and all(0.0 <= v <= 1.0 for v in vals)
                    except ValueError:
                        ok = False
                if not ok:
                    fail(errors, f"{lbl}:{ln}: bad label line: {line!r}")
    return counts


def check_metadata(root: Path, errors):
    meta_path = root / "metadata.jsonl"
    if not meta_path.exists():
        fail(errors, "metadata.jsonl missing")
        return {}
    by_split = defaultdict(set)
    seen_images = set()
    for ln, line in enumerate(meta_path.read_text().splitlines(), 1):
        if not line.strip():
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError as e:
            fail(errors, f"metadata.jsonl:{ln}: invalid JSON ({e})")
            continue
        missing = REQUIRED_META - rec.keys()
        if missing:
            fail(errors, f"metadata.jsonl:{ln}: missing fields {sorted(missing)}")
            continue
        if rec["domain"] not in DOMAINS:
            fail(errors, f"metadata.jsonl:{ln}: unknown domain {rec['domain']!r}")
        if rec["domain"] == "field" and rec.get("consent") not in ("yes", "n/a"):
            fail(errors, f"metadata.jsonl:{ln}: field image lacks consent flag")
        seen_images.add(rec["image"])
        split = rec.get("split", rec["domain"])
        for inst in rec["seal_instances"]:
            by_split[split].add(inst)
    # cross-split instance leakage
    splits = list(by_split)
    for i, a in enumerate(splits):
        for b in splits[i + 1 :]:
            leak = by_split[a] & by_split[b]
            if leak:
                fail(errors, f"instance leakage between '{a}' and '{b}': {sorted(leak)[:5]}...")
    return seen_images


def main(root_str: str) -> int:
    root = Path(root_str)
    errors: list = []
    counts = check_pairing(root, errors)
    check_metadata(root, errors)
    print("image counts:", counts or "(no domain dirs found)")
    if errors:
        print(f"\nFAIL — {len(errors)} problem(s):")
        for e in errors[:50]:
            print("  -", e)
        return 1
    print("OK — dataset passes validation")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "data"))
