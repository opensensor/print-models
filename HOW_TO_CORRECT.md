# How to Correct Labels - Visual Guide

## The Setup

When you run the correction command, a **GUI window** will open with:

```
┌─────────────────────────────────────────────────────┐
│  Image 1/18 - 20251111T085447.jpg [Current: OFFLINE]│
│                                                     │
│              [Printer Image Here]                   │
│                                                     │
│                                                     │
│  ┌──────────┐ ┌──────────┐ ┌──────┐ ┌────┐ ┌────┐ │
│  │ OFFLINE  │ │ ACTIVE   │ │ Skip │ │Back│ │Quit│ │
│  │   (0)    │ │   (1)    │ │  (S) │ │(B) │ │(Q) │ │
│  └──────────┘ └──────────┘ └──────┘ └────┘ └────┘ │
└─────────────────────────────────────────────────────┘
```

**You can:**
- **Click the buttons** with your mouse
- **Press keyboard shortcuts** (0, 1, S, B, Q)

## Step-by-Step Process

### Step 1: Run the Command

In your terminal:
```bash
make correct-retrain DATE=20251111 TIME=08:54-09:25
```

### Step 2: GUI Window Opens

A window pops up showing:
- The printer image
- Current label (if any)
- Buttons at the bottom
- Progress (Image 1/18)

### Step 3: Look at the Image

**Ask yourself:** Is the printer actively printing in this image?

- **YES** → Click **ACTIVE (1)** button or press **1** key
- **NO** → Click **OFFLINE (0)** button or press **0** key

### Step 4: Click or Press Key

**Two ways to label:**

**Option A: Click the button**
- Click **OFFLINE (0)** if printer is idle
- Click **ACTIVE (1)** if printer is printing

**Option B: Press keyboard shortcut**
- Press **0** or **O** for OFFLINE
- Press **1** or **A** for ACTIVE
- Press **S** to skip
- Press **B** to go back
- Press **Q** to quit

### Step 5: Repeat

The next image appears automatically. Repeat for all images!

## Example Session

```
Terminal Output:
================

Finding images for 20251111 in range 08:54-09:25
Found 18 images

Loaded 150 existing labels

Correcting 18 images...

[Image window opens showing first image]

>>> Type 0, 1, s, or q and press ENTER: 1
✓ Updated: 20251111T085447.jpg -> ACTIVE

[Image window opens showing second image]

>>> Type 0, 1, s, or q and press ENTER: 1
✓ Updated: 20251111T085545.jpg -> ACTIVE

[Image window opens showing third image]

>>> Type 0, 1, s, or q and press ENTER: 1
✓ Updated: 20251111T085650.jpg -> ACTIVE

... (continues for all 18 images)

============================================================
✓ Made 18 corrections
✓ Total labels: 168
============================================================

Label distribution:
  Active:  78 (46.4%)
  Offline: 90 (53.6%)

Starting automatic retraining...
============================================================

[Training begins...]
```

## Common Questions

### Q: Can I use my mouse?

**A:** Yes! Click the buttons at the bottom of the window.

### Q: Can I use keyboard shortcuts?

**A:** Yes! Press **0** (offline), **1** (active), **S** (skip), **B** (back), or **Q** (quit).

### Q: What if I make a mistake?

**A:** Click the **Back (B)** button or press **B** to go back to the previous image.

### Q: How do I quit early?

**A:** Click the **Quit (Q)** button or press **Q**. Your corrections will be saved.

## Visual Workflow

```
1. Run command in terminal
   ↓
2. Image window pops up
   ↓
3. Look at image: Is printer printing?
   ↓
4. Go to terminal
   ↓
5. Type 1 (active) or 0 (offline)
   ↓
6. Press ENTER
   ↓
7. Image window closes
   ↓
8. Next image appears
   ↓
9. Repeat steps 3-8 for all images
   ↓
10. Done! Model retrains automatically
```

## Tips

1. **Keep both windows visible** - Arrange your screen so you can see both the image window and terminal
2. **Focus on terminal** - Always type in the terminal, not the image window
3. **Look carefully** - Take your time to look at each image
4. **Be consistent** - If printer is printing, always label as 1 (ACTIVE)
5. **Use skip** - If you're unsure, press 's' to skip

## Keyboard Shortcuts

While in the terminal prompt:

- **1** + ENTER = Label as ACTIVE (printer printing)
- **0** + ENTER = Label as OFFLINE (printer idle)
- **s** + ENTER = Skip this image
- **q** + ENTER = Quit and save

## Screen Layout Suggestion

```
┌──────────────────────┬──────────────────────┐
│                      │                      │
│  IMAGE WINDOW        │  TERMINAL            │
│  (matplotlib)        │  (bash/zsh)          │
│                      │                      │
│  [Printer Image]     │  >>> Type choice:    │
│                      │  _                   │
│                      │                      │
│                      │                      │
└──────────────────────┴──────────────────────┘
```

Arrange your windows side-by-side so you can:
- **Look left** at the image
- **Type right** in the terminal

## Troubleshooting

### Image window doesn't appear

**Problem:** No display configured

**Solution:** Make sure you're running in a graphical environment (not SSH without X11 forwarding)

### Can't see the terminal prompt

**Problem:** Image window is covering the terminal

**Solution:** Move or resize the image window to see the terminal

### Accidentally closed the image window

**Problem:** Clicked the X button on the image window

**Solution:** The script will continue - just type your choice in the terminal anyway, or press 'q' to quit and restart

## Summary

**Remember:**
- 👀 **LOOK** at the image window
- ⌨️ **TYPE** in the terminal
- ✅ Press **ENTER** to confirm

That's it! 🎉

---

## Quick Start

```bash
# Run the command
make correct-retrain DATE=20251111 TIME=08:54-09:25

# For each image:
# 1. Look at image window
# 2. Type in terminal: 1 (active) or 0 (offline)
# 3. Press ENTER
# 4. Repeat

# Done!
```

