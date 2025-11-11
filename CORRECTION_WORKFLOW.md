# Label Correction & Model Improvement Workflow

When you notice false detections during monitoring, you can quickly correct them and retrain the model!

## Quick Start

### Scenario: False "Printer went offline" detections

You're monitoring a print and see this:
```
🟢 [2025-11-11 08:54:47] 20251111T085447.jpg - Print OK (good: 2.4%)
⚫ [2025-11-11 08:55:45] 20251111T085545.jpg - Printer went offline  ← FALSE!
🟢 [2025-11-11 08:56:50] 20251111T085650.jpg - Print OK (good: 17.7%)
🟢 [2025-11-11 08:58:53] 20251111T085853.jpg - Print OK (good: 5.9%)
⚫ [2025-11-11 09:00:53] 20251111T090053.jpg - Printer went offline  ← FALSE!
🟢 [2025-11-11 09:02:56] 20251111T090256.jpg - Print OK (good: 11.5%)
```

The printer was actually running the whole time!

### Solution: Correct the labels

**Option 1: Correct a time range (recommended)**
```bash
make correct-time DATE=20251111 TIME=08:54-09:25
```

**Option 2: Correct and auto-retrain**
```bash
make correct-retrain DATE=20251111 TIME=08:54-09:25
```

**Option 3: Correct specific images**
```bash
make correct-images IMAGES='printer-timelapses/20251111/20251111T085545.jpg printer-timelapses/20251111/20251111T090053.jpg'
```

## How It Works

### Step 1: Select Images

The tool will find all images in the specified time range:
```
Finding images for 20251111 in range 08:54-09:25
Found 15 images
```

### Step 2: Review Each Image

For each image, you'll see:
- The image displayed in a window
- Current label (if any)
- Options to correct

```
============================================================
Image: 20251111T085545.jpg
Current label: OFFLINE (0)
============================================================
Commands:
  0 - Label as OFFLINE
  1 - Label as ACTIVE
  s - Skip (keep current label)
  q - Quit
============================================================
Your choice: 
```

### Step 3: Make Corrections

- Press **1** if printer was ACTIVE (printing)
- Press **0** if printer was OFFLINE (idle)
- Press **s** to skip (no change)
- Press **q** to quit early

### Step 4: Review Summary

After correcting, you'll see:
```
============================================================
✓ Made 8 corrections
✓ Total labels: 158
============================================================

Label distribution:
  Active:  68 (43.0%)
  Offline: 90 (57.0%)

To retrain the model with updated labels, run:
  make train
```

### Step 5: Retrain Model

**Manual retrain:**
```bash
make train
```

**Or use auto-retrain:**
```bash
make correct-retrain DATE=20251111 TIME=08:54-09:25
```

This will automatically retrain after corrections!

## Common Workflows

### Workflow 1: Quick Correction During Print

You're monitoring and see false detections:

```bash
# 1. Note the time range with issues
# Example: 08:54-09:25 on 2025-11-11

# 2. Stop monitoring (Ctrl+C)

# 3. Correct the labels
make correct-time DATE=20251111 TIME=08:54-09:25

# 4. Retrain model
make train

# 5. Resume monitoring with improved model
make monitor
```

### Workflow 2: Batch Correction After Print

Print finished, review the log and fix issues:

```bash
# 1. Review monitor output (saved to file)
cat print.log | grep "went offline"

# 2. Identify time ranges with false detections
# Example: 08:54-09:25, 14:30-15:00

# 3. Correct each range
make correct-time DATE=20251111 TIME=08:54-09:25
make correct-time DATE=20251111 TIME=14:30-15:00

# 4. Retrain once with all corrections
make train
```

### Workflow 3: One-Step Correction & Retrain

For quick iterations:

```bash
# Correct and retrain in one command
make correct-retrain DATE=20251111 TIME=08:54-09:25
```

This is perfect when you want to immediately test the improved model!

