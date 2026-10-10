#!/usr/bin/env python3
"""
RangRakshak - Train Paint Defect Detector using Ultralytics YOLOv11.
Optimized for H200 GPU with mixed precision (fp16) and direct export to ONNX & TensorRT.
"""

import os
import argparse
import yaml
from pathlib import Path

def train_model(data_yaml, model_name="yolo11n.pt", epochs=30, batch_size=32, imgsz=640):
    try:
        from ultralytics import YOLO
    except ImportError:
        print("❌ Error: ultralytics is not installed. Run: pip install ultralytics")
        return

    print("=" * 60)
    print("🎨 RangRakshak: Initiating H200 Paint Defect Detector Training")
    print("=" * 60)
    print(f"📦 Base Model: {model_name}")
    print(f"📄 Data Config: {data_yaml}")
    print(f"⚡ Epochs: {epochs} | Batch: {batch_size} | Size: {imgsz}")
    
    # Load model
    model = YOLO(model_name)
    
    # Train model
    results = model.train(
        data=data_yaml,
        epochs=epochs,
        batch=batch_size,
        imgsz=imgsz,
        half=True,       # Mixed precision fp16 on H200
        device="0",      # H200 GPU
        project="runs/paint_defect",
        name="rangrakshak_model",
        exist_ok=True,
        plots=True,
        save=True
    )
    
    print("\n" + "=" * 60)
    print("✅ Training Complete! Validating on Held-Out Synthetic Test Set...")
    print("=" * 60)
    metrics = model.val()
    print(f"🎯 Validation mAP50-95: {metrics.box.map:.4f}")
    print(f"🎯 Validation mAP50:    {metrics.box.map50:.4f}")
    
    # Export weights for deployment
    weights_path = Path("runs/paint_defect/rangrakshak_model/weights/best.pt")
    if weights_path.exists():
        os.makedirs("weights", exist_ok=True)
        import shutil
        shutil.copy(weights_path, "weights/best.pt")
        print(f"💾 Copied best weights to: weights/best.pt")
        
        # Export to ONNX (universal deployment)
        print("🚀 Exporting model to ONNX...")
        try:
            model.export(format="onnx", half=True)
            print("✅ ONNX export complete.")
        except Exception as e:
            print(f"⚠️ ONNX export warning: {e}")
            
        # Export to TensorRT engine (for Jetson edge)
        print("⚡ Exporting model to TensorRT engine (Jetson/GPU)...")
        try:
            model.export(format="engine", half=True, device="0")
            print("✅ TensorRT export complete.")
        except Exception as e:
            print(f"⚠️ TensorRT export warning (requires tensorrt python package): {e}")

    print("\n🎉 RangRakshak detector is ready for real-time inspection!")

def main():
    parser = argparse.ArgumentParser(description="Train paint defect detector.")
    parser.add_argument("--data", type=str, default="data/synthetic/data.yaml", help="Path to data.yaml")
    parser.add_argument("--model", type=str, default="yolo11n.pt", help="Base model (yolo11n.pt, yolo11s.pt, yolo11x.pt)")
    parser.add_argument("--epochs", type=int, default=30, help="Number of training epochs")
    parser.add_argument("--batch", type=int, default=32, help="Batch size (optimized for H200)")
    parser.add_argument("--imgsz", type=int, default=640, help="Input image size")
    args = parser.parse_args()

    train_model(
        data_yaml=os.path.abspath(args.data),
        model_name=args.model,
        epochs=args.epochs,
        batch_size=args.batch,
        imgsz=args.imgsz
    )

if __name__ == "__main__":
    main()
