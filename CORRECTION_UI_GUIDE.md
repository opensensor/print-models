# Label Correction UI - Quick Reference

## The Interface

When you run a correction command, a GUI window opens:

```
┌───────────────────────────────────────────────────────────────┐
│  Image 5/18 - 20251111T085545.jpg [Current: OFFLINE]          │
│                                                               │
│                                                               │
│                    [Printer Image]                            │
│                                                               │
│                                                               │
│                                                               │
│  ┌─────────────┐ ┌─────────────┐ ┌────────┐ ┌──────┐ ┌─────┐│
│  │  OFFLINE    │ │   ACTIVE    │ │  Skip  │ │ Back │ │Quit ││
│  │    (0)      │ │    (1)      │ │  (S)   │ │ (B)  │ │(Q)  ││
│  └─────────────┘ └─────────────┘ └────────┘ └──────┘ └─────┘│
└───────────────────────────────────────────────────────────────┘
```

## How to Use

### Click Buttons (Mouse)

- **OFFLINE (0)** - Click if printer is idle
- **ACTIVE (1)** - Click if printer is printing
- **Skip (S)** - Click to keep current label
- **Back (B)** - Click to go to previous image
- **Quit (Q)** - Click to save and exit

### Keyboard Shortcuts

Press these keys while the window is focused:

- **0** or **O** → Label as OFFLINE
- **1** or **A** → Label as ACTIVE
- **S** → Skip this image
- **B** → Go back to previous image
- **Q** → Quit and save

## Workflow

1. **Look at the image** - Is the printer printing?
2. **Click button or press key** - Choose OFFLINE or ACTIVE
3. **Next image appears** - Repeat for all images
4. **Done!** - Corrections are saved automatically

## Example Session

```bash
# Start correction
make correct-retrain DATE=20251111 TIME=08:54-09:25
```

**Terminal output:**
```
Finding images for 20251111 in range 08:54-09:25
Found 18 images

Loaded 150 existing labels

Correcting 18 images...
============================================================
Use buttons or keyboard shortcuts:
  0 or O - Label as OFFLINE
  1 or A - Label as ACTIVE
  S - Skip
  B - Go back
  Q - Quit
============================================================

✓ Updated: 20251111T085447.jpg -> ACTIVE
✓ Updated: 20251111T085545.jpg -> ACTIVE
- No change: 20251111T085650.jpg
✓ Updated: 20251111T085853.jpg -> ACTIVE
...

============================================================
Correction session complete!
============================================================
✓ Made 15 corrections
✓ Total labels: 165
============================================================

Label distribution:
  Active:  75 (45.5%)
  Offline: 90 (54.5%)

Starting automatic retraining...
```

## Tips

### Fast Labeling

Use keyboard shortcuts for speed:
- **1** for active prints (most common during print time)
- **0** for offline
- **S** to skip uncertain images

### Fix Mistakes

Made a mistake? Press **B** to go back!

### Take Breaks

Press **Q** to quit anytime. Your corrections are saved. Run the command again to continue.

### Focus the Window

Make sure the GUI window is focused (clicked) for keyboard shortcuts to work.

## Common Scenarios

### Scenario 1: All Images Are Active

The printer was running the whole time:

1. Look at first image → Press **1**
2. Look at second image → Press **1**
3. Continue pressing **1** for all images
4. Done in seconds!

### Scenario 2: Mixed Active/Offline

Some images are active, some offline:

1. Look at each image carefully
2. Press **1** if printing, **0** if idle
3. Use **B** if you make a mistake
4. Press **Q** when done

### Scenario 3: Uncertain Images

Not sure if printer is active?

1. Press **S** to skip
2. Come back later with more examples
3. Or make your best guess

## Keyboard Shortcuts Reference

| Key | Action |
|-----|--------|
| **0** | Label as OFFLINE |
| **O** | Label as OFFLINE (alternative) |
| **1** | Label as ACTIVE |
| **A** | Label as ACTIVE (alternative) |
| **S** | Skip (no change) |
| **B** | Back to previous image |
| **Q** | Quit and save |

## Button Reference

| Button | Color | Action |
|--------|-------|--------|
| **OFFLINE (0)** | Red | Label as offline |
| **ACTIVE (1)** | Green | Label as active |
| **Skip (S)** | Gray | Skip this image |
| **Back (B)** | Yellow | Previous image |
| **Quit (Q)** | Blue | Save and exit |

## Progress Indicator

The title bar shows:
```
Image 5/18 - 20251111T085545.jpg [Current: OFFLINE]
```

- **Image 5/18** - You're on image 5 of 18
- **20251111T085545.jpg** - Current filename
- **[Current: OFFLINE]** - Current label (what it's labeled as now)

## What Happens After

### If using `correct-time`:
```bash
make correct-time DATE=20251111 TIME=08:54-09:25
```
- Corrections are saved
- You manually retrain: `make train`

### If using `correct-retrain`:
```bash
make correct-retrain DATE=20251111 TIME=08:54-09:25
```
- Corrections are saved
- Model retrains automatically
- Ready to use immediately!

## Troubleshooting

### Window doesn't appear

**Problem:** No GUI window shows up

**Solution:** Make sure you're in a graphical environment (not SSH without X11)

### Keyboard shortcuts don't work

**Problem:** Pressing keys does nothing

**Solution:** Click on the GUI window to focus it, then try again

### Accidentally closed window

**Problem:** Clicked the X button

**Solution:** Your corrections up to that point are saved. Run the command again to continue.

### Can't see buttons

**Problem:** Window is too small

**Solution:** Resize the window or maximize it

## Summary

**Two ways to label:**
1. 🖱️ **Click buttons** - Easy and visual
2. ⌨️ **Press keys** - Fast and efficient

**Choose what works best for you!**

Most users find keyboard shortcuts faster once they get used to them:
- **1** for active
- **0** for offline
- **B** to go back
- **Q** to quit

---

## Quick Start

```bash
# Run correction
make correct-retrain DATE=20251111 TIME=08:54-09:25

# GUI opens
# For each image:
#   - Click ACTIVE or press 1 (if printing)
#   - Click OFFLINE or press 0 (if idle)
#   - Click Skip or press S (if unsure)

# Done! Model retrains automatically
```

Happy correcting! 🎯

