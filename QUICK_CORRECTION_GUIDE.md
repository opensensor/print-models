# Quick Correction Guide

## Your Specific Case

You noticed false "Printer went offline" detections during monitoring:

```
🟢 [2025-11-11 08:54:47] 20251111T085447.jpg - Print OK (good: 2.4%)
⚫ [2025-11-11 08:55:45] 20251111T085545.jpg - Printer went offline  ← FALSE!
🟢 [2025-11-11 08:56:50] 20251111T085650.jpg - Print OK (good: 17.7%)
🟢 [2025-11-11 08:58:53] 20251111T085853.jpg - Print OK (good: 5.9%)
⚫ [2025-11-11 09:00:53] 20251111T090053.jpg - Printer went offline  ← FALSE!
🟢 [2025-11-11 09:02:56] 20251111T090256.jpg - Print OK (good: 11.5%)
⚫ [2025-11-11 09:06:34] 20251111T090634.jpg - Printer went offline  ← FALSE!
🟢 [2025-11-11 09:07:56] 20251111T090756.jpg - Print OK (good: 4.0%)
🟢 [2025-11-11 09:08:09] 20251111T090809.jpg - Print OK (good: 14.3%)
🟢 [2025-11-11 09:09:51] 20251111T090951.jpg - Print OK (good: 11.6%)
🟢 [2025-11-11 09:11:52] 20251111T091152.jpg - Print OK (good: 13.1%)
⚫ [2025-11-11 09:13:53] 20251111T091353.jpg - Printer went offline  ← FALSE!
🟢 [2025-11-11 09:17:53] 20251111T091753.jpg - Print OK (good: 13.7%)
⚫ [2025-11-11 09:19:51] 20251111T091951.jpg - Printer went offline  ← FALSE!
🟢 [2025-11-11 09:21:52] 20251111T092152.jpg - Print OK (good: 8.8%)
🟢 [2025-11-11 09:23:50] 20251111T092350.jpg - Print OK (good: 11.9%)
⚫ [2025-11-11 09:24:54] 20251111T092454.jpg - Printer went offline  ← FALSE!
```

## Fix It in 3 Steps

### Step 1: Correct the Labels

```bash
make correct-time DATE=20251111 TIME=08:54-09:25
```

This will:
1. Find all images in that time range (about 15-20 images)
2. Show you each image one by one
3. Let you correct the label

**For each image:**
- Press **1** if printer was ACTIVE (printing)
- Press **0** if printer was OFFLINE (idle)
- Press **s** to skip
- Press **q** to quit

### Step 2: Use the GUI

A window will open with buttons:

```
┌─────────────────────────────────────────────────────┐
│  Image 1/18 - 20251111T085447.jpg [Current: OFFLINE]│
│                                                     │
│              [Printer Image Here]                   │
│                                                     │
│  ┌──────────┐ ┌──────────┐ ┌──────┐ ┌────┐ ┌────┐ │
│  │ OFFLINE  │ │ ACTIVE   │ │ Skip │ │Back│ │Quit│ │
│  │   (0)    │ │   (1)    │ │  (S) │ │(B) │ │(Q) │ │
│  └──────────┘ └──────────┘ └──────┘ └────┘ └────┘ │
└─────────────────────────────────────────────────────┘
```

**Click the buttons or press keys:**
- **ACTIVE (1)** - Printer was printing
- **OFFLINE (0)** - Printer was idle
- **Skip (S)** - Keep current label
- **Back (B)** - Go to previous image
- **Quit (Q)** - Save and exit

### Step 3: Retrain the Model

After correcting, retrain:

```bash
make train
```

This will retrain the offline detection model with your corrections.

### Step 4: Test It

Monitor again to see if it's better:

```bash
make monitor
```

## One-Step Alternative

If you want to correct AND retrain in one command:

```bash
make correct-retrain DATE=20251111 TIME=08:54-09:25
```

This does both steps automatically!

## What to Expect

### During Correction

A **GUI window** will open with buttons and keyboard shortcuts!

**What you'll see:**

```
┌─────────────────────────────────────────────────────┐
│  Image 1/18 - 20251111T085545.jpg [Current: OFFLINE]│
│                                                     │
│              [Printer Image Here]                   │
│                                                     │
│  ┌──────────┐ ┌──────────┐ ┌──────┐ ┌────┐ ┌────┐ │
│  │ OFFLINE  │ │ ACTIVE   │ │ Skip │ │Back│ │Quit│ │
│  │   (0)    │ │   (1)    │ │  (S) │ │(B) │ │(Q) │ │
│  └──────────┘ └──────────┘ └──────┘ └────┘ └────┘ │
└─────────────────────────────────────────────────────┘
```

**How to use:**
1. Look at the image - Is the printer printing?
2. **Click a button** OR **press a key**:
   - Click **ACTIVE (1)** or press **1** → Printer is printing
   - Click **OFFLINE (0)** or press **0** → Printer is idle
   - Click **Skip (S)** or press **S** → Keep current label
   - Click **Back (B)** or press **B** → Go to previous image
3. Next image appears automatically!

**Terminal output:**
```
✓ Updated: 20251111T085545.jpg -> ACTIVE
✓ Updated: 20251111T085650.jpg -> ACTIVE
- No change: 20251111T085853.jpg
```

### After Correction

```
============================================================
✓ Made 6 corrections
✓ Total labels: 156
============================================================

Label distribution:
  Active:  66 (42.3%)
  Offline: 90 (57.7%)

To retrain the model with updated labels, run:
  make train
```

### After Retraining

```
Epoch 20/20: 100%|████████| 10/10 [00:15<00:00]
Train Loss: 0.1234, Train Acc: 96.15%
Val Loss: 0.0987, Val Acc: 95.00%

✓ Best model saved to models/printer_offline_detector.pth
```

## Tips

1. **Be consistent** - If printer was running, always label as ACTIVE (1)
2. **Look at the image** - Don't just trust the current label
3. **Correct in batches** - Do 10-20 corrections before retraining
4. **Test after retraining** - Run monitor to see if it improved

## Expected Improvement

After 1-2 correction cycles:
- Fewer false "offline" detections
- Better accuracy on your specific printer
- More reliable monitoring

After 5+ correction cycles:
- Very few false detections
- Model learns your printer's specific behavior
- Trustworthy real-time alerts

## Full Commands Reference

```bash
# Correct time range
make correct-time DATE=20251111 TIME=08:54-09:25

# Correct and auto-retrain
make correct-retrain DATE=20251111 TIME=08:54-09:25

# Correct specific images
make correct-images IMAGES='printer-timelapses/20251111/20251111T085545.jpg printer-timelapses/20251111/20251111T090053.jpg'

# Retrain manually
make train

# Check status
make status

# Monitor again
make monitor
```

## Troubleshooting

**Q: No window appears**
- Make sure you have X11/display configured
- Try running in a graphical environment

**Q: "No images found"**
- Check date format: `DATE=20251111` (not `2025-11-11`)
- Check time format: `TIME=08:54-09:25` (24-hour format)

**Q: Model not improving**
- Need more corrections (try 20-30 images)
- Make sure you're labeling correctly
- Check label balance (should be 30-70% active)

---

**Ready to fix those false detections? Run:**

```bash
make correct-retrain DATE=20251111 TIME=08:54-09:25
```

This will correct the labels and automatically retrain the model! 🚀

