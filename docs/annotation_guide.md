# SealBench Annotation Guide v0.1

## Task
Axis-aligned bounding boxes, one per visible seal, class per
`taxonomy/seal_classes.yaml` (7 classes, ids 0-6).

## Box rules
1. **Tight box around the entire seal assembly**: for cable seals include the
   lock body AND the visible cable run (one box; if the coiled excess is
   separated by >1 box-width of background, box only the locked portion).
2. **Occlusion**: label if ≥ 25% of the seal is visible and identifiable.
3. **Truncation** at image edge: label the visible part.
4. **Multiple seals** on one hasp (common in practice): one box each.
5. **Unidentifiable small objects** (< 12 px shortest side): skip.
6. **Negatives**: bare hardware images get an empty label file — do NOT skip
   uploading them; absence is a first-class case.
7. When torn between two classes, prefer the specific class over `other_seal`;
   use `other_seal` only when genuinely novel.

## Metadata (`data/metadata.jsonl`, one JSON object per image)

```json
{
  "image": "bench/0231.jpg",
  "domain": "bench",                  // synthetic | bench | field
  "seal_instances": ["bolt-A-03"],    // physical instance ids; [] for negatives
  "capture": {
    "distance_m": 1.5, "angle_deg": 30, "light": "overcast",
    "weather": "dry", "sensor": "usb_webcam", "occlusion": "none"
  },
  "tamper_state": "intact",           // intact | cut | resealed | missing_suspected
  "number_legible": "partial",        // yes | partial | no
  "consent": "n/a",                   // yes | n/a (public) — field domain only
  "blur_applied": false
}
```

`seal_instances` powers the leakage check: `tools/make_splits.py` guarantees a
physical seal instance never crosses split boundaries.

## Quality control
- Self-review 10% random sample after each labeling session.
- Run `python tools/validate_dataset.py data/` before every commit: it checks
  label/image pairing, class-id range, box bounds, metadata completeness, and
  split leakage.
