#!/usr/bin/env python3
"""
Interactive tool to correct mislabeled predictions and retrain the model.

Usage:
    python src/correct_labels.py --image-paths path1.jpg path2.jpg path3.jpg
    python src/correct_labels.py --from-monitor-log monitor.log
    python src/correct_labels.py --date 20251111 --time-range 08:54-09:25
"""

import argparse
import json
import re
from pathlib import Path
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from PIL import Image

def load_labels(labels_file):
    """Load existing labels."""
    if Path(labels_file).exists():
        with open(labels_file, 'r') as f:
            return json.load(f)
    return {}

def save_labels(labels, labels_file):
    """Save labels to file."""
    with open(labels_file, 'w') as f:
        json.dump(labels, f, indent=2)
    print(f"✓ Saved {len(labels)} labels to {labels_file}")

def parse_monitor_log(log_file):
    """Extract image paths from monitor log output."""
    images = []
    with open(log_file, 'r') as f:
        for line in f:
            # Match lines like: 🟢 [2025-11-11 08:54:47] 20251111T085447.jpg - Print OK
            match = re.search(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] (\d{8}T\d{6}\.jpg)', line)
            if match:
                timestamp_str, filename = match.groups()
                images.append({
                    'timestamp': timestamp_str,
                    'filename': filename
                })
    return images

def find_images_by_time_range(date, time_range):
    """Find images in a specific time range."""
    # Parse time range like "08:54-09:25"
    start_time, end_time = time_range.split('-')
    start_hour, start_min = map(int, start_time.split(':'))
    end_hour, end_min = map(int, end_time.split(':'))
    
    image_dir = Path(f'printer-timelapses/{date}')
    if not image_dir.exists():
        print(f"Error: Directory {image_dir} not found")
        return []
    
    images = []
    for img_path in sorted(image_dir.glob('*.jpg')):
        # Parse filename like 20251111T085447.jpg
        match = re.match(r'\d{8}T(\d{2})(\d{2})(\d{2})\.jpg', img_path.name)
        if match:
            hour, minute, second = map(int, match.groups())
            
            # Check if in range
            img_time = hour * 60 + minute
            start = start_hour * 60 + start_min
            end = end_hour * 60 + end_min
            
            if start <= img_time <= end:
                images.append(img_path)
    
    return images

