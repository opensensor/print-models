# Git LFS Quick Start Guide

## Why Git LFS for This Project?

Currently, `printer-timelapses/` is a symlink to your camera storage. This means:
- ❌ Training datasets are not in version control
- ❌ Models can't be reproduced from the repo alone
- ❌ No record of which images trained which model
- ❌ Collaboration is difficult

**Solution:** Use Git LFS to version control your labeled training images and model checkpoints.

## Quick Setup (5 minutes)

### Step 1: Install Git LFS

```bash
# Ubuntu/Debian
sudo apt-get install git-lfs

# Verify installation
git lfs version
```

### Step 2: Run Setup Script

```bash
# This configures Git LFS and creates directory structure
./scripts/setup_git_lfs.sh
```

This will:
- Initialize Git LFS in your repo
- Configure tracking for `*.jpg`, `*.png`, `*.pth` files in `datasets/` and `models/versions/`
- Create directory structure
- Update `.gitignore`

### Step 3: Export Current Datasets

```bash
# Export offline detection dataset (v1)
python scripts/export_dataset.py \
    --labels-file data/labels.json \
    --output-dir datasets/offline-detection/v1 \
    --version "1.0" \
    --description "Initial training set: 60 active, 90 offline" \
    --dataset-type offline-detection

# Export failed print detection dataset (v1)
python scripts/export_dataset.py \
    --labels-file data/failed_print_labels.json \
    --output-dir datasets/failed-print-detection/v1 \
    --version "1.0" \
    --description "Initial failed print dataset: 175 good, 21 failed" \
    --dataset-type failed-print-detection
```

### Step 4: Version Current Models

```bash
# Copy current best models to versions directory
cp models/printer_offline_detector.pth models/versions/offline_detector_v1.pth
cp models/failed_print_detector.pth models/versions/failed_detector_v1.pth
cp models/training_history.png models/versions/offline_detector_v1_history.png
cp models/failed_print_detector_history.png models/versions/failed_detector_v1_history.png
```

### Step 5: Commit and Push

```bash
# Stage all new files
git add .gitattributes datasets/ models/versions/ scripts/

# Commit
git commit -m "Add versioned datasets and models with Git LFS

- Add offline detection dataset v1 (150 images)
- Add failed print detection dataset v1 (196 images)
- Add model checkpoints v1
- Configure Git LFS for large files"

# Push (LFS files will be uploaded to LFS storage)
git push
```

## What Gets Tracked Where?

### Git LFS (Large Files)
- `datasets/**/*.jpg` - Training images
- `datasets/**/*.png` - Training images
- `models/versions/*.pth` - Model checkpoints
- `models/versions/*.png` - Training history plots

### Regular Git (Small Files)
- `data/labels.json` - Label mappings
- `data/failed_print_labels.json` - Failed print labels
- `datasets/**/README.md` - Dataset documentation
- `datasets/**/dataset_info.json` - Dataset metadata
- `src/*.py` - Source code
- `*.md` - Documentation

### Gitignored (Not Tracked)
- `printer-timelapses/` - Symlink to camera (too large, always changing)
- `data/monitor_state.json` - Transient monitor state
- `venv/` - Python virtual environment
- `__pycache__/` - Python cache files

## Directory Structure After Setup

```
print-models/
├── datasets/                          # NEW: Versioned training datasets (Git LFS)
│   ├── offline-detection/
│   │   └── v1/
│   │       ├── active/                # 60 images
│   │       ├── offline/               # 90 images
│   │       ├── labels.json
│   │       ├── dataset_info.json
│   │       └── README.md
│   └── failed-print-detection/
│       └── v1/
│           ├── good/                  # 175 images
│           ├── failed/                # 21 images
│           ├── labels.json
│           ├── dataset_info.json
│           └── README.md
├── models/
│   ├── printer_offline_detector.pth   # Current best (symlink or copy)
│   ├── failed_print_detector.pth      # Current best (symlink or copy)
│   └── versions/                      # NEW: Versioned models (Git LFS)
│       ├── offline_detector_v1.pth
│       ├── offline_detector_v1_history.png
│       ├── failed_detector_v1.pth
│       └── failed_detector_v1_history.png
├── scripts/                           # NEW: Utility scripts
│   ├── setup_git_lfs.sh
│   └── export_dataset.py
└── printer-timelapses/                # Symlink (gitignored)
```

