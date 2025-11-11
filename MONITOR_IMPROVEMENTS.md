# Monitor Improvements

## Issue: Race Condition with File Uploads

### Problem
The monitor was encountering errors when trying to classify images that were still being uploaded from the camera device:

```
Error classifying printer-timelapses/20251111/20251111T145355.jpg: cannot identify image file
```

This happened because:
1. The file appeared in the directory (detected by the monitor)
2. The monitor immediately tried to open and classify it
3. The file wasn't fully written yet, causing PIL to fail

### Solution
Added retry logic with file validation in `src/monitor_print.py`:

```python
def classify_image(self, image_path, model, max_retries=3, retry_delay=0.5):
    """Classify a single image with retry logic for incomplete file uploads."""
    
    for attempt in range(max_retries):
        try:
            # Check if file exists and has non-zero size
            if not os.path.exists(image_path) or os.path.getsize(image_path) == 0:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                else:
                    return None, None
            
            # Classify the image
            image = Image.open(image_path).convert('RGB')
            # ... classification logic ...
            
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)  # Wait and retry
            else:
                print(f"Error after {max_retries} attempts: {e}")
                return None, None
```

### How It Works
1. **File validation**: Checks if file exists and has non-zero size before opening
2. **Retry mechanism**: Up to 3 attempts with 0.5 second delays between attempts
3. **Graceful failure**: If all retries fail, returns `None` and skips the image
4. **Automatic retry**: Failed images aren't marked as processed, so they'll be retried on the next poll cycle

### Benefits
- Handles incomplete file uploads gracefully
- Reduces false "offline" detections caused by upload timing
- No manual intervention needed - automatically retries
- Failed images are retried on next poll (30 seconds later)

### Configuration
You can adjust the retry behavior by modifying these parameters in the `classify_image` method:
- `max_retries=3` - Number of retry attempts (default: 3)
- `retry_delay=0.5` - Delay between retries in seconds (default: 0.5)

For slower network uploads, you might want to increase these values.

