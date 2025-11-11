# Print Models - 3D Printer Activity Detection

This project develops machine learning models to analyze 3D printer timelapse images, starting with a "printer-offline" detector to filter out images with no printer activity.

## 🎯 Goal

Filter 4,800+ timelapse images to identify only those with active printing, enabling focused analysis of print quality and failure detection.

## 📊 Current Dataset

- **4,822 images** across 4 days (Nov 7-10, 2025)
- 1920x1080 JPEG format
- ~297 KB average file size
- Most images show printer offline (idle time)

## 🚀 Quick Start

```bash
# 1. Setup (one time)
make setup

# 2. Check status
make status

# 3. Explore your data
make explore

# 4. Label training data (interactive GUI)
make label

# 5. Train the model
make train

# 6. Run inference on all images
make inference-org

# 7. Analyze results
make analyze
```

See `QUICKSTART.md` for detailed instructions.

## 📁 Project Structure

```
print-models/
├── src/                    # Source code
│   ├── explore_images.py   # Data exploration
│   ├── label_images.py     # Interactive labeling tool
│   ├── train_model.py      # Model training
│   ├── inference.py        # Batch prediction
│   └── analyze_results.py  # Results analysis
├── data/                   # Generated data
│   ├── labels.json         # Your labeled training data
│   ├── predictions.json    # Model predictions
│   └── organized/          # Images sorted by prediction
├── models/                 # Trained models
│   └── printer_offline_detector.pth
├── printer-timelapses/     # Symlink to your images
├── requirements.txt        # Python dependencies
├── Makefile               # Command shortcuts
├── workflow.sh            # Workflow automation
├── QUICKSTART.md          # Detailed guide
└── PROJECT_SUMMARY.md     # Complete documentation
```

## 🔄 Workflow

```
┌─────────────────┐
│  Raw Images     │  4,822 timelapse images
│  (Symlinked)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  1. Explore     │  Visualize & understand data
│  make explore   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  2. Label       │  Manually label 100-200 images
│  make label     │  (offline vs active)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  3. Train       │  Train ResNet18 model
│  make train     │  Expected: 85-95% accuracy
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  4. Inference   │  Classify all 4,822 images
│  make inference │  Organize by prediction
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  5. Analyze     │  Review results & iterate
│  make analyze   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Filtered Data  │  Only active printing images
│  Next: Failed   │  Ready for failure detection
│  Print Model    │
└─────────────────┘
```

## 🛠️ Available Commands

Run `make help` to see all commands, or use these common ones:

**Setup & Exploration:**
- `make setup` - Install dependencies
- `make explore` - Show dataset statistics
- `make status` - Check project status

**Labeling:**
- `make label` - Label 100 images (interactive)
- `make label-50` - Label 50 images
- `make label-200` - Label 200 images

**Training:**
- `make train` - Train model (20 epochs)
- `make train-quick` - Quick training (10 epochs)
- `make train-long` - Extended training (30 epochs)

**Inference:**
- `make inference` - Run predictions
- `make inference-org` - Run predictions & organize images

**Analysis:**
- `make analyze` - Full analysis
- `make analyze-conf` - Plot confidence distribution
- `make analyze-uncertain` - Find uncertain predictions

## 🎓 How It Works

1. **Transfer Learning**: Uses pre-trained ResNet18 model
2. **Binary Classification**: Offline (0) vs Active (1)
3. **Data Augmentation**: Improves generalization
4. **Confidence Scores**: Identifies uncertain predictions
5. **Iterative Improvement**: Label uncertain cases, retrain

## 📈 Expected Results

- **Training Time**: 5-15 min (GPU) or 30-60 min (CPU)
- **Accuracy**: 85-95% with 100+ labeled examples
- **Inference Speed**: ~1-2 images/sec (CPU), ~10-20 images/sec (GPU)
- **Filtered Dataset**: Expect 10-30% active images (varies by usage)

## 🔧 Requirements

- Python 3.8+
- 4GB+ RAM
- Optional: NVIDIA GPU for faster training

## 📚 Documentation

- **QUICKSTART.md** - Step-by-step tutorial
- **PROJECT_SUMMARY.md** - Complete technical documentation
- **Makefile** - Command reference (run `make help`)

## 🎯 Next Steps

After filtering offline images:

1. **Failed Print Detection** - Classify active images as good/failed
2. **Temporal Analysis** - Track print sessions over time
3. **Early Warning System** - Detect failures in progress
4. **Timelapse Generation** - Create videos from active sessions

## 💡 Tips

- Start with 100 labeled images
- Balance offline/active examples
- Use temporal context when labeling
- Review uncertain predictions
- Iterate: label → train → analyze → repeat

## 🐛 Troubleshooting

See `QUICKSTART.md` for detailed troubleshooting, or:

- **Low accuracy?** Label more diverse examples
- **Out of memory?** Reduce batch size: `make train BATCH_SIZE=16`
- **Slow training?** Use GPU or reduce epochs
- **No images found?** Check symlink: `ls -la printer-timelapses`

---

**Ready to start?** Run `make setup` then `make explore`!

