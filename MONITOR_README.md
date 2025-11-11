# Real-Time Print Monitor (tail -f style)

Monitor your 3D printer in real-time as new images arrive!

## Quick Start

### Monitor an Active Print

```bash
make monitor
```

This will continuously watch for new images in today's directory and classify them as they appear.

**Output looks like:**
```
============================================================
🖨️  PRINT MONITOR STARTED
============================================================
Monitoring: printer-timelapses/20251110
Polling every 30 seconds...
Press Ctrl+C to stop
============================================================

🟢 [2025-11-10 14:23:45] 20251110T142345.jpg - Print OK (good: 92.3%)
🟢 [2025-11-10 14:24:15] 20251110T142415.jpg - Print OK (good: 94.1%)
🟢 [2025-11-10 14:24:45] 20251110T142445.jpg - Print OK (good: 91.8%)
🚨 [2025-11-10 14:25:15] 20251110T142515.jpg
   ⚠️  FAILED PRINT DETECTED! (confidence: 87.2%)
   🔔 CHECK YOUR PRINTER NOW!

⚫ [2025-11-10 14:25:45] 20251110T142545.jpg - Printer went offline
```

## How It Works

1. **Polls directory** every 30 seconds (configurable)
2. **Detects new images** that haven't been processed yet
3. **Classifies each image:**
   - First: Is printer active or offline?
   - If active: Is print good or failed?
4. **Displays results** in real-time (like `tail -f`)
5. **Saves state** so you can stop/resume anytime

## Commands

### Basic Usage

```bash
# Monitor today's prints (30 second polling)
make monitor

# Monitor with faster polling (10 seconds)
make monitor-fast

# Monitor a specific date
make monitor-date DATE=20251110

# Demo with existing images (2 second polling)
./demo_monitor.sh
```

### Advanced Usage

```bash
# Custom settings
source venv/bin/activate
python src/monitor_print.py \
  --image-dir printer-timelapses/20251110 \
  --interval 15 \
  --offline-threshold 0.8 \
  --failed-threshold 0.7
```

## Output Symbols

- 🟢 **Active print** - Printer is running
- 🚨 **Failed print detected** - Immediate alert!
- ⚫ **Offline** - Printer went idle (only shown on status change)

## State Management

The monitor remembers which images it has processed in `data/monitor_state.json`.

**Resume monitoring:**
```bash
# Start
make monitor

# Stop (Ctrl+C)
^C

# Resume later - picks up where you left off
make monitor
```

**Reset state (reprocess all images):**
```bash
rm data/monitor_state.json
make monitor
```

## Use Cases

### 1. Live Monitoring During Print

Start when you begin a print:
```bash
make monitor
```

Leave it running in a terminal window. You'll see each new image classified in real-time.

### 2. Background Monitoring

Run in background and log to file:
```bash
nohup make monitor > print.log 2>&1 &

# Check log
tail -f print.log
```

### 3. Alert on Failure

Pipe to notification system:
```bash
make monitor | while read line; do
  if echo "$line" | grep -q "FAILED PRINT DETECTED"; then
    notify-send "Print Failed!" "$line"
  fi
done
```

### 4. Multiple Printers

Monitor multiple printers in different terminals:
```bash
# Terminal 1
python src/monitor_print.py --image-dir printer1/20251110

# Terminal 2
python src/monitor_print.py --image-dir printer2/20251110
```

## Configuration

### Polling Interval

How often to check for new images:
- **30 seconds** (default) - Good for most prints
- **10 seconds** (fast) - For critical prints
- **60 seconds** (slow) - For long prints

```bash
python src/monitor_print.py --image-dir DIR --interval 60
```

### Confidence Thresholds

Adjust sensitivity:

**Offline threshold** (default: 0.7)
- Higher = fewer false "active" detections
- Lower = catch more active prints

**Failed threshold** (default: 0.6)
- Higher = fewer false alarms
- Lower = catch more potential failures

```bash
python src/monitor_print.py \
  --image-dir DIR \
  --offline-threshold 0.9 \
  --failed-threshold 0.8
```

## Tips

1. **Start before the print** - Catch everything from the beginning
2. **Use tmux/screen** - Keep monitor running even if you disconnect
3. **Adjust thresholds** - Tune based on your false positive rate
4. **Check the log** - Review `print.log` after long prints
5. **Reset state for testing** - Use `--reset` flag to reprocess images

## Troubleshooting

### No images detected

Check:
```bash
# Is directory correct?
ls -la printer-timelapses/20251110/

# Are new images arriving?
watch -n 5 'ls -lt printer-timelapses/20251110/ | head -5'
```

### Too many false positives

Increase thresholds:
```bash
python src/monitor_print.py \
  --image-dir printer-timelapses/20251110 \
  --offline-threshold 0.9 \
  --failed-threshold 0.8
```

### Missing failures

Decrease failed threshold:
```bash
python src/monitor_print.py \
  --image-dir printer-timelapses/20251110 \
  --failed-threshold 0.5
```

## Integration Examples

### Discord Webhook

Add to `monitor_print.py`:
```python
import requests

def send_discord_alert(message):
    webhook_url = "YOUR_WEBHOOK_URL"
    data = {"content": f"🚨 {message}"}
    requests.post(webhook_url, json=data)

# In the monitoring loop, when failure detected:
send_discord_alert(f"Print failed at {timestamp}!")
```

### Pushover Notification

```bash
make monitor | while read line; do
  if echo "$line" | grep -q "FAILED PRINT DETECTED"; then
    curl -s \
      --form-string "token=YOUR_APP_TOKEN" \
      --form-string "user=YOUR_USER_KEY" \
      --form-string "message=$line" \
      https://api.pushover.net/1/messages.json
  fi
done
```

### Home Assistant

```bash
# When failure detected, update sensor
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"state": "failed"}' \
  http://homeassistant.local:8123/api/states/sensor.printer_status
```

## Next Steps

- Set up automated alerts (Discord, email, SMS)
- Create a web dashboard
- Add more sophisticated failure detection
- Integrate with OctoPrint/Klipper

---

**Happy printing!** 🖨️✨

