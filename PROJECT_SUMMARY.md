# Project Summary - Printer-Offline Detection Model

## Overview

This project provides a complete machine learning pipeline to detect and filter out "printer-offline" images from 3D printer timelapse sequences. This is the first step in building a comprehensive failed print detection system.

## What Was Built

### 1. **Data Exploration Tools** (`src/explore_images.py`)
- Analyze image dataset statistics (count, dimensions, file sizes)
- Visualize random samples to understand the data
- View temporal sequences to see patterns over time
- Helps you understand what offline vs active images look like

### 2. **Interactive Labeling Tool** (`src/label_images.py`)
- User-friendly GUI for manually labeling images
- Keyboard shortcuts for fast labeling (O=offline, A=active, S=skip, B=back)
- Saves progress incrementally to `data/labels.json`
- Supports resuming labeling sessions
- Shows labeling progress and statistics

### 3. **Model Training Pipeline** (`src/train_model.py`)
- Uses transfer learning with ResNet18 (pre-trained on ImageNet)
- Automatic train/validation split with stratification
- Data augmentation for better generalization
- Learning rate scheduling
- Saves best model based on validation accuracy
- Generates training history plots
- Typical accuracy: 85-95% with good labeled data

### 4. **Batch Inference System** (`src/inference.py`)
- Classifies all images in the dataset
- Provides confidence scores for each prediction
- Can organize images into folders (offline/active/uncertain)
- Generates filtered lists of high-confidence active images
- Saves predictions to JSON for further analysis

### 5. **Analysis Tools** (`src/analyze_results.py`)
- Analyze label distribution and balance
- Analyze prediction statistics
- Compare labels vs predictions (confusion matrix)
- Plot confidence distributions
- Find uncertain predictions for review
- Helps identify areas for improvement

### 6. **Workflow Automation** (`workflow.sh`)
- Convenience script to run common tasks
- Handles virtual environment activation
- Provides guided workflow

## Your Dataset

Based on the exploration, you have:
- **4,821 total images** across 4 days (Nov 7-10, 2025)
- Images are 1920x1080 JPEG format
- Average file size: ~297 KB
- Distribution:
  - Nov 7: 1,411 images
  - Nov 8: 1,426 images
  - Nov 9: 1,135 images
  - Nov 10: 849 images

## Recommended Workflow

### Phase 1: Initial Model (You are here)
1. ✅ **Setup complete** - Environment and tools ready
2. **Label 100-200 images** - Start with diverse examples
   ```bash
   source venv/bin/activate
   python src/label_images.py --sample-size 100
   ```
3. **Train initial model** - Get baseline performance
   ```bash
   python src/train_model.py --epochs 20
   ```
4. **Run inference** - Classify all images
   ```bash
   python src/inference.py --organize --filter-active
   ```
5. **Analyze results** - Check performance
   ```bash
   python src/analyze_results.py --mode all --plot-confidence
   ```

### Phase 2: Iteration (If needed)
6. **Review uncertain predictions** - Find edge cases
   ```bash
   python src/analyze_results.py --find-uncertain --uncertainty-threshold 0.6
   ```
7. **Label more examples** - Focus on uncertain cases
   ```bash
   python src/label_images.py --sample-size 50
   ```
8. **Retrain** - Improve model with more data
   ```bash
   python src/train_model.py --epochs 25
   ```

### Phase 3: Production Use
9. **Filter dataset** - Keep only active images
10. **Next model** - Develop "failed print" detector using active images

## Key Files

### Configuration & Setup
- `requirements.txt` - Python dependencies
- `.gitignore` - Excludes data/models from git
- `README.md` - Project overview
- `QUICKSTART.md` - Detailed usage guide
- `PROJECT_SUMMARY.md` - This file

### Source Code
- `src/explore_images.py` - Data exploration
- `src/label_images.py` - Interactive labeling
- `src/train_model.py` - Model training
- `src/inference.py` - Batch prediction
- `src/analyze_results.py` - Results analysis

