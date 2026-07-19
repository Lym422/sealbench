# SealBench

**The first public benchmark for cargo security seal detection** — recognizing
the presence and type of trailer/container door seals from images, built for
the gate-verification use case in freight security.

## Why

Cargo theft cost the U.S. supply chain an estimated **$725M in reported direct
losses in 2025 (+60% YoY)**, and seal verification at custody transfer is a
core physical control. But electronic (RFID) seals only cover single-vendor
hardware — freight from third-party shippers routinely arrives with seals a
facility's readers **cannot read but a camera can see**. Automating visual seal
verification needs data, and none is public. SealBench fills that gap.

Companion project: [carrier-verify](https://github.com/Lym422/carrier-usdot-verify)
(carrier identity verification against FMCSA data) — together they form the two
halves of gate-level physical verification: *who is taking the load* and
*is the load sealed*.

## The benchmark

7 seal classes ([taxonomy](taxonomy/seal_classes.yaml)): bolt, cable, plastic
indicative, metal strap, wire, electronic, other — plus first-class **negatives**
(hardware with no seal), because seal *absence* is the theft-relevant detection.

Three capture domains with a strict **sim-to-real protocol**:

| Domain | Source | Role |
|---|---|---|
| `synthetic` | Blender generator with domain randomization | train |
| `bench` | Real purchased seals on a trailer-door hardware rig | train / val |
| `field` | Consented + public-place photos of real trailers | **test only** |

Headline metrics: mAP@50 per domain, the **sim-to-real gap**, and
**seal-absence accuracy** on negatives. See [training/eval.py](training/eval.py).

## Status

- [x] Taxonomy, collection protocol, annotation guide, dataset card
- [x] Synthetic generator (bolt + cable) — `synthetic/generate_seals.py`
- [x] Tooling: COCO→YOLO conversion, instance-aware splits, integrity validator
- [x] Baseline training/eval harness (Ultralytics YOLO)
- [ ] v0.1 data release (bench collection in progress)
- [ ] Field test set (consented shoots)
- [ ] Baseline model weights + results table

## Quickstart

```bash
# generate synthetic training data (requires Blender >= 3.6)
blender -b -P synthetic/generate_seals.py -- --out data/synthetic --n 500

# after labeling bench/field images in Label Studio (COCO export):
python tools/to_yolo.py export.json data/bench
python tools/validate_dataset.py data/
python tools/make_splits.py data/

# train + evaluate the baseline
pip install ultralytics
python training/train_yolo.py --model yolov8s.pt
python training/eval.py runs/detect/sealbench-baseline/weights/best.pt
```

## Contributing

Seal types vary enormously by region and shipper — photo contributions of seal
types not in the taxonomy are especially welcome (see the
[collection protocol](docs/collection_protocol.md) for capture and privacy
rules; contributions must be your own images with consent where applicable).

## License & citation

Code Apache-2.0; images & annotations CC BY 4.0. Citation info in the
[dataset card](docs/dataset_card.md). No image in this dataset originates from
any commercial yard system; see the dataset card for collection ethics.
