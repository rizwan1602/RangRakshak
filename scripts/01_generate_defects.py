#!/usr/bin/env python3
"""
RangRakshak - Synthetic Paint Defect Data Generator
Generates realistic automotive surface defect images and YOLO annotations.
Supports Replicator procedural generation and standalone high-speed OpenCV synthesis.
"""

import os
import random
import argparse
import yaml
import numpy as np
import cv2
from tqdm import tqdm

CLASSES = [
    "scratch",
    "orange_peel",
    "fish_eye",
    "dust_nib",
    "run_sag",
    "color_mismatch",
    "blister",
    "pinhole"
]

BASE_COLORS = [
    (180, 20, 20),    # Automotive Red (BGR)
    (20, 40, 180),    # Deep Blue (BGR)
    (220, 220, 225),  # Pearl White (BGR)
    (25, 25, 28),     # Obsidian Black (BGR)
    (170, 175, 180),  # Metallic Silver (BGR)
]

def create_base_panel(width=640, height=640):
    """Creates a realistic automotive painted metal panel with gradient lighting and metallic grain."""
    base_color = random.choice(BASE_COLORS)
    img = np.zeros((height, width, 3), dtype=np.float32)
    
    # Lighting gradient across panel
    y_grad = np.linspace(0.85, 1.15, height)[:, None]
    x_grad = np.linspace(0.90, 1.10, width)[None, :]
    lighting = y_grad * x_grad
    
    for c in range(3):
        img[:, :, c] = base_color[c] * lighting
        
    # Metallic specular flake noise
    noise = np.random.normal(0, 3.5, (height, width, 3))
    img = np.clip(img + noise, 0, 255).astype(np.uint8)
    return img

def inject_scratch(img, width=640, height=640):
    x1, y1 = random.randint(50, width - 100), random.randint(50, height - 100)
    length = random.randint(40, 160)
    angle = random.uniform(0, 2 * np.pi)
    x2 = int(np.clip(x1 + length * np.cos(angle), 10, width - 10))
    y2 = int(np.clip(y1 + length * np.sin(angle), 10, height - 10))
    
    thickness = random.randint(1, 3)
    scratch_color = (240, 240, 245) if np.mean(img[y1, x1]) < 128 else (40, 40, 45)
    cv2.line(img, (x1, y1), (x2, y2), scratch_color, thickness, cv2.LINE_AA)
    
    xmin, xmax = min(x1, x2) - 5, max(x1, x2) + 5
    ymin, ymax = min(y1, y2) - 5, max(y1, y2) + 5
    return 0, max(0, xmin), max(0, ymin), min(width, xmax), min(height, ymax)

def inject_orange_peel(img, width=640, height=640):
    bw, bh = random.randint(80, 180), random.randint(80, 180)
    bx = random.randint(20, width - bw - 20)
    by = random.randint(20, height - bh - 20)
    
    patch = img[by:by+bh, bx:bx+bw].astype(np.float32)
    # High frequency wavy texture
    wavy = np.sin(np.linspace(0, 15, bh))[:, None] * np.cos(np.linspace(0, 15, bw))[None, :] * 12.0
    for c in range(3):
        patch[:, :, c] += wavy
    img[by:by+bh, bx:bx+bw] = np.clip(patch, 0, 255).astype(np.uint8)
    return 1, bx, by, bx + bw, by + bh

def inject_fish_eye(img, width=640, height=640):
    cx = random.randint(60, width - 60)
    cy = random.randint(60, height - 60)
    radius = random.randint(12, 35)
    
    # Outer pale ring
    cv2.circle(img, (cx, cy), radius, (230, 230, 235), 2, cv2.LINE_AA)
    # Darker recessed core
    cv2.circle(img, (cx, cy), radius - 3, (30, 30, 35), -1, cv2.LINE_AA)
    return 2, cx - radius - 4, cy - radius - 4, cx + radius + 4, cy + radius + 4

def inject_dust_nib(img, width=640, height=640):
    cx = random.randint(40, width - 40)
    cy = random.randint(40, height - 40)
    radius = random.randint(3, 8)
    # Tiny raised bump with highlight and micro shadow
    cv2.circle(img, (cx + 1, cy + 1), radius, (20, 20, 20), -1, cv2.LINE_AA)
    cv2.circle(img, (cx, cy), radius, (250, 250, 250), -1, cv2.LINE_AA)
    return 3, cx - radius - 4, cy - radius - 4, cx + radius + 4, cy + radius + 4