class LabelCorrector:
    """Interactive GUI for correcting labels."""

    def __init__(self, images_to_correct, labels):
        self.images_to_correct = images_to_correct
        self.labels = labels
        self.current_idx = 0
        self.corrections_made = 0
        self.fig = None
        self.ax = None
        self.user_quit = False

    def label_offline(self, event):
        """Label current image as offline."""
        if self.current_idx < len(self.images_to_correct):
            img_path = str(self.images_to_correct[self.current_idx])
            old_label = self.labels.get(img_path)
            self.labels[img_path] = 'offline'
            if old_label != 'offline':
                self.corrections_made += 1
                print(f"✓ Updated: {self.images_to_correct[self.current_idx].name} -> OFFLINE")
            else:
                print(f"- No change: {self.images_to_correct[self.current_idx].name}")
            self.next_image()

    def label_active(self, event):
        """Label current image as active."""
        if self.current_idx < len(self.images_to_correct):
            img_path = str(self.images_to_correct[self.current_idx])
            old_label = self.labels.get(img_path)
            self.labels[img_path] = 'active'
            if old_label != 'active':
                self.corrections_made += 1
                print(f"✓ Updated: {self.images_to_correct[self.current_idx].name} -> ACTIVE")
            else:
                print(f"- No change: {self.images_to_correct[self.current_idx].name}")
            self.next_image()

    def skip_image(self, event):
        """Skip current image without changing label."""
        print(f"- Skipped: {self.images_to_correct[self.current_idx].name}")
        self.next_image()

    def previous_image(self, event):
        """Go back to previous image."""
        if self.current_idx > 0:
            self.current_idx -= 1
            self.show_current_image()

    def next_image(self):
        """Move to next image."""
        self.current_idx += 1
        if self.current_idx >= len(self.images_to_correct):
            print("\n" + "="*60)
            print("Correction session complete!")
            print("="*60)
            plt.close(self.fig)
        else:
            self.show_current_image()

    def quit_session(self, event):
        """Quit the correction session."""
        self.user_quit = True
        print("\nQuitting...")
        plt.close(self.fig)

    def show_current_image(self):
        """Display current image with correction interface."""
        if self.current_idx >= len(self.images_to_correct):
            return

        img_path = self.images_to_correct[self.current_idx]

        # Clear and update
        self.ax.clear()

        try:
            img = Image.open(img_path)
            self.ax.imshow(img)

            # Show progress and path
            progress = f"Image {self.current_idx + 1}/{len(self.images_to_correct)}"
            path_info = f"{img_path.name}"

            # Check current label (handle both string and numeric formats)
            current_label = self.labels.get(str(img_path))
            if current_label is not None:
                if current_label == 'active' or current_label == 1:
                    label_text = "ACTIVE"
                elif current_label == 'offline' or current_label == 0:
                    label_text = "OFFLINE"
                else:
                    label_text = str(current_label)
                label_info = f" [Current: {label_text}]"
            else:
                label_info = " [Not labeled]"

            self.ax.set_title(f"{progress} - {path_info}{label_info}", fontsize=12, fontweight='bold')
            self.ax.axis('off')

            self.fig.canvas.draw()
        except Exception as e:
            self.ax.text(0.5, 0.5, f"Error loading image:\n{e}",
                        ha='center', va='center', transform=self.ax.transAxes)
            self.ax.axis('off')
            self.fig.canvas.draw()

    def start(self):
        """Start the correction interface."""
        if not self.images_to_correct:
            print("No images to correct!")
            return self.corrections_made

        # Create figure and axes
        self.fig = plt.figure(figsize=(14, 10))

        # Main image axes
        self.ax = plt.axes([0.1, 0.2, 0.8, 0.75])

        # Button axes
        btn_offline_ax = plt.axes([0.1, 0.05, 0.15, 0.075])
        btn_active_ax = plt.axes([0.3, 0.05, 0.15, 0.075])
        btn_skip_ax = plt.axes([0.5, 0.05, 0.15, 0.075])
        btn_prev_ax = plt.axes([0.7, 0.05, 0.1, 0.075])
        btn_quit_ax = plt.axes([0.85, 0.05, 0.1, 0.075])

        # Create buttons
        btn_offline = Button(btn_offline_ax, 'OFFLINE (0)', color='lightcoral')
        btn_active = Button(btn_active_ax, 'ACTIVE (1)', color='lightgreen')
        btn_skip = Button(btn_skip_ax, 'Skip (S)', color='lightgray')
        btn_prev = Button(btn_prev_ax, 'Back (B)', color='lightyellow')
        btn_quit = Button(btn_quit_ax, 'Quit (Q)', color='lightblue')

        # Connect buttons
        btn_offline.on_clicked(self.label_offline)
        btn_active.on_clicked(self.label_active)
        btn_skip.on_clicked(self.skip_image)
        btn_prev.on_clicked(self.previous_image)
        btn_quit.on_clicked(self.quit_session)

        # Keyboard shortcuts
        def on_key(event):
            if event.key == '0' or event.key == 'o':
                self.label_offline(None)
            elif event.key == '1' or event.key == 'a':
                self.label_active(None)
            elif event.key == 's':
                self.skip_image(None)
            elif event.key == 'b':
                self.previous_image(None)
            elif event.key == 'q':
                self.quit_session(None)

        self.fig.canvas.mpl_connect('key_press_event', on_key)

        # Show first image
        self.show_current_image()

        plt.show()

        return self.corrections_made

