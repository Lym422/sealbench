# Dataset Card — SealBench v0.1 (template; fill bracketed fields at release)

## Summary
SealBench is the first public benchmark for **cargo security seal detection**:
recognizing the presence and type of trailer/container door seals from images,
across bolt, cable, plastic indicative, metal strap, wire, and electronic seal
types. It targets the gate-verification use case in freight security, where
RFID readers only cover single-vendor e-seals and human checks don't scale.

- **Curated by:** Lingyu Meng (independent work)
- **License:** images & annotations CC BY 4.0; code Apache-2.0
- **Size:** [N_syn] synthetic + [N_bench] bench-rig + [N_field] field images
- **Task:** object detection (7 classes) + seal-absence verification

## Motivation
Cargo theft losses reached ~$725M (reported) in 2025 (+60% YoY, Verisk
CargoNet); seal presence/integrity at custody transfer is a core physical
control, but no public data exists for training or comparing detectors. RFID
e-seals cover only a fraction of real freight; third-party vendor seals are
routinely unreadable electronically yet visually recognizable.

## Composition & the sim-to-real protocol
Three capture domains: `synthetic` (Blender, domain-randomized), `bench`
(purchased seals on real trailer-door hardware rig), `field` (consented and
public-place photos of real trailers). **The official protocol trains on
synthetic+bench only and tests on field** — the benchmark's headline metric is
the sim-to-real transfer gap, plus seal-absence accuracy on negatives (the
theft-relevant failure mode).

## Collection & consent
See [collection_protocol.md](collection_protocol.md). No image originates from
any commercial yard system or employer facility. Field images are either
consented (signed forms held by the maintainer) or taken from public property;
all plates, USDOT/MC numbers, logos, and faces are blurred.

## Known limitations
- Bench-rig images use a plywood door mock, not full trailer geometry.
- v0.1 synthetic generator covers bolt and cable seals only.
- Class balance follows purchasability, not real freight distribution.
- Tamper-state (cut/resealed) is metadata-only in v0.1, not a detection target.

## Intended & out-of-scope use
Intended: research and engineering of seal detection/verification, sim-to-real
transfer study, gate-automation prototyping. Out of scope: identifying
individuals, companies, or specific shipments; any use of the imagery to plan
interference with cargo.

## Citation
```
@misc{meng2026sealbench,
  author = {Meng, Lingyu},
  title  = {SealBench: A Benchmark for Cargo Security Seal Detection},
  year   = {2026},
  url    = {https://github.com/Lym422/sealbench}
}
```