## Workflow: Making Corrections and Creating v2

When you correct labels and want to create a new dataset version:

```bash
# 1. Make corrections using the GUI tool
make correct-retrain DATE=20251111 TIME=08:54-09:25

# 2. Export new dataset version
python scripts/export_dataset.py \
    --labels-file data/labels.json \
    --output-dir datasets/offline-detection/v2 \
    --version "2.0" \
    --description "Added corrections for false offline detections (151 images: 61 active, 90 offline)" \
    --dataset-type offline-detection

# 3. Train model on new dataset
python src/train_model.py --epochs 20 --batch-size 32

# 4. Save new model version
cp models/printer_offline_detector.pth models/versions/offline_detector_v2.pth
cp models/training_history.png models/versions/offline_detector_v2_history.png

# 5. Update README in datasets/offline-detection/v2/README.md with model performance

# 6. Commit
git add datasets/offline-detection/v2/ models/versions/offline_detector_v2.*
git commit -m "Add dataset v2 with corrections and retrained model"
git push
```

## Benefits

### ✅ Reproducibility
Anyone can clone your repo and get the exact training data used for each model version.

```bash
# Clone repo
git clone https://github.com/opensensor/print-models.git
cd print-models

# LFS files are automatically downloaded
# Train model from scratch with exact same data
python src/train_model.py --dataset-dir datasets/offline-detection/v1
```

### ✅ Version Control
Track how your dataset evolves:

```bash
# See all dataset versions
ls datasets/offline-detection/
# v1/  v2/  v3/

# Compare versions
diff datasets/offline-detection/v1/labels.json datasets/offline-detection/v2/labels.json
```

### ✅ Model Lineage
Clear connection between datasets and models:

```
offline_detector_v1.pth ← trained on ← datasets/offline-detection/v1/
offline_detector_v2.pth ← trained on ← datasets/offline-detection/v2/
```

### ✅ Collaboration
Share datasets with team members or the community.

## Storage Costs

### GitHub Free Tier
- **Storage:** 1 GB
- **Bandwidth:** 1 GB/month
- **Cost:** Free

### Your Current Usage (Estimated)
- Offline detection v1: ~45 MB (150 images)
- Failed print detection v1: ~59 MB (196 images)
- Model checkpoints: ~90 MB (2 models)
- **Total:** ~194 MB

**Verdict:** Well within free tier! You can store ~5 dataset versions before hitting limits.

### If You Need More
- **GitHub Pro:** $4/month → 50 GB storage, 50 GB/month bandwidth
- **Self-hosted LFS:** Free, unlimited (requires server)
- **DVC (Data Version Control):** Free, works with any cloud storage

## Checking LFS Status

```bash
# See which files are tracked by LFS
git lfs ls-files

# See LFS storage usage
git lfs status

# See what will be uploaded
git lfs push --dry-run origin main
```

## Troubleshooting

### "git-lfs not found"
```bash
sudo apt-get install git-lfs
git lfs install
```

### "This exceeds GitHub's file size limit"
Make sure files are tracked by LFS before committing:
```bash
git lfs track "datasets/**/*.jpg"
git add .gitattributes
git add datasets/
```

### "Bandwidth limit exceeded"
- Wait until next month (resets monthly)
- Upgrade to GitHub Pro
- Use `git lfs fetch --exclude="datasets/"` to skip large files when cloning

## Next Steps

1. **Run the setup:** `./scripts/setup_git_lfs.sh`
2. **Export datasets:** Use `scripts/export_dataset.py`
3. **Commit and push:** Share your versioned datasets
4. **Update documentation:** Add model performance to dataset READMEs

## Questions?

See `DATASET_MANAGEMENT.md` for detailed information about:
- Directory structure rationale
- Dataset metadata format
- Alternative solutions (DVC)
- Migration plan

