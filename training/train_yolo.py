#!/usr/bin/env python3
"""Train the SealBench baseline detector (Ultralytics YOLO).

    pip install ultralytics
    python training/train_yolo.py --model yolov8s.pt --epochs 100
"""

import argparse

from ultralytics import YOLO


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="yolov8s.pt")
    ap.add_argument("--data", default="training/configs/sealbench.yaml")
    ap.add_argument("--epochs", type=int, default=100)
    ap.add_argument("--imgsz", type=int, default=960)
    ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--name", default="sealbench-baseline")
    args = ap.parse_args()

    model = YOLO(args.model)
    model.train(
        data=args.data,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        name=args.name,
        # gate cameras see harsh light; keep photometric augs strong,
        # geometric augs moderate (seals are small, boxes tight)
        hsv_h=0.02,
        hsv_s=0.6,
        hsv_v=0.5,
        degrees=5.0,
        translate=0.1,
        scale=0.4,
        fliplr=0.5,
        mosaic=0.7,
    )


if __name__ == "__main__":
    main()
