# Quick Start Guide - Printer-Offline Detection

This guide will walk you through developing a model to detect printer-offline images.

## Overview

The goal is to filter out timelapse images where the printer is offline/inactive, leaving only images with actual printing activity for further analysis.

## Step-by-Step Workflow

### 1. Setup Environment

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Explore Your Data

First, let's understand what we're working with:

```bash
# See statistics about your images
python src/explore_images.py --mode stats

# Visualize random samples (opens matplotlib window)
python src/explore_images.py --mode random --num-samples 12

# View temporal sequence from a specific date
python src/explore_images.py --mode temporal --date 20251110 --start-idx 0
```

This will help you understand:
- How many images you have
- What offline vs active images look like
- Patterns in the data

### 3. Label Training Data

You need to manually label some images to train the model. Start with 100-200 images:

```bash
# Label 100 random images
python src/label_images.py --sample-size 100
```

**Labeling Interface:**
- Click **OFFLINE** (or press 'O') if the printer is off/idle
- Click **ACTIVE** (or press 'A') if the printer is running/printing
- Click **Skip** (or press 'S') to skip uncertain images
- Click **Back** (or press 'B') to go back
- Press 'Q' to quit and save progress

**Tips for labeling:**
- Offline: Empty build plate, no activity, lights off, or no visible changes
- Active: Printer head moving, print in progress, visible activity
- You can run the labeling tool multiple times - it saves progress to `data/labels.json`
- Aim for at least 50 examples of each class (offline and active)

### 4. Train the Model

Once you have labeled data:

```bash
# Train with default settings (20 epochs)
python src/train_model.py

# Or customize training
python src/train_model.py --epochs 30 --batch-size 16 --lr 0.0001
```

The model will:
- Use transfer learning with ResNet18
- Split your labeled data into train/validation sets
- Save the best model to `models/printer_offline_detector.pth`
- Generate a training history plot

**What to expect:**
- Training time depends on your hardware (GPU recommended)
- Validation accuracy should reach 85-95% with good labels
- If accuracy is low, label more diverse examples

### 5. Run Inference on All Images

Now classify all your images:

```bash
# Run inference and organize images
python src/inference.py --organize --filter-active

# Or just get predictions without organizing
python src/inference.py --output-json data/predictions.json
```

This will:
- Classify all images in `printer-timelapses/`
- Save predictions to `data/predictions.json`
- (If `--organize`) Copy images to `data/organized/offline/` and `data/organized/active/`
- (If `--filter-active`) Create a list of high-confidence active images

### 6. Review Results

Check the results:

```bash
# View predictions summary
cat data/predictions.json | grep -c '"offline"'
cat data/predictions.json | grep -c '"active"'

# View organized images
ls -lh data/organized/offline/
ls -lh data/organized/active/
```

### 7. Iterate and Improve

If the model isn't performing well:

1. **Label more diverse examples:**
   ```bash
   python src/label_images.py --sample-size 50
   ```

2. **Retrain with more data:**
   ```bash
   python src/train_model.py --epochs 25
   ```

3. **Adjust confidence thresholds:**
   ```bash
   python src/inference.py --organize --confidence-threshold 0.7
   ```

## Using the Workflow Script

For convenience, use the workflow script:

```bash
# Explore data
./workflow.sh explore

# Label images (default 100)
./workflow.sh label 100

# Train model
./workflow.sh train

# Run inference
./workflow.sh inference
```

## Next Steps

Once you have filtered out offline images, you can:

1. **Focus on active images** for the next classification task
2. **Develop a "failed print" detector** using the active images
3. **Build a timelapse video** from only active printing sessions
4. **Analyze print patterns** to detect early failure signs

## File Structure

```
print-models/
├── src/
│   ├── explore_images.py      # Data exploration
│   ├── label_images.py        # Interactive labeling tool
│   ├── train_model.py         # Model training
│   └── inference.py           # Batch inference
├── data/
│   ├── labels.json            # Your labeled data
│   ├── predictions.json       # Model predictions
│   ├── active_images.txt      # Filtered active images
│   └── organized/             # Organized images by prediction
├── models/
│   └── printer_offline_detector.pth  # Trained model
├── printer-timelapses/        # Symlink to your images
├── requirements.txt           # Python dependencies
└── workflow.sh               # Convenience script
```

## Troubleshooting

**"No images found"**
- Check that `printer-timelapses` symlink is correct
- Verify images are .jpg or .png format

**"Not enough labeled data"**
- You need at least 10 labeled images to train
- Recommended: 100+ images with balanced classes

**Low model accuracy**
- Label more diverse examples
- Check for labeling errors in `data/labels.json`
- Increase training epochs
- Try different learning rates

**Out of memory during training**
- Reduce batch size: `--batch-size 16` or `--batch-size 8`
- Use CPU if GPU memory is limited (slower but works)

## Tips for Success

1. **Start small:** Label 50-100 images first, train, evaluate
2. **Balance classes:** Try to have similar numbers of offline and active examples
3. **Diverse examples:** Include different times of day, lighting conditions
4. **Iterate:** The first model won't be perfect - that's expected!
5. **Use temporal context:** If unsure, look at neighboring images in the sequence

