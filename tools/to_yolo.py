#!/usr/bin/env python3
"""Convert a COCO-format export (e.g. from Label Studio) to YOLO txt labels.

Usage:
    python tools/to_yolo.py export.json data/bench
Writes one <stem>.txt per image into data/bench/labels/, matching
data/bench/images/<stem>.<ext>. Images with no annotations get an empty file
(negatives are first-class in SealBench).
"""

import json
import sys
from collections import defaultdict
from pathlib import Path


def main(coco_path: str, out_root: str) -> None:
    coco = json.loads(Path(coco_path).read_text())
    out_labels = Path(out_root) / "labels"
    out_labels.mkdir(parents=True, exist_ok=True)

    # COCO category id -> contiguous SealBench class id via sorted category ids
    cats = sorted(c["id"] for c in coco["categories"])
    cat_map = {cid: idx for idx, cid in enumerate(cats)}
    if len(cats) > 7:
        print(f"warning: {len(cats)} categories found; SealBench v0.1 defines 7")

    anns_by_img = defaultdict(list)
    for a in coco.get("annotations", []):
        anns_by_img[a["image_id"]].append(a)

    n_boxes = 0
    for img in coco["images"]:
        w, h = img["width"], img["height"]
        stem = Path(img["file_name"]).stem
        lines = []
        for a in anns_by_img.get(img["id"], []):
            x, y, bw, bh = a["bbox"]  # COCO: top-left xywh in pixels
            cx, cy = (x + bw / 2) / w, (y + bh / 2) / h
            lines.append(
                f"{cat_map[a['category_id']]} {cx:.6f} {cy:.6f} {bw / w:.6f} {bh / h:.6f}"
            )
            n_boxes += 1
        (out_labels / f"{stem}.txt").write_text("\n".join(lines))
    print(f"wrote {len(coco['images'])} label files, {n_boxes} boxes -> {out_labels}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
