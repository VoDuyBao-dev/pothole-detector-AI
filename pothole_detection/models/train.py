# yolo_training/train.py
import argparse, os
from ultralytics import YOLO

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=str, required=True, help="path to data.yaml")
    parser.add_argument("--model", type=str, default="yolo11s.pt")
    parser.add_argument("--epochs", type=int, default=60)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--name", type=str, default="pothole11")
    args = parser.parse_args()

    model = YOLO(args.model)
    model.train(
        data=args.data,
        epochs=5,
        # epochs=args.epochs,
        imgsz=args.imgsz,
        batch=-1,
        device=0,
        patience=15,
        project="runs",
        name=args.name,
    )
    print(f"Done. Check runs/detect/{args.name}/weights/best.pt")

if __name__ == "__main__":
    main()
