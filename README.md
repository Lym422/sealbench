# SealBench

**The first documented public benchmark for cargo security seal detection**:
recognizing the presence and type of trailer and container door seals from
images, built for the gate-verification use case in freight security.

"Documented" is deliberate. A few small seal image sets exist on model-sharing
sites (a few hundred images, one class, no description, no negatives, no
protocol). They show there is demand; they are not benchmarks. SealBench has a
taxonomy, a collection protocol with privacy rules, first-class no-seal
negatives, a sim-to-real protocol, and a dataset card that says where every
image came from.

SealBench is the evaluation layer of the
[Freight Custody Verification Framework](https://doi.org/10.5281/zenodo.23179115)
(FCVF), an open specification for verifying carrier identity and load
integrity at freight custody transfers. Requirement P-11 of the framework asks
for a detector that reports seal present, absent, or uncertain for seals of
any type; SealBench is how such detectors are measured, and
[seal-check](https://github.com/Lym422/seal-check) is the open reference
detector trained and evaluated on it.

## Why

Cargo theft cost the U.S. supply chain an estimated **$725M in reported direct
losses in 2025 (+60% YoY)**, and seal verification at custody transfer is a
core physical control. But electronic (RFID) seals only cover single-vendor
hardware; freight from third-party shippers routinely arrives with seals a
facility's readers **cannot read but a camera can see**. Automating visual seal
verification needs data, and no documented data is public. SealBench fills
that gap.

Companion projects:
[carrier-verify](https://github.com/Lym422/carrier-usdot-verify) (carrier
identity verification against FMCSA data) and
[seal-check](https://github.com/Lym422/seal-check) (the seal presence
detector). Together they are the two halves of gate-level physical
verification: *who is taking the load* and *is the load sealed*.

## The benchmark

7 seal classes ([taxonomy](taxonomy/seal_classes.yaml)): bolt, cable, plastic
indicative, metal strap, wire, electronic, other, plus first-class
**negatives** (hardware with no seal), because seal *absence* is the
theft-relevant detection.

Capture domains. The primary one is the yard camera, because that is the
camera a facility already has: it sees the whole trailer rear from the gate
post or a pole, and it does not take close-ups. On such a frame the seal is
7 to 30 pixels across. Close-ups and synthetic renders are supplements, not
the main course.

| Domain | Source | Role |
|---|---|---|
| `wild` (yard distance) | Public-place photos of real trailers from where a yard camera sits, cropped to the trailer rear, seals 7 to 30 px; released as SealBench-Lite v0.1 (https://doi.org/10.5281/zenodo.23290066) | **train / val / test** (primary) |
| `closeup` | Real trailer doors in public lots, framed from 2 to 4 m, for sites that have a near camera | optional train / val |
| `bench` | Real purchased seals on a trailer-door hardware rig | optional train |
| `synthetic` | Blender generator with domain randomization | optional train |

Headline metrics: image-level **seal-absence accuracy** on negatives,
presence recall, uncertain rate (the FCVF P-11 answers), then mAP@50 per
domain and the gap between the supplements and the yard domain. See
[training/eval.py](training/eval.py) and seal-check's `scripts/evaluate.py`.

## Provenance

Every image was photographed by the author with a phone, on public ground
(public roads and parking lots open to the public) or on a bench rig of
purchased seals, or rendered synthetically. No image was captured on the
author's employer's property, of the employer's equipment, or with any
camera other than the author's own, and trailers carrying the employer's
branding or rental marks are excluded from every release. License plates,
trailer and container numbers, and other readable identifiers are blurred
before release; metadata is stripped. No image, label, or line of code is
shared with any production system. See the
[dataset card](docs/dataset_card.md).

## Status

- [x] Taxonomy, collection protocol, annotation guide, dataset card
- [x] Synthetic generator (bolt + cable): `synthetic/generate_seals.py`
- [x] Tooling: COCO to YOLO conversion, instance-aware splits, integrity validator
- [x] Baseline training/eval harness (Ultralytics YOLO)
- [x] **Wild yard-distance set v0.1** (October 10, 2026): 123 third-party trailers, 108 with seal and 15 without, bolt 41, padlock 34, cable 18, plastic indicative 15; logos, signs and plates blurred; `data/wild/` with manifest and summary. Split 73 / 25 / 25 by seal-check's `make_yard_splits.py`.
- [ ] More yard-distance images, above all no-seal (target 60 no-seal, about 240 total) and an instance-aware split
- [ ] Close-up and bench supplement (optional)
- [x] **SealBench-Lite v0.1 data release** (October 11, 2026): https://doi.org/10.5281/zenodo.23290066, CC BY 4.0, 123 images with labels, splits, dataset card
- [x] Baseline model weights and results table: seal-check v0.1, https://github.com/Lym422/seal-check/releases/tag/v0.1 (test split: 20 of 22 sealed called present, 3 of 3 unsealed called absent)

## Quickstart

```bash
# generate synthetic training data (requires Blender >= 3.6)
blender -b -P synthetic/generate_seals.py -- --out data/synthetic --n 500

# after labeling bench/close-up images in Label Studio (COCO export):
python tools/to_yolo.py export.json data/bench
python tools/validate_dataset.py data/
python tools/make_splits.py data/

# train + evaluate the baseline
pip install ultralytics
python training/train_yolo.py --model yolov8s.pt
python training/eval.py runs/detect/sealbench-baseline/weights/best.pt

# or evaluate with the FCVF image-level metrics (present / absent / uncertain):
# see https://github.com/Lym422/seal-check, scripts/evaluate.py
```

## Contributing

Seal types vary enormously by region and shipper, so photo contributions of
seal types not in the taxonomy are especially welcome (see the
[collection protocol](docs/collection_protocol.md) for capture and privacy
rules; contributions must be your own images, taken on public ground or with
the site's consent, with plates and identifiers blurred).

## License and citation

Code Apache-2.0; images and annotations CC BY 4.0. Data: Meng, L. (2026).
SealBench-Lite v0.1: yard-distance photographs of trailer rears for cargo
seal presence detection [Data set]. Zenodo. https://doi.org/10.5281/zenodo.23290066
Framework:
Meng, L. (2026). Freight Custody Verification Framework, v0.1-draft. Zenodo.
https://doi.org/10.5281/zenodo.23179115
