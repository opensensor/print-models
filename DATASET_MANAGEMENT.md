# Dataset Management with Git LFS

## Problem

Currently, `printer-timelapses/` is a symlink to your camera's storage, which means:
- Training datasets are not version controlled
- Models cannot be reproduced from the repository alone
- No historical record of which images were used to train which model version
- Collaboration is difficult (others can't access your camera's storage)

## Solution: Git LFS for Training Datasets

Use Git Large File Storage (LFS) to version control the labeled training images while keeping the repository size manageable.

## Proposed Directory Structure

```
print-models/
├── data/
│   ├── labels.json                    # Offline vs Active labels (version controlled)
│   ├── failed_print_labels.json       # Good vs Failed labels (version controlled)
│   └── monitor_state.json             # Monitor state (gitignored)
├── datasets/                          # NEW: Training datasets (Git LFS)
│   ├── offline-detection/
│   │   ├── v1/                        # First training set (150 images)
│   │   │   ├── active/
│   │   │   │   ├── 20251107T005601.jpg
│   │   │   │   ├── 20251110T000537.jpg
│   │   │   │   └── ... (60 images)
│   │   │   ├── offline/
│   │   │   │   ├── 20251109T152426.jpg
│   │   │   │   ├── 20251108T032702.jpg
│   │   │   │   └── ... (90 images)
│   │   │   ├── labels.json            # Copy of labels for this version
│   │   │   └── README.md              # Dataset metadata
│   │   └── v2/                        # After corrections (151 images)
│   │       ├── active/
│   │       ├── offline/
│   │       ├── labels.json
│   │       └── README.md
│   └── failed-print-detection/
│       └── v1/                        # First failed print dataset (196 images)
│           ├── good/
│           ├── failed/
│           ├── labels.json
│           └── README.md
├── models/                            # Model checkpoints (Git LFS)
│   ├── printer_offline_detector.pth   # Current best model
│   ├── failed_print_detector.pth      # Current best model
│   └── versions/                      # NEW: Versioned models
│       ├── offline-detector-v1.pth    # Trained on datasets/offline-detection/v1
│       ├── offline-detector-v2.pth    # Trained on datasets/offline-detection/v2
│       └── failed-detector-v1.pth     # Trained on datasets/failed-print-detection/v1
├── printer-timelapses/                # Symlink to camera (gitignored)
└── .gitattributes                     # Git LFS configuration
```

## Setup Instructions

### 1. Install Git LFS

```bash
# Ubuntu/Debian
sudo apt-get install git-lfs

# Initialize Git LFS in your repository
git lfs install
```

### 2. Configure Git LFS

```bash
# Track image files with LFS
git lfs track "datasets/**/*.jpg"
git lfs track "datasets/**/*.png"
git lfs track "models/versions/*.pth"

# This creates/updates .gitattributes
git add .gitattributes
git commit -m "Configure Git LFS for datasets and model versions"
```

### 3. Create Dataset Structure

```bash
# Create directories
mkdir -p datasets/offline-detection/v1/{active,offline}
mkdir -p datasets/failed-print-detection/v1/{good,failed}
mkdir -p models/versions
```

### 4. Copy Training Images

We'll create a script to copy labeled images from `printer-timelapses/` to `datasets/`:

```bash
# Script: scripts/export_dataset.py
python scripts/export_dataset.py \
    --labels data/labels.json \
    --output datasets/offline-detection/v1 \
    --version "1.0" \
    --description "Initial training set: 60 active, 90 offline"
```

### 5. Update .gitignore

```gitignore
# Existing
venv/
__pycache__/
*.pyc
data/monitor_state.json
data/predictions.json
data/active_candidates.txt
data/active_images.txt

# Camera symlink - don't track live camera data
printer-timelapses/

# Keep datasets/ tracked (managed by Git LFS)
# Keep models/versions/ tracked (managed by Git LFS)
```

## Benefits

### 1. **Reproducibility**
- Anyone can clone the repo and get the exact training data
- Models can be retrained from scratch with identical results
- Clear lineage: model version → dataset version → images

### 2. **Version Control**
- Track how datasets evolve over time
- See which corrections were made between versions
- Roll back to previous datasets if needed

### 3. **Collaboration**
- Share datasets with team members
- Others can contribute labeled images
- Consistent training across different machines

### 4. **Documentation**
- Each dataset version has a README with metadata:
  - Date created
  - Number of images per class
  - Model performance on this dataset
  - Notes about data collection

### 5. **Efficient Storage**
- Git LFS stores large files on remote server
- Local clone only downloads files you need
- Deduplication across versions

## Dataset Metadata Example

Each dataset version should have a `README.md`:

```markdown
# Offline Detection Dataset v1

**Created:** 2025-11-10
**Total Images:** 150
**Classes:**
- Active: 60 (40%)
- Offline: 90 (60%)

## Model Performance

Trained with this dataset:
- Model: ResNet18 transfer learning
- Validation Accuracy: 96.67%
- Training Date: 2025-11-10
- Model File: `models/versions/offline-detector-v1.pth`

## Data Collection

- Source: Printer timelapses from 2025-11-07 to 2025-11-10
- Labeling: Manual labeling using `src/label_images.py`
- Active sequences identified using frame-to-frame difference analysis

## Notes

- Initial dataset with class imbalance (1.5:1 ratio)
- Active images concentrated in 3 printing sequences
- Some edge cases with printer warming up not included
```

## Migration Plan

### Phase 1: Export Current Dataset (v1)
1. Create export script
2. Copy 150 labeled images to `datasets/offline-detection/v1/`
3. Copy 196 failed print images to `datasets/failed-print-detection/v1/`
4. Generate README files with metadata
5. Commit to Git LFS

### Phase 2: Version Current Models
1. Copy current models to `models/versions/`
2. Rename with version numbers
3. Link to dataset versions in documentation

### Phase 3: Update Training Scripts
1. Modify `src/train_model.py` to accept `--dataset-dir` parameter
2. Default to `datasets/offline-detection/v1/` for reproducibility
3. Keep ability to train on `data/labels.json` for active development

### Phase 4: Future Workflow
1. Active development: Use `data/labels.json` + symlinked `printer-timelapses/`
2. When ready to release: Export to new dataset version (v2, v3, etc.)
3. Train versioned model on versioned dataset
4. Commit both to repository

## Storage Considerations

### GitHub LFS Limits
- Free: 1 GB storage, 1 GB/month bandwidth
- Pro: 50 GB storage, 50 GB/month bandwidth

### Estimated Sizes
- 150 JPG images @ ~300 KB each = ~45 MB (offline detection v1)
- 196 JPG images @ ~300 KB each = ~59 MB (failed print detection v1)
- Model checkpoint @ ~45 MB each
- **Total for v1:** ~150 MB

### Recommendations
1. Start with current datasets (v1) - well within free tier
2. Only commit "release" versions, not every correction
3. Consider self-hosted LFS if datasets grow large
4. Alternative: Use DVC (Data Version Control) for very large datasets

## Alternative: DVC (Data Version Control)

If Git LFS becomes too expensive, consider DVC:
- Designed specifically for ML datasets
- Works with any cloud storage (S3, Google Cloud, etc.)
- Better for very large datasets (GBs to TBs)
- Similar workflow to Git LFS

## Next Steps

Would you like me to:
1. Create the export script to copy labeled images to `datasets/`?
2. Set up Git LFS configuration?
3. Generate dataset README files with metadata?
4. Update training scripts to support versioned datasets?