### Data Files (Created during use)
- `data/labels.json` - Your labeled training data
- `data/predictions.json` - Model predictions on all images
- `data/active_images.txt` - Filtered list of active images
- `data/organized/` - Images organized by prediction
- `models/printer_offline_detector.pth` - Trained model

## Technical Details

### Model Architecture
- **Base**: ResNet18 (pre-trained on ImageNet)
- **Modification**: Final layer replaced for binary classification
- **Input**: 224x224 RGB images
- **Output**: 2 classes (offline=0, active=1)
- **Training**: Adam optimizer, CrossEntropyLoss, learning rate scheduling

### Data Augmentation
- Random horizontal flip
- Random rotation (±5°)
- Color jitter (brightness, contrast)
- Standard ImageNet normalization

### Performance Expectations
- **Training time**: 5-15 minutes on GPU, 30-60 minutes on CPU (20 epochs)
- **Inference time**: ~1-2 images/second on CPU, ~10-20 images/second on GPU
- **Expected accuracy**: 85-95% with 100+ well-labeled examples
- **Memory usage**: ~2GB GPU memory, ~4GB system RAM

## Next Steps

After successfully filtering offline images, you can:

1. **Build Failed Print Detector**
   - Use only the "active" images
   - Label them as "good print" vs "failed print"
   - Train a second model using the same pipeline
   - Look for signs like: spaghetti, layer shifts, warping, detachment

2. **Temporal Analysis**
   - Analyze sequences of active images
   - Detect when prints start/stop
   - Create clean timelapse videos
   - Track print duration

3. **Early Failure Detection**
   - Analyze patterns in failed prints
   - Detect failures in progress
   - Alert system for intervention

4. **Multi-Printer Support**
   - Extend to handle multiple printers
   - Compare printer performance
   - Aggregate statistics

## Tips for Success

### Labeling
- **Be consistent**: Define clear criteria for offline vs active
- **Use context**: Look at neighboring images if unsure
- **Balance classes**: Try to label similar numbers of each class
- **Diverse examples**: Include different times, lighting, print states

### Training
- **Start small**: 100 labels → train → evaluate → iterate
- **Monitor validation**: If val accuracy << train accuracy, you're overfitting
- **Adjust epochs**: More epochs if still improving, fewer if plateauing
- **Learning rate**: Default (0.001) usually works, try 0.0001 if unstable

### Inference
- **Confidence threshold**: Higher = more certain but fewer images
- **Review uncertain**: Images with low confidence may need more training examples
- **Batch processing**: Process all images at once for consistency

## Troubleshooting

### "Not enough labeled data"
- Need at least 10 labeled images, recommend 100+
- Run: `python src/label_images.py --sample-size 100`

### Low model accuracy
- Label more diverse examples
- Check for labeling errors in `data/labels.json`
- Increase training epochs
- Ensure balanced classes

### Out of memory
- Reduce batch size: `--batch-size 16` or `--batch-size 8`
- Use CPU instead of GPU (slower but works)

### Slow inference
- Use GPU if available
- Process in batches (already implemented)
- Consider smaller model if needed

## Project Statistics

- **Lines of code**: ~800 (Python)
- **Scripts**: 5 main tools
- **Dependencies**: 8 Python packages
- **Model size**: ~45 MB (ResNet18)
- **Development time**: ~2 hours to set up complete pipeline

## Future Enhancements

Potential improvements for later:
- [ ] Web interface for labeling
- [ ] Active learning (model suggests uncertain images to label)
- [ ] Ensemble models for better accuracy
- [ ] Real-time monitoring and alerts
- [ ] Integration with printer APIs
- [ ] Automated timelapse video generation
- [ ] Multi-class classification (offline/printing/finished/failed)

## License & Credits

This is a custom-built pipeline using:
- PyTorch for deep learning
- torchvision for pre-trained models
- OpenCV and PIL for image processing
- matplotlib for visualization
- scikit-learn for data splitting

---

**Ready to start?** See `QUICKSTART.md` for step-by-step instructions!

