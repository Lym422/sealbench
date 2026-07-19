#!/usr/bin/env python3
"""Build the official SealBench splits, enforcing the sim-to-real protocol:

  train = synthetic + ~80% of bench (by SEAL INSTANCE, not by image)
  val   = remaining ~20% of bench instances
  test  = ALL field images (never trainable)

Usage:
    python tools/make_splits.py data/ --seed 42
Writes data/splits/{train,val,test}.txt (image paths) and stamps each metadata
record with its split. Grouping by physical seal instance prevents the classic
leakage bug where near-duplicate shots of one seal land in both train and val.
"""

import argparse
import json
import random
from collections import defaultdict
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default="data")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--val-frac", type=float, default=0.2)
    args = ap.parse_args()

    root = Path(args.root)
    meta_path = root / "metadata.jsonl"
    records = [json.loads(l) for l in meta_path.read_text().splitlines() if l.strip()]

    # group bench images by seal instance (negatives group under "__negative__")
    bench_by_inst = defaultdict(list)
    splits = {"train": [], "val": [], "test": []}
    for rec in records:
        if rec["domain"] == "synthetic":
            splits["train"].append(rec)
        elif rec["domain"] == "field":
            splits["test"].append(rec)
        else:
            key = rec["seal_instances"][0] if rec["seal_instances"] else "__negative__"
            bench_by_inst[key].append(rec)

    instances = sorted(k for k in bench_by_inst if k != "__negative__")
    rng = random.Random(args.seed)
    rng.shuffle(instances)
    n_val = max(1, int(len(instances) * args.val_frac)) if instances else 0
    val_instances = set(instances[:n_val])

    negatives = bench_by_inst.pop("__negative__", [])
    rng.shuffle(negatives)
    n_val_neg = int(len(negatives) * args.val_frac)

    for inst, recs in bench_by_inst.items():
        splits["val" if inst in val_instances else "train"].extend(recs)
    splits["val"].extend(negatives[:n_val_neg])
    splits["train"].extend(negatives[n_val_neg:])

    out = root / "splits"
    out.mkdir(exist_ok=True)
    for name, recs in splits.items():
        (out / f"{name}.txt").write_text("\n".join(r["image"] for r in recs))
        for r in recs:
            r["split"] = name
        print(f"{name}: {len(recs)} images")

    meta_path.write_text("\n".join(json.dumps(r) for r in records))
    print(f"splits written to {out}/, metadata.jsonl updated with split field")


if __name__ == "__main__":
    main()
