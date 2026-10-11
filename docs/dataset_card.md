# Dataset card: SealBench-Lite v0.1

## Summary

SealBench-Lite is a small, documented image set for training and evaluating
detectors that answer one question about a trailer rear seen from a yard
camera: is a cargo seal physically present. It is the seed of the larger
SealBench benchmark described in the Freight Custody Verification Framework
(FCVF, doi:10.5281/zenodo.23179115), and it exists so that any detector,
open or commercial, can be measured on the same images for the case that
matters most, a door with no seal.

| | |
|---|---|
| Version | 0.1 |
| Release date | October 2026 |
| License | CC BY 4.0 |
| Images | 123 yard-distance photographs: 73 train, 25 val, 25 test |
| Classes | `seal` (one class; no-seal images carry empty labels) |
| Seal types | bolt 41, padlock 34, cable 18, plastic indicative 15; electronic: none |
| Negatives | 15 unsealed trailers (9 train, 3 val, 3 test) |
| Format | YOLO (images/, labels/ with `0 cx cy w h`), `manifest.json`, `splits/*.txt` |
| Image size | median 424 by 517 pixels (356 to 615 wide); seal boxes 7 to 18 pixels wide, 11 to 30 tall |
| Distinct fleets or lessors | 12 (names not released) |
| DOI | https://doi.org/10.5281/zenodo.23290066 |

## Provenance

All images were photographed by the author with a phone, on public ground
(public roads and parking lots open to the public), from the distance a yard
or gate camera would see the trailer, [dates of capture, from the originals],
and cropped to the trailer rear. No image was captured on the author's
employer's property, of the employer's equipment, or with any camera other
than the author's own. No image, label, or line of code is shared with any
production system the author has worked on. Originals with metadata are
retained privately by the author as a record of capture; the released files
are re-encoded without metadata.

Of 153 photographs collected, 30 showed trailers carrying the author's
employer's branding or rental marks and were excluded before labeling,
redaction, or any other processing (`prepare_wild.py` in seal-check). The
remaining 123 are the release.

## Redaction

Three passes, then a check by eye of every image:

1. Lettered logos, company names, signs, license plates, trailer and
   container numbers and DOT numbers: detected with EasyOCR (two passes, one
   at 2x) and pixelated (`blur_logos.py`). Generic safety and specification
   markings such as WARNING, HIGH CUBE, 53' and 24,000 lbs were kept.
2. Pictorial emblems and placard artwork that carry no letters: builder
   ovals and lessor badges found by template matching, and the artwork
   beside lettered placards taken by widening the first-pass boxes
   (`blur_emblems.py`).
3. 31 images were finished by hand where a faint ghost of a removed decal or
   a small emblem remained (`manual_boxes.json` records the boxes).

Where a blur touched the labeled seal, the seal and a 4-pixel margin were
pasted back from the original, so no seal is altered. Seal numbers are not
redacted: they are not personal data and a detector should see real seal
faces. No people appear in any image. Fleet names are not released in the
manifest; `summary.json` gives only the count of distinct fleets.

## Splits

`make_yard_splits.py` (seed 7) assigns images at random, stratified so that
no-seal images fall in every split. The test split was held out and not used
to choose thresholds.

| split | images | with seal | no seal | by type |
|---|---|---|---|---|
| train | 73 | 64 | 9 | bolt 20, padlock 23, cable 12, plastic 9 |
| val | 25 | 22 | 3 | bolt 9, padlock 7, cable 4, plastic 2 |
| test | 25 | 22 | 3 | bolt 12, padlock 4, cable 2, plastic 4 |

The split is by image, not by trailer. Where several photographs show the
same trailer, they may fall in different splits; v0.2 will carry a
`groups.csv` and an instance-aware split.

## Known limitations

* Small. 123 images, one collector, one region, one season. Expect any model
  trained on it to be a baseline.
* Only 15 no-seal images (about one trailer in eight on the road). Absence
  numbers rest on 3 test images and should be read as a smoke signal, not a
  measurement, until v0.2 raises the count.
* The split is by image, so val and test numbers are optimistic by an
  unknown amount where the same trailer was photographed more than once.
* Bolt seals and padlocks dominate because they dominate the road. Cable and
  plastic indicative seals are under-represented; electronic seals are
  absent. Night, rain and glare are rare.
* Pixelated rectangles remain on the doors where logos and signs were. The
  seal region is untouched, so a model should not learn anything about
  seals from them, but a model may learn that a patch means a trailer. A
  user running on unblurred yard frames should check results by eye before
  trusting thresholds chosen here.
* No images of open doors with freight visible, by design.

## Intended use

Training and evaluating seal-presence detectors for custody verification
(FCVF P-11, S-3). Not intended for identifying individuals, vehicles,
fleets or companies, and the redaction is designed to prevent that. If you
find a residual identifier, open an issue at
https://github.com/Lym422/sealbench and it will be removed in the next
version.

## How to cite

Meng, L. (2026). SealBench-Lite v0.1: yard-distance photographs of trailer
rears for cargo seal presence detection [Data set]. Zenodo. https://doi.org/10.5281/zenodo.23290066

## Changes

* 0.1: first release.
