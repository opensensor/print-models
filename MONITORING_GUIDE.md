# Real-Time Print Monitoring Guide

Monitor your 3D printer in real-time as new timelapse images arrive!

## Overview

The monitoring script polls a directory for new images and automatically classifies them using both models:

1. **Printer Offline Detection** - Is the printer active or idle?
2. **Failed Print Detection** - If active, is the print good or failed?

Perfect for monitoring ongoing prints that capture images every 30 seconds.

## Quick Start

### Monitor Today's Print

```bash
make monitor
```

This will:
- Monitor today's directory (e.g., `printer-timelapses/20251110`)
- Check for new images every 30 seconds
- Classify each new image as offline/active
- If active, check if the print is good or failed
- Alert you immediately if a failure is detected

### Monitor with Faster Polling (10 seconds)

```bash
make monitor-fast
```

### Monitor a Specific Date

```bash
make monitor-date DATE=20251110
```

## How It Works

### Workflow

```
New Image Arrives
    ↓
Stage 1: Offline Detection
    ↓
Is printer active?
    ├─ NO → Mark as OFFLINE ⚫
    └─ YES → Mark as ACTIVE 🟢
         ↓
    Stage 2: Failed Print Detection
         ↓
    Is print failing?
         ├─ NO → Print looks good ✓
         └─ YES → ⚠️ FAILURE DETECTED! 🚨
```

### Example Output

```
============================================================
🖨️  PRINT MONITOR STARTED
============================================================

Using device: cpu
Loading models...
Monitoring directory: printer-timelapses/20251110
Poll interval: 30 seconds
Offline threshold: 0.7
Failed threshold: 0.6

Found 1 new image(s)
------------------------------------------------------------
🟢 [2025-11-10 14:23:45] 20251110T142345.jpg
   Status: ACTIVE (confidence: 98.5%)
   ✓ Print looks good (confidence: 92.3%)

Found 1 new image(s)
------------------------------------------------------------
🟢 [2025-11-10 14:24:15] 20251110T142415.jpg
   Status: ACTIVE (confidence: 99.1%)
   ⚠️  WARNING: FAILED PRINT DETECTED! (confidence: 87.2%)
   🚨 Check your printer immediately!
```

## Advanced Usage

### Custom Parameters

Run the script directly with custom settings:

```bash
source venv/bin/activate
python src/monitor_print.py \
  --image-dir printer-timelapses/20251110 \
  --interval 15 \
  --offline-threshold 0.8 \
  --failed-threshold 0.7
```

**Parameters:**
- `--image-dir` - Directory to monitor (required)
- `--interval` - Seconds between polls (default: 30)
- `--offline-threshold` - Confidence threshold for "active" (default: 0.7)
- `--failed-threshold` - Confidence threshold for "failed" (default: 0.6)
- `--reset` - Reset state and reprocess all images

### Reset State

The monitor tracks which images it has already processed in `data/monitor_state.json`. To reprocess all images:

```bash
python src/monitor_print.py --image-dir printer-timelapses/20251110 --reset
```

## Use Cases

### 1. Live Print Monitoring

Start the monitor when you begin a print:

```bash
make monitor
```

Leave it running in a terminal. You'll get real-time updates as each image arrives.

### 2. Overnight Prints

Start monitoring before bed:

```bash
nohup make monitor > print_monitor.log 2>&1 &
```

Check the log in the morning to see if any failures were detected.

### 3. Remote Monitoring

Run on a server and get notifications:

```bash
# Add to monitor_print.py or wrap with notification script
make monitor | while read line; do
  if echo "$line" | grep -q "FAILED PRINT DETECTED"; then
    # Send notification (email, SMS, Discord, etc.)
    notify-send "Print Failed!" "$line"
  fi
done
```

### 4. Batch Processing

Process all images from a specific date (useful for testing):

```bash
python src/monitor_print.py --image-dir printer-timelapses/20251107 --reset
```

## State Management

### State File: `data/monitor_state.json`

The monitor saves its state to avoid reprocessing images:

```json
{
  "processed_images": [
    "printer-timelapses/20251110/20251110T142345.jpg",
    "printer-timelapses/20251110/20251110T142415.jpg"
  ],
  "last_update": "2025-11-10T14:24:30"
}
```

### Resume Monitoring

If you stop the monitor (Ctrl+C) and restart it, it will automatically resume from where it left off:

```bash
# Start monitoring
make monitor

# Stop with Ctrl+C
^C
🛑 MONITOR STOPPED
State saved. You can resume monitoring later.

# Resume later - will skip already processed images
make monitor
```

## Stopping the Monitor

Press **Ctrl+C** to stop gracefully:

```
^C
============================================================
🛑 MONITOR STOPPED
============================================================
Processed 42 total images
State saved. You can resume monitoring later.
```

## Troubleshooting

### "Directory not found"

Make sure the directory exists:

```bash
ls -la printer-timelapses/
```

The monitor expects a date-based directory like `20251110`.

### No new images detected

Check that:
1. Images are being saved to the correct directory
2. Images have `.jpg`, `.jpeg`, or `.png` extensions
3. The poll interval is long enough for new images to arrive

### Model not found

Ensure both models are trained:

```bash
make status
make status-failed
```

If models are missing:
- Run `make train` for offline detection
- Run `make train-failed` for failed print detection

### High false positive rate

Adjust confidence thresholds:

```bash
# More conservative (fewer false positives)
python src/monitor_print.py \
  --image-dir printer-timelapses/20251110 \
  --offline-threshold 0.9 \
  --failed-threshold 0.8
```

## Tips

1. **Start monitoring before the print** - This way you catch everything from the beginning

2. **Adjust thresholds based on your data** - If you get too many false alarms, increase the thresholds

3. **Use with notifications** - Pipe output to a notification system for alerts

4. **Monitor multiple printers** - Run multiple instances with different directories

5. **Check the state file** - If something seems wrong, check `data/monitor_state.json`

## Integration Ideas

### Discord Webhook

```python
# Add to monitor_print.py
import requests

def send_discord_alert(message):
    webhook_url = "YOUR_WEBHOOK_URL"
    requests.post(webhook_url, json={"content": message})
```

### Email Alerts

```python
import smtplib
from email.message import EmailMessage

def send_email_alert(subject, body):
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = "printer@example.com"
    msg['To'] = "you@example.com"
    
    with smtplib.SMTP('localhost') as s:
        s.send_message(msg)
```

### Home Assistant

```bash
# Call Home Assistant API when failure detected
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"state": "failed", "attributes": {"friendly_name": "3D Printer"}}' \
  http://homeassistant.local:8123/api/states/sensor.printer_status
```

## Next Steps

- Set up automated notifications
- Create a dashboard to visualize print status
- Add more sophisticated failure detection
- Integrate with OctoPrint or other printer management software

