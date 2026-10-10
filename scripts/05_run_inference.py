#!/usr/bin/env python3
"""
RangRakshak - Live Defect Detection & Quality Inspection Routine
Runs YOLOv11 inference on synthetic validation panels or live streams.
Annotates detected defects with bounding boxes and logs PASS/REJECT verdicts to CSV.
"""

import os
import glob
import time
import argparse
import csv
import cv2
from pathlib import Path

def run_inspection(weights_path, source_dir="data/synthetic/images/val", output_dir="runs/inspection_results", output_csv="runs/inspection_log.csv"):
    try:
        from ultralytics import YOLO
    except ImportError:
        print("❌ Error: ultralytics is not installed. Run: pip install ultralytics")
        return

    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.dirname(output_csv) if os.path.dirname(output_csv) else ".", exist_ok=True)

    print("=" * 60)
    print("🔍 RangRakshak: Initiating Real-Time Quality Inspection")
    print("=" * 60)
    print(f"📦 Loading weights from: {weights_path}")
    model = YOLO(weights_path)
    
    # Collect sample test frames
    image_paths = sorted(glob.glob(os.path.join(source_dir, "*.jpg")) + glob.glob(os.path.join(source_dir, "*.png")))
    if not image_paths:
        print(f"⚠️ No images found in {source_dir}. Run scripts/01_generate_defects.py first!")
        return

    print(f"📸 Found {len(image_paths)} automotive panels to inspect in {source_dir}\n")

    with open(output_csv, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "panel_file", "verdict", "defect_count", "detected_classes", "confidences"])

        total_inspected = 0
        total_rejected = 0

        for img_path in image_paths[:50]:  # Inspect first 50 panels for demo
            start_t = time.time()
            results = model.predict(source=img_path, conf=0.25, verbose=False)[0]
            infer_time = (time.time() - start_t) * 1000

            total_inspected += 1
            boxes = results.boxes
            num_defects = len(boxes)

            defect_names = [results.names[int(cls)] for cls in boxes.cls.tolist()] if num_defects > 0 else []
            confs = [f"{conf:.2f}" for conf in boxes.conf.tolist()] if num_defects > 0 else []

            if num_defects > 0:
                verdict = "REJECT"
                total_rejected += 1
                color_tag = "\033[91m[REJECT]\033[0m"
            else:
                verdict = "PASS"
                color_tag = "\033[92m[PASS]\033[0m"

            filename = os.path.basename(img_path)
            # Annotate and save visual result
            annotated_frame = results.plot()
            out_img_path = os.path.join(output_dir, f"inspected_{filename}")
            cv2.imwrite(out_img_path, annotated_frame)

            writer.writerow([time.strftime("%Y-%m-%d %H:%M:%S"), filename, verdict, num_defects, ";".join(defect_names), ";".join(confs)])

            print(f"{color_tag} Panel: {filename:<20} | Defect(s): {num_defects:<2} | Classes: {', '.join(defect_names) if defect_names else 'Flawless':<30} | {infer_time:.1f}ms")

    defect_rate = (total_rejected / total_inspected) * 100 if total_inspected > 0 else 0
    print("\n" + "=" * 60)
    print(f"📊 Final Inspection Summary:")
    print(f"   • Total Panels Checked:  {total_inspected}")
    print(f"   • Total Passed:          {total_inspected - total_rejected}")
    print(f"   • Total Rejected:        {total_rejected} ({defect_rate:.1f}% defect rate)")
    print(f"   • Annotated Visuals:     {output_dir}")
    print(f"   • Audit Log:             {output_csv}")
    print("=" * 60)

def main():
    parser = argparse.ArgumentParser(description="Run defect inspection on automotive panels.")
    parser.add_argument("--weights", type=str, default="weights/best.pt", help="Path to trained YOLO weights")
    parser.add_argument("--source", type=str, default="data/synthetic/images/val", help="Path to test images")
    parser.add_argument("--out", type=str, default="runs/inspection_results", help="Directory for visual output")
    parser.add_argument("--log", type=str, default="runs/inspection_log.csv", help="Inspection CSV log file")
    args = parser.parse_args()

    run_inspection(args.weights, args.source, args.out, args.log)

if __name__ == "__main__":
    main()