### Workflow 4: Correct Specific Images

If you know exactly which images are wrong:

```bash
make correct-images IMAGES='printer-timelapses/20251111/20251111T085545.jpg printer-timelapses/20251111/20251111T090053.jpg'
```

## Advanced Usage

### From Monitor Log File

If you saved monitor output to a file:

```bash
# Save monitor output
make monitor > monitor.log 2>&1

# Later, extract and correct from log
python src/correct_labels.py --from-monitor-log monitor.log
```

The tool will parse the log and let you select which images to correct.

### Custom Labels File

For Phase 2 (failed print detection):

```bash
python src/correct_labels.py \
  --date 20251111 \
  --time-range 08:54-09:25 \
  --labels-file data/failed_print_labels.json
```

## Tips for Effective Correction

### 1. Correct in Batches

Don't correct one image at a time. Correct a time range:
- ✅ `make correct-time DATE=20251111 TIME=08:54-09:25`
- ❌ Correcting individual images one by one

### 2. Look for Patterns

If you see multiple false detections in a row, they're likely all wrong:
```
⚫ [09:00:53] - Printer went offline  ← Probably all false
⚫ [09:13:53] - Printer went offline  ← if print was continuous
⚫ [09:19:51] - Printer went offline  ← 
```

### 3. Retrain Periodically

Don't retrain after every correction:
- ✅ Collect 10-20 corrections, then retrain
- ❌ Retrain after each single correction

### 4. Check Label Balance

After corrections, check the distribution:
```
Active:  68 (43.0%)
Offline: 90 (57.0%)
```

Aim for reasonable balance (30-70% is fine).

### 5. Test After Retraining

After retraining, test on a known sequence:
```bash
# Retrain
make train

# Test on same time range
make monitor-date DATE=20251111
# (Ctrl+C after a few images)

# Check if false detections are fixed
```

## Iterative Improvement Cycle

```
1. Monitor print
   ↓
2. Notice false detections
   ↓
3. Correct labels (make correct-time)
   ↓
4. Retrain model (make train)
   ↓
5. Monitor next print
   ↓
6. Repeat until satisfied
```

Each iteration improves the model!

## Expected Results

### After 1-2 Correction Cycles
- Fewer false "offline" detections
- Better handling of edge cases
- More stable monitoring

### After 5+ Correction Cycles
- Very few false detections
- Model learns your specific printer behavior
- Reliable real-time monitoring

### Long Term
- 200+ labeled images
- 95%+ accuracy
- Minimal false positives
- Trustworthy alerts

## Troubleshooting

### "No images found"

Check date format:
```bash
# ✅ Correct
make correct-time DATE=20251111 TIME=08:54-09:25

# ❌ Wrong
make correct-time DATE=2025-11-11 TIME=08:54-09:25
```

### "Image not found"

Check directory structure:
```bash
ls printer-timelapses/20251111/
```

### "No corrections made"

You pressed 's' (skip) for all images. That's fine!

### Model not improving

- Need more diverse examples
- Check label quality (are you labeling correctly?)
- May need to adjust model architecture (advanced)

## Summary

**Quick correction workflow:**
```bash
# 1. Correct labels
make correct-time DATE=20251111 TIME=08:54-09:25

# 2. Retrain
make train

# 3. Test
make monitor
```

**One-step workflow:**
```bash
make correct-retrain DATE=20251111 TIME=08:54-09:25
```

**The more you correct, the better the model gets!** 🚀

---

## Command Reference

```bash
# Correct time range
make correct-time DATE=YYYYMMDD TIME=HH:MM-HH:MM

# Correct specific images
make correct-images IMAGES='path1.jpg path2.jpg'

# Correct and auto-retrain
make correct-retrain DATE=YYYYMMDD TIME=HH:MM-HH:MM

# Manual retrain
make train

# Check status
make status
```

Happy correcting! 🎯

