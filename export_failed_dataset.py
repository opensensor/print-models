#!/usr/bin/env python3
import json
import shutil
from pathlib import Path
from collections import Counter

# Load labels
print("Loading labels...")
with open('data/failed_print_labels.json', 'r') as f:
    labels = json.load(f)

print(f"Loaded {len(labels)} labels")

# Create directories
output_path = Path('datasets/failed-print-detection/v1')
output_path.mkdir(parents=True, exist_ok=True)
(output_path / 'good').mkdir(exist_ok=True)
(output_path / 'failed').mkdir(exist_ok=True)

print(f"Created directories at {output_path}")

# Copy images
copied = 0
skipped = 0
class_counts = Counter()

for img_path_str, label in labels.items():
    img_path = Path(img_path_str)
    if not img_path.exists():
        print(f"Skipping {img_path} (not found)")
        skipped += 1
        continue
    
    dest_dir = output_path / label
    dest_path = dest_dir / img_path.name
    shutil.copy2(img_path, dest_path)
    copied += 1
    class_counts[label] += 1

print(f"\nCopied {copied} images, skipped {skipped}")
print(f"Good: {class_counts['good']}")
print(f"Failed: {class_counts['failed']}")

# Save labels.json
labels_output = output_path / "labels.json"
with open(labels_output, 'w') as f:
    json.dump(labels, f, indent=2)
print(f"Saved labels to {labels_output}")

# Save dataset_info.json
dataset_info = {
    "version": "1.0",
    "description": "Initial failed print dataset: 175 good, 21 failed",
    "created": "2025-11-12",
    "total_images": copied,
    "classes": dict(class_counts),
    "dataset_type": "failed-print-detection",
    "source_labels": "data/failed_print_labels.json"
}
info_path = output_path / "dataset_info.json"
with open(info_path, 'w') as f:
    json.dump(dataset_info, f, indent=2)
print(f"Saved dataset info to {info_path}")

print("\n✓ Export complete!")

