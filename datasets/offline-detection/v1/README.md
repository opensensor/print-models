# Offline Detection Dataset v1.0

**Created:** 2025-11-12
**Total Images:** 169
**Description:** Initial training set: 60 active, 90 offline

## Classes

- **Active:** 79 images (46.7%)
- **Offline:** 90 images (53.3%)


## Directory Structure

```
README.md/
├── active/          # 79 images
├── offline/          # 90 images
├── labels.json       # Original labels file
├── dataset_info.json # Dataset metadata
└── README.md         # This file
```

## Source

- **Labels File:** `data/labels.json`
- **Images:** Copied from printer timelapse storage

## Usage

### Training with this dataset

```python
# Load dataset
from pathlib import Path
import json

dataset_dir = Path("README.md")
with open(dataset_dir / "dataset_info.json") as f:
    info = json.load(f)

print(f"Dataset version: {info['version']}")
print(f"Total images: {info['total_images']}")
print(f"Classes: {info['classes']}")
```

### Training script

```bash
# Train model on this specific dataset version
python src/train_model.py \
    --dataset-dir datasets/offline-detection/v1/README.md \
    --epochs 20 \
    --batch-size 32
```

## Model Performance

*To be filled in after training*

- **Model:** ResNet18 transfer learning
- **Validation Accuracy:** TBD
- **Training Date:** TBD
- **Model File:** `models/versions/offline_detection_v1.0.pth`

## Notes

- Images are stored in class subdirectories for easy loading with PyTorch ImageFolder
- Original labels.json preserved for reference
- All images are 1920x1080 JPEG format from printer timelapse camera

## Version History

### v1.0 (2025-11-12)
- Initial training set: 60 active, 90 offline
