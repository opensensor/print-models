# Phase 2: Failed Print Detection

This guide covers the second phase of the project: detecting failed prints vs successful prints.

## Overview

After filtering out offline/idle printer images in Phase 1, we now have **393 active printing images**. Phase 2 focuses on classifying these active images as either:
- **Good prints** - Successful prints with no issues
- **Failed prints** - Prints with problems (spaghetti, layer shifts, adhesion failures, etc.)

## Prerequisites

✅ Complete Phase 1:
- Trained printer-offline detection model
- Generated `data/active_images.txt` with 393 active images

## Workflow

### Step 1: Label Active Images

Label the active images as good or failed prints:

```bash
make label-failed
```

**Keyboard shortcuts:**
- `G` - Label as **good** print
- `F` - Label as **failed** print  
- `S` - Skip this image
- `B` - Go back to previous image
- `Q` - Save and quit

**Labeling tips:**
- Look for signs of failure:
  - Spaghetti (detached layers)
  - Layer shifts
  - Poor bed adhesion
  - Warping
  - Stringing/blobs
  - Incomplete prints
- Start with 50-100 labels to get a baseline
- Try to balance good vs failed examples

### Step 2: Check Label Distribution

```bash
make status-failed
```

Or analyze in detail:

```bash
source venv/bin/activate
python src/analyze_results.py --mode failed-labels
```

**Recommended balance:**
- Aim for at least 30 examples of each class
- Ideally 50+ of each for better model performance
- Balance ratio should be < 3:1

### Step 3: Train Failed Print Model

Once you have enough labeled examples:

```bash
make train-failed
```

This will:
- Train a ResNet18 model with transfer learning
- Use 80/20 train/validation split
- Save best model to `models/failed_print_detector.pth`
- Generate training history plot

**Training parameters:**
- Epochs: 20 (default)
- Batch size: 32
- Learning rate: 0.001
- Data augmentation: rotation, flip, color jitter

### Step 4: Evaluate Results

Check the training history plot:

```bash
ls -lh models/failed_print_detector_history.png
```

Expected results:
- Validation accuracy: 80-95% (depends on data quality)
- Training should converge within 10-15 epochs
- If overfitting (train >> val acc), add more data or augmentation

## File Structure

```
data/
├── active_images.txt              # List of 393 active images (from Phase 1)
├── failed_print_labels.json       # Your labels (good/failed)
└── failed_print_predictions.json  # Model predictions (after inference)

models/
├── failed_print_detector.pth      # Trained model
└── failed_print_detector_history.png  # Training curves

src/
├── label_failed_prints.py         # Interactive labeling tool
└── train_failed_print_model.py    # Training script
```

## Common Issues

### Not Enough Labels

**Problem:** "Need at least one example of each class!"

**Solution:** Label more images. You need at least 1 good and 1 failed example to start training.

### Imbalanced Dataset

**Problem:** Warning about class imbalance (e.g., 80 good, 10 failed)

**Solution:** 
- Label more examples of the minority class
- Look through different dates for failed prints
- Consider data augmentation for minority class

### Low Validation Accuracy

**Problem:** Model accuracy < 70%

**Possible causes:**
1. Not enough training data (< 50 total examples)
2. Ambiguous labels (hard to distinguish good vs failed)
3. High class imbalance

**Solutions:**
- Label more examples (aim for 100+ total)
- Review and fix incorrect labels
- Balance the dataset better
- Train for more epochs

### Overfitting

**Problem:** Train accuracy 100%, validation accuracy < 80%

**Solutions:**
- Add more training data
- Increase data augmentation
- Reduce training epochs
- Add dropout/regularization

## Next Steps

After training a good failed print detector:

1. **Run inference** on all active images
2. **Filter** to find all failed prints
3. **Analyze patterns** - which dates had more failures?
4. **Iterate** - retrain with more examples if needed
5. **Deploy** - use for real-time monitoring

## Tips for Success

1. **Start small** - Label 50 images, train, evaluate, then add more
2. **Be consistent** - Define clear criteria for "failed" vs "good"
3. **Use context** - Look at neighboring frames in the timelapse
4. **Iterate** - Model performance improves with more diverse examples
5. **Document** - Note what types of failures you're seeing

## Example Session

```bash
# Check status
make status-failed

# Label 50 images
make label-failed
# (Label until you have ~50 examples, then press Q)

# Check distribution
source venv/bin/activate
python src/analyze_results.py --mode failed-labels

# Train model
make train-failed

# Check results
ls -lh models/failed_print_detector*
```

## Questions?

- Review the training history plot to understand model performance
- Check `data/failed_print_labels.json` to see your labels
- Run `make help` to see all available commands

