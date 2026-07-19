# SealBench Collection Protocol v0.1

Goal: a curated, fully-owned benchmark of cargo-seal imagery across ≥6 seal
types, three capture domains, and controlled variation — **without access to any
operational yard**. Target for v0.1 release: **~1,500 real images + unlimited
synthetic**, with a strict sim-to-real evaluation protocol.

## 1. The three capture domains

| Domain | Source | Role in benchmark |
|---|---|---|
| `synthetic` | Blender generator (`synthetic/generate_seals.py`) | Training scale |
| `bench` | Purchased seals on trailer-door hardware rig | Training + validation |
| `field` | Consented real trailers, public-place photos, CDL school / rental shoots | **Test set only** (sim-to-real gap measurement) |

**Split rule (non-negotiable): no `field` image is ever used for training in the
official benchmark, and no physical seal instance appears in more than one
split.** This is what makes the benchmark scientifically interesting: it
measures transfer from cheap data (synthetic + bench) to the real world.

## 2. Shopping list (~$120 total)

**Seals (Uline, Amazon, or eBay; buy 5-10 of each):**
- Bolt seals, 2 brands/colors (~$15)
- Cable seals, 1.5mm and 3.5mm (~$20)
- Plastic pull-tight indicative seals, 3 colors (~$12)
- Metal strap / ball seals (~$10)
- Wire + crimp seals (~$8)
- If findable: one reusable RFID/e-seal (eBay used, ~$20)

**Rig (eBay "trailer door lock rod kit", truck parts stores):**
- Cam-lock rod + keeper + hasp assembly (~$30-50)
- Plywood sheet 2'x3', white/gray exterior paint (~$15)
- Aging kit: sandpaper, mud, rust-effect spray, WD-40 grime (~$10)

## 3. Bench-rig shot list (per seal instance)

Mount hardware on painted plywood; apply one seal; complete the matrix below,
then cut the seal off and record 3 "cut/tampered" shots for v2 metadata.

| Axis | Values (capture all combinations where practical) |
|---|---|
| Distance | 0.5 m (seal-number range), 1.5 m, 3 m (gate-camera range) |
| Angle | head-on, 30°, 60°, low-angle-up |
| Light | midday sun, overcast, golden hour, night + flashlight, night + headlights |
| Weather sim | dry, water-sprayed, mud-flecked |
| Sensor | phone main cam, phone wide, cheap USB webcam (gate-camera realism) |
| Occlusion | none, partial (hand, strap, shadow) |

≥ 5 seal instances/type x ~15 kept frames = **~450-700 bench images per weekend**.
Also capture **no-seal negatives** of the bare rig under the same matrix (~100).

**Metadata per image** (see `docs/annotation_guide.md`): seal_instance_id,
class, domain=bench, distance, angle, light, weather, sensor, tamper_state.

## 4. Field capture (test set)

Priority order:
1. **CDL school / driving school session** — call 2-3 local schools; offer $50
   for an hour with a parked trailer. Bring your seals; apply, photograph, remove.
2. **Trailer rental** (Penske et al. rent semi trailers day-rate) — full control,
   fully consented, one afternoon yields hundreds of in-domain images.
3. **Owner-operator consent shoots** — truck stops, trucking Facebook groups;
   $20 to photograph their (already sealed or your-sealed) rear door. Get a
   one-line signed consent (template below).
4. **Public-place photography** — trailers visible from public streets/sidewalks.
   Lawful in the US from public property; crop to door region, blur plates and
   logos before inclusion. Use judgment and be respectful; never enter property.

Target: **300-500 field images**, ≥ 4 seal classes, ≥ 5 distinct trailers.

**Consent template:** "I, ____, authorize Lingyu Meng to photograph the rear
door and seal area of my trailer for inclusion in a public research dataset.
Identifying marks (plates, logos) will be blurred. Date/Signature."

## 5. Privacy & publication rules

- Blur all license plates, USDOT/MC numbers, company names/logos, and faces
  before an image enters the repo.
- No image may originate from any employer system, device, or facility —
  including "reference" use.
- Field images from private property require signed consent (keep forms
  privately; note `consent=yes` in metadata).

## 6. Labeling

Use [Label Studio](https://labelstud.io) locally, bounding boxes with the
7-class taxonomy (`taxonomy/seal_classes.yaml`). Export COCO JSON →
`tools/to_yolo.py` converts to YOLO format. `tools/validate_dataset.py` checks
integrity before any split is built. See `docs/annotation_guide.md`.
