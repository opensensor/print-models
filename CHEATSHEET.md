# Printer-Offline Detection - Command Cheat Sheet

## Quick Reference

### First Time Setup
```bash
make setup              # Install everything
make status             # Check what's ready
make explore            # See your data
```

### Main Workflow
```bash
make label              # Label 100 images (GUI)
make train              # Train model
make inference-org      # Classify & organize all images
make analyze            # Review results
```

### Labeling Shortcuts
- **O** = Offline (printer idle/off)
- **A** = Active (printer running)
- **S** = Skip (uncertain)
- **B** = Back (previous image)
- **Q** = Quit & save

### Common Commands

#### Data Exploration
```bash
make explore                    # Statistics
make explore-visual             # Random samples (GUI)
make explore-time              # Temporal sequence (GUI)
```

#### Labeling
```bash
make label                      # 100 images
make label-50                   # 50 images
make label-200                  # 200 images
```

#### Training
```bash
make train                      # Standard (20 epochs)
make train-quick                # Fast (10 epochs)
make train-long                 # Extended (30 epochs)
```

#### Inference
```bash
make inference                  # Just predictions
make inference-org              # Predictions + organize files
```

#### Analysis
```bash
make analyze                    # Full analysis
make analyze-conf               # Confidence plots
make analyze-uncertain          # Find uncertain predictions
```

#### Utilities
```bash
make status                     # Project status
make clean                      # Remove generated files (keep labels)
make clean-all                  # Remove everything
make help                       # Show all commands
```

### Manual Commands (if not using Make)

#### Activate Environment
```bash
source venv/bin/activate
```

#### Explore
```bash
python src/explore_images.py --mode stats
python src/explore_images.py --mode random --num-samples 12
python src/explore_images.py --mode temporal --date 20251110
```

#### Label
```bash
python src/label_images.py --sample-size 100
python src/label_images.py --sample-size 50 --sequential
```

#### Train
```bash
python src/train_model.py --epochs 20 --batch-size 32
python src/train_model.py --epochs 30 --lr 0.0001
```

#### Inference
```bash
python src/inference.py
python src/inference.py --organize --filter-active
python src/inference.py --organize --confidence-threshold 0.7
```

#### Analyze
```bash
python src/analyze_results.py --mode all
python src/analyze_results.py --mode labels
python src/analyze_results.py --mode predictions
python src/analyze_results.py --mode compare
python src/analyze_results.py --plot-confidence
python src/analyze_results.py --find-uncertain --uncertainty-threshold 0.6
```

### File Locations

#### Input
- `printer-timelapses/` - Your images (symlink)

#### Generated
- `data/labels.json` - Your labeled data
- `data/predictions.json` - Model predictions
- `data/active_images.txt` - Filtered active images
- `data/organized/offline/` - Offline images
- `data/organized/active/` - Active images
- `data/organized/uncertain/` - Low confidence images
- `models/printer_offline_detector.pth` - Trained model
- `models/training_history.png` - Training plots

### Typical Workflow

#### First Time
```bash
make setup              # 1. Install
make explore            # 2. Understand data
make label              # 3. Label 100 images
make train              # 4. Train model
make inference-org      # 5. Classify all images
make analyze            # 6. Review results
```

#### Iteration (if accuracy is low)
```bash
make analyze-uncertain  # 1. Find problem cases
make label-50           # 2. Label more examples
make train              # 3. Retrain
make inference-org      # 4. Re-classify
make analyze            # 5. Check improvement
```

### Troubleshooting

#### "No images found"
```bash
ls -la printer-timelapses/  # Check symlink
```

#### "Not enough labeled data"
```bash
make label-200          # Label more images
```

#### "Out of memory"
```bash
# Edit src/train_model.py and reduce batch_size
python src/train_model.py --batch-size 8
```

#### "Low accuracy"
```bash
make analyze-uncertain  # Find edge cases
make label-50           # Label more diverse examples
make train-long         # Train longer
```

#### Check status
```bash
make status             # See what's ready
cat data/labels.json | grep -c "offline"    # Count offline labels
cat data/labels.json | grep -c "active"     # Count active labels
```

### Tips

**Labeling:**
- Start with 100 images
- Balance offline/active (50/50 if possible)
- Look at neighboring images if unsure
- Skip if really uncertain

**Training:**
- Watch validation accuracy
- If val_acc << train_acc, you're overfitting
- If both low, need more/better labels
- GPU recommended but not required

**Inference:**
- Review uncertain predictions
- Adjust confidence threshold as needed
- Check organized folders for quality

**Iteration:**
- Label → Train → Analyze → Repeat
- Focus on errors and edge cases
- More diverse data > more similar data

### Expected Performance

- **Labeling**: ~30-60 seconds per image
- **Training**: 5-15 min (GPU), 30-60 min (CPU)
- **Inference**: ~5-10 minutes for 4,800 images (CPU)
- **Accuracy**: 85-95% with 100+ good labels

### Next Phase

After filtering offline images:

```bash
# Use only active images for next model
cat data/active_images.txt  # List of active images

# Next: Build failed print detector
# - Label active images as good/failed
# - Train second model
# - Detect print failures
```

### Quick Checks

```bash
# How many images?
find -L printer-timelapses -name '*.jpg' | wc -l

# How many labeled?
cat data/labels.json | grep -c '"label"'

# Model exists?
ls -lh models/printer_offline_detector.pth

# Predictions exist?
cat data/predictions.json | grep -c '"label"'

# How many active?
cat data/predictions.json | grep -c '"active"'

# How many offline?
cat data/predictions.json | grep -c '"offline"'
```

### Getting Help

```bash
make help                           # All make commands
python src/explore_images.py -h     # Explore options
python src/label_images.py -h       # Label options
python src/train_model.py -h        # Train options
python src/inference.py -h          # Inference options
python src/analyze_results.py -h    # Analyze options
```

### Demo Mode

```bash
./demo.sh               # Run quick demo with synthetic data
```

---

**Remember:** Label → Train → Analyze → Iterate!