def inject_run_sag(img, width=640, height=640):
    sx = random.randint(80, width - 80)
    sy = random.randint(50, height - 160)
    length = random.randint(60, 140)
    w = random.randint(10, 22)
    
    color = [int(c * 0.7) for c in img[sy, sx]]
    cv2.ellipse(img, (sx, sy + length // 2), (w // 2, length // 2), 0, 0, 360, color, -1)
    cv2.circle(img, (sx, sy + length), int(w * 0.75), color, -1)
    return 4, sx - w, sy, sx + w, sy + length + w

def inject_color_mismatch(img, width=640, height=640):
    bw, bh = random.randint(100, 220), random.randint(100, 220)
    bx = random.randint(20, width - bw - 20)
    by = random.randint(20, height - bh - 20)
    patch = img[by:by+bh, bx:bx+bw].astype(np.float32)
    patch[:, :, 0] = np.clip(patch[:, :, 0] * 1.25, 0, 255)
    img[by:by+bh, bx:bx+bw] = patch.astype(np.uint8)
    return 5, bx, by, bx + bw, by + bh

def inject_blister(img, width=640, height=640):
    cx = random.randint(60, width - 60)
    cy = random.randint(60, height - 60)
    r = random.randint(15, 30)
    cv2.circle(img, (cx, cy), r, (190, 190, 200), -1, cv2.LINE_AA)
    cv2.ellipse(img, (cx - r//3, cy - r//3), (r//3, r//5), 45, 0, 360, (255, 255, 255), -1)
    return 6, cx - r - 3, cy - r - 3, cx + r + 3, cy + r + 3

def inject_pinhole(img, width=640, height=640):
    cx = random.randint(40, width - 40)
    cy = random.randint(40, height - 40)
    r = random.randint(2, 5)
    cv2.circle(img, (cx, cy), r, (10, 10, 10), -1)
    return 7, cx - r - 2, cy - r - 2, cx + r + 2, cy + r + 2

DEFECT_FUNCS = [
    inject_scratch,
    inject_orange_peel,
    inject_fish_eye,
    inject_dust_nib,
    inject_run_sag,
    inject_color_mismatch,
    inject_blister,
    inject_pinhole,
]

def to_yolo_bbox(xmin, ymin, xmax, ymax, w=640, h=640):
    xc = (xmin + xmax) / (2.0 * w)
    yc = (ymin + ymax) / (2.0 * h)
    bw = (xmax - xmin) / float(w)
    bh = (ymax - ymin) / float(h)
    return f"{xc:.6f} {yc:.6f} {bw:.6f} {bh:.6f}"

def main():
    parser = argparse.ArgumentParser(description="Generate synthetic paint defect dataset.")
    parser.add_argument("--config", type=str, default="configs/dig_config.yaml", help="Path to config")
    parser.add_argument("--samples", type=int, default=1200, help="Total synthetic samples to generate")
    parser.add_argument("--out_dir", type=str, default="data/synthetic", help="Output directory")
    args = parser.parse_args()

    out_dir = os.path.abspath(args.out_dir)
    for split in ["train", "val"]:
        os.makedirs(os.path.join(out_dir, "images", split), exist_ok=True)
        os.makedirs(os.path.join(out_dir, "labels", split), exist_ok=True)

    print(f"🎨 Generating {args.samples} synthetic automotive paint defect images...")
    
    val_count = int(args.samples * 0.2)
    train_count = args.samples - val_count

    splits = [("train", train_count), ("val", val_count)]
    
    img_idx = 0
    for split, count in splits:
        for _ in tqdm(range(count), desc=f"Generating {split} set"):
            img = create_base_panel(640, 640)
            
            # Inject 1 to 3 defects per panel
            num_defects = random.choices([1, 2, 3], weights=[0.6, 0.3, 0.1])[0]
            labels = []
            
            for _ in range(num_defects):
                defect_fn = random.choice(DEFECT_FUNCS)
                cls_id, x1, y1, x2, y2 = defect_fn(img, 640, 640)
                yolo_box = to_yolo_bbox(x1, y1, x2, y2, 640, 640)
                labels.append(f"{cls_id} {yolo_box}")
                
            img_filename = f"defect_syn_{img_idx:06d}.jpg"
            lbl_filename = f"defect_syn_{img_idx:06d}.txt"
            
            img_path = os.path.join(out_dir, "images", split, img_filename)
            lbl_path = os.path.join(out_dir, "labels", split, lbl_filename)
            
            cv2.imwrite(img_path, img, [cv2.IMWRITE_JPEG_QUALITY, 95])
            with open(lbl_path, "w") as f:
                f.write("\n".join(labels))
                
            img_idx += 1

    # Write data.yaml for YOLOv11
    yaml_content = {
        "path": out_dir,
        "train": "images/train",
        "val": "images/val",
        "nc": len(CLASSES),
        "names": {i: name for i, name in enumerate(CLASSES)}
    }
    yaml_path = os.path.join(out_dir, "data.yaml")
    with open(yaml_path, "w") as f:
        yaml.dump(yaml_content, f, default_flow_style=False)

    print(f"\n✅ Dataset generated successfully!")
    print(f"📁 Dataset path: {out_dir}")
    print(f"📄 YOLO data file: {yaml_path}")
    print(f"📊 Training samples: {train_count} | Validation samples: {val_count}")

if __name__ == "__main__":
    main()
