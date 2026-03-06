#!/usr/bin/env python3
"""
Forward Watch Dataset Preparation
Merges Kaggle datasets into YOLOv8 training format.

Classes: 0=ship, 1=boat, 2=debris, 3=buoy, 4=kayak, 5=log
"""
import os
import shutil
import random
import xml.etree.ElementTree as ET

BASE = "/home/d3kos/kaggle-datasets"
OUT  = "/home/d3kos/forward-watch-dataset"

# Output folders
for split in ["train", "val"]:
    os.makedirs(f"{OUT}/images/{split}", exist_ok=True)
    os.makedirs(f"{OUT}/labels/{split}", exist_ok=True)

copied = 0
skipped = 0

# ── Helper: copy image + label, remapping class IDs ──────────────────────────
def copy_pair(img_path, lbl_path, class_remap, val_ratio=0.1):
    global copied, skipped
    if not os.path.exists(img_path) or not os.path.exists(lbl_path):
        skipped += 1
        return
    lines = open(lbl_path).read().strip().splitlines()
    if not lines:
        skipped += 1
        return
    new_lines = []
    for line in lines:
        parts = line.strip().split()
        if len(parts) < 5:
            continue
        cls = int(parts[0])
        new_cls = class_remap.get(cls)
        if new_cls is None:
            continue  # drop classes we don't care about
        new_lines.append(f"{new_cls} " + " ".join(parts[1:]))
    if not new_lines:
        skipped += 1
        return
    split = "val" if random.random() < val_ratio else "train"
    stem = os.path.splitext(os.path.basename(img_path))[0]
    ext  = os.path.splitext(img_path)[1]
    # Avoid name collisions
    dest_img = f"{OUT}/images/{split}/{stem}{ext}"
    dest_lbl = f"{OUT}/labels/{split}/{stem}.txt"
    n = 0
    while os.path.exists(dest_img):
        n += 1
        dest_img = f"{OUT}/images/{split}/{stem}_{n}{ext}"
        dest_lbl = f"{OUT}/labels/{split}/{stem}_{n}.txt"
    shutil.copy2(img_path, dest_img)
    open(dest_lbl, "w").write("\n".join(new_lines))
    copied += 1

# ── Helper: convert PASCAL VOC XML to YOLO ───────────────────────────────────
def xml_to_yolo(xml_path, img_path, out_class):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    size = root.find("size")
    if size is None:
        return None
    W = float(size.find("width").text)
    H = float(size.find("height").text)
    if W == 0 or H == 0:
        return None
    lines = []
    for obj in root.findall("object"):
        bb = obj.find("bndbox")
        if bb is None:
            continue
        xmin = float(bb.find("xmin").text)
        ymin = float(bb.find("ymin").text)
        xmax = float(bb.find("xmax").text)
        ymax = float(bb.find("ymax").text)
        cx = ((xmin + xmax) / 2) / W
        cy = ((ymin + ymax) / 2) / H
        w  = (xmax - xmin) / W
        h  = (ymax - ymin) / H
        lines.append(f"{out_class} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}")
    return lines if lines else None

# ── 1. yolov8-ship-detection v1-v7 (class 0 = ship) ─────────────────────────
print("Processing yolov8-ship-detection v1-v7...")
for v in ["v1", "v2", "v3", "v4", "v5", "v6", "v7"]:
    img_dir = f"{BASE}/yolov8-ship-detection/{v}/train/images"
    lbl_dir = f"{BASE}/yolov8-ship-detection/{v}/train/labels"
    val_img  = f"{BASE}/yolov8-ship-detection/{v}/valid/images"
    val_lbl  = f"{BASE}/yolov8-ship-detection/{v}/valid/labels"
    for src_img, src_lbl in [(img_dir, lbl_dir), (val_img, val_lbl)]:
        if not os.path.isdir(src_img):
            continue
        for fname in os.listdir(src_img):
            stem = os.path.splitext(fname)[0]
            copy_pair(
                f"{src_img}/{fname}",
                f"{src_lbl}/{stem}.txt",
                class_remap={0: 0}  # ship stays ship
            )
    print(f"  {v}: running total {copied} copied, {skipped} skipped")

# ── 2. uw-garbage-debris (class 0 = garbage → remap to 2 = debris) ──────────
print("Processing uw-garbage-debris...")
for split in ["train", "valid", "test"]:
    img_dir = f"{BASE}/uw-garbage-debris/Underwater_garbage/{split}/images"
    lbl_dir = f"{BASE}/uw-garbage-debris/Underwater_garbage/{split}/labels"
    if not os.path.isdir(img_dir):
        continue
    for fname in os.listdir(img_dir):
        stem = os.path.splitext(fname)[0]
        copy_pair(
            f"{img_dir}/{fname}",
            f"{lbl_dir}/{stem}.txt",
            class_remap={0: 2}  # garbage → debris
        )
print(f"  running total {copied} copied, {skipped} skipped")

# ── 3. ship-detection-aerial (XML → YOLO, class 1 = boat) ───────────────────
print("Processing ship-detection-aerial...")
ann_dir = f"{BASE}/ship-detection-aerial/annotations"
img_dir = f"{BASE}/ship-detection-aerial/images"
for xml_file in os.listdir(ann_dir):
    if not xml_file.endswith(".xml"):
        continue
    stem = os.path.splitext(xml_file)[0]
    # Find matching image
    img_path = None
    for ext in [".png", ".jpg", ".jpeg"]:
        candidate = f"{img_dir}/{stem}{ext}"
        if os.path.exists(candidate):
            img_path = candidate
            break
    if img_path is None:
        skipped += 1
        continue
    lines = xml_to_yolo(f"{ann_dir}/{xml_file}", img_path, out_class=1)
    if not lines:
        skipped += 1
        continue
    split = "val" if random.random() < 0.1 else "train"
    dest_img = f"{OUT}/images/{split}/{stem}.png"
    dest_lbl = f"{OUT}/labels/{split}/{stem}.txt"
    shutil.copy2(img_path, dest_img)
    open(dest_lbl, "w").write("\n".join(lines))
    copied += 1
print(f"  running total {copied} copied, {skipped} skipped")

# ── Write data.yaml ───────────────────────────────────────────────────────────
train_count = len(os.listdir(f"{OUT}/images/train"))
val_count   = len(os.listdir(f"{OUT}/images/val"))

yaml = f"""path: {OUT}
train: images/train
val: images/val

nc: 6
names:
  0: ship
  1: boat
  2: debris
  3: buoy
  4: kayak
  5: log
"""
open(f"{OUT}/data.yaml", "w").write(yaml)

print()
print("=" * 50)
print("DATASET READY")
print("=" * 50)
print(f"Train images : {train_count}")
print(f"Val images   : {val_count}")
print(f"Total copied : {copied}")
print(f"Skipped      : {skipped}")
print(f"data.yaml    : {OUT}/data.yaml")
print("=" * 50)
