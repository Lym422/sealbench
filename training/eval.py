#!/usr/bin/env python3
"""SealBench evaluation — reports the headline benchmark numbers:

  1. mAP@50 / mAP@50-95 on val (bench domain) and test (field domain)
  2. THE SIM-TO-REAL GAP: val-vs-test delta, the benchmark's core metric
  3. Seal-ABSENCE accuracy on negatives (the theft-relevant case):
     an image with no ground-truth seal counts as correct only if the model
     emits no detection above --conf.

    python training/eval.py runs/detect/sealbench-baseline/weights/best.pt
"""

import argparse
import json
from pathlib import Path

from ultralytics import YOLO


def absence_accuracy(model, root: Path, split_file: Path, conf: float) -> tuple:
    imgs = [root / p for p in split_file.read_text().splitlines() if p.strip()]
    negatives = []
    for img in imgs:
        lbl = img.parent.parent / "labels" / (img.stem + ".txt")
        if lbl.exists() and not lbl.read_text().strip():
            negatives.append(img)
    if not negatives:
        return None, 0
    correct = 0
    for img in negatives:
        res = model.predict(str(img), conf=conf, verbose=False)[0]
        if len(res.boxes) == 0:
            correct += 1
    return correct / len(negatives), len(negatives)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("weights")
    ap.add_argument("--data", default="training/configs/sealbench.yaml")
    ap.add_argument("--root", default="data")
    ap.add_argument("--conf", type=float, default=0.25)
    args = ap.parse_args()

    model = YOLO(args.weights)
    report = {}
    for split in ("val", "test"):
        metrics = model.val(data=args.data, split=split, verbose=False)
        report[split] = {
            "mAP50": round(float(metrics.box.map50), 4),
            "mAP50_95": round(float(metrics.box.map), 4),
        }

    report["sim_to_real_gap_mAP50"] = round(
        report["val"]["mAP50"] - report["test"]["mAP50"], 4
    )

    root = Path(args.root)
    for split in ("val", "test"):
        acc, n = absence_accuracy(model, root, root / "splits" / f"{split}.txt", args.conf)
        report[split]["absence_accuracy"] = None if acc is None else round(acc, 4)
        report[split]["n_negatives"] = n

    print(json.dumps(report, indent=2))
    Path("eval_report.json").write_text(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
