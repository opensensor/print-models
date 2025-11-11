#!/bin/bash
# Demo script to show how the monitor works
# This simulates a live print by processing existing images slowly

echo "=== PRINT MONITOR DEMO ==="
echo ""
echo "This demo will process images from 20251110 one at a time"
echo "to simulate a live print monitoring session."
echo ""
echo "In real usage, you would run:"
echo "  make monitor"
echo ""
echo "And it would automatically detect new images as they arrive."
echo ""
read -p "Press Enter to start demo (Ctrl+C to stop)..."
echo ""

# Reset state for demo
rm -f data/monitor_state.json

# Run monitor with fast interval for demo
source venv/bin/activate
python src/monitor_print.py \
  --image-dir printer-timelapses/20251110 \
  --interval 2 \
  --offline-threshold 0.7 \
  --failed-threshold 0.6