def main():
    parser = argparse.ArgumentParser(description='Correct mislabeled predictions')
    
    # Different input methods
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--image-paths', nargs='+', help='Specific image paths to correct')
    input_group.add_argument('--from-monitor-log', help='Extract images from monitor log file')
    input_group.add_argument('--date', help='Date to correct (YYYYMMDD)')
    
    parser.add_argument('--time-range', help='Time range for --date option (HH:MM-HH:MM)')
    parser.add_argument('--labels-file', default='data/labels.json', help='Labels file to update')
    parser.add_argument('--auto-retrain', action='store_true', help='Automatically retrain model after corrections')
    
    args = parser.parse_args()
    
    # Determine which images to correct
    images_to_correct = []
    
    if args.image_paths:
        images_to_correct = [Path(p) for p in args.image_paths]
    
    elif args.from_monitor_log:
        print(f"Parsing monitor log: {args.from_monitor_log}")
        log_entries = parse_monitor_log(args.from_monitor_log)
        print(f"Found {len(log_entries)} images in log")
        
        # Ask user which ones to correct
        print("\nImages found:")
        for i, entry in enumerate(log_entries, 1):
            print(f"  {i}. [{entry['timestamp']}] {entry['filename']}")
        
        print("\nEnter image numbers to correct (e.g., '1 3 5' or '1-10' or 'all'):")
        selection = input("> ").strip()
        
        if selection == 'all':
            selected_indices = list(range(len(log_entries)))
        elif '-' in selection:
            start, end = map(int, selection.split('-'))
            selected_indices = list(range(start-1, end))
        else:
            selected_indices = [int(x)-1 for x in selection.split()]
        
        for idx in selected_indices:
            if 0 <= idx < len(log_entries):
                entry = log_entries[idx]
                # Find the actual file
                date = entry['timestamp'][:10].replace('-', '')
                filename = entry['filename']
                img_path = Path(f'printer-timelapses/{date}/{filename}')
                if img_path.exists():
                    images_to_correct.append(img_path)
    
    elif args.date:
        if not args.time_range:
            print("Error: --time-range required when using --date")
            return
        
        print(f"Finding images for {args.date} in range {args.time_range}")
        images_to_correct = find_images_by_time_range(args.date, args.time_range)
        print(f"Found {len(images_to_correct)} images")
    
    if not images_to_correct:
        print("No images to correct!")
        return
    
    # Load existing labels
    labels = load_labels(args.labels_file)
    print(f"\nLoaded {len(labels)} existing labels")

    # Start GUI correction session
    print(f"\nCorrecting {len(images_to_correct)} images...")
    print("=" * 60)
    print("Use buttons or keyboard shortcuts:")
    print("  0 or O - Label as OFFLINE")
    print("  1 or A - Label as ACTIVE")
    print("  S - Skip")
    print("  B - Go back")
    print("  Q - Quit")
    print("=" * 60)
    print()

    corrector = LabelCorrector(images_to_correct, labels)
    corrections_made = corrector.start()
    
    # Save updated labels
    if corrections_made > 0:
        save_labels(labels, args.labels_file)
        print(f"\n{'='*60}")
        print(f"✓ Made {corrections_made} corrections")
        print(f"✓ Total labels: {len(labels)}")
        print(f"{'='*60}")
        
        # Count label distribution (handle both string and numeric formats)
        active_count = sum(1 for v in labels.values() if v == 'active' or v == 1)
        offline_count = sum(1 for v in labels.values() if v == 'offline' or v == 0)
        print(f"\nLabel distribution:")
        print(f"  Active:  {active_count} ({active_count/len(labels)*100:.1f}%)")
        print(f"  Offline: {offline_count} ({offline_count/len(labels)*100:.1f}%)")
        
        # Auto-retrain if requested
        if args.auto_retrain:
            print(f"\n{'='*60}")
            print("Starting automatic retraining...")
            print(f"{'='*60}\n")
            
            import subprocess
            result = subprocess.run(
                ['python', 'src/train_model.py', '--epochs', '20', '--batch-size', '16'],
                cwd=Path.cwd()
            )
            
            if result.returncode == 0:
                print(f"\n{'='*60}")
                print("✓ Model retrained successfully!")
                print(f"{'='*60}")
            else:
                print(f"\n{'='*60}")
                print("✗ Retraining failed!")
                print(f"{'='*60}")
        else:
            print(f"\nTo retrain the model with updated labels, run:")
            print(f"  make train")
            print(f"  # or")
            print(f"  python src/train_model.py --epochs 20 --batch-size 16")
    else:
        print("\nNo corrections made.")

if __name__ == '__main__':
    main()

