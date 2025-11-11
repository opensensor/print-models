#!/usr/bin/env python3
"""
Simple image labeling tool for creating training data.
Allows manual classification of images as 'offline' or 'active'.
"""

import os
import json
import random
from pathlib import Path
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.widgets import Button


class ImageLabeler:
    def __init__(self, base_dir="printer-timelapses", labels_file="data/labels.json", 
                 sample_size=None, random_sample=True):
        self.base_dir = Path(base_dir)
        self.labels_file = Path(labels_file)
        self.labels = self.load_labels()
        
        # Get all images
        self.all_images = self.get_all_images()
        
        # Filter to unlabeled images or sample
        if sample_size:
            unlabeled = [img for img in self.all_images if str(img) not in self.labels]
            if random_sample:
                self.images_to_label = random.sample(unlabeled, min(sample_size, len(unlabeled)))
            else:
                self.images_to_label = unlabeled[:sample_size]
        else:
            self.images_to_label = [img for img in self.all_images if str(img) not in self.labels]
        
        self.current_idx = 0
        self.fig = None
        self.ax = None
        
        print(f"Found {len(self.all_images)} total images")
        print(f"Already labeled: {len(self.labels)}")
        print(f"To label in this session: {len(self.images_to_label)}")
    
    def get_all_images(self):
        """Recursively find all image files."""
        image_extensions = {'.jpg', '.jpeg', '.png'}
        images = []
        for ext in image_extensions:
            images.extend(self.base_dir.rglob(f'*{ext}'))
            images.extend(self.base_dir.rglob(f'*{ext.upper()}'))
        return sorted(images)
    
    def load_labels(self):
        """Load existing labels from JSON file."""
        if self.labels_file.exists():
            with open(self.labels_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_labels(self):
        """Save labels to JSON file."""
        self.labels_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.labels_file, 'w') as f:
            json.dump(self.labels, f, indent=2)
        print(f"Saved {len(self.labels)} labels to {self.labels_file}")
    
    def label_offline(self, event):
        """Label current image as offline."""
        if self.current_idx < len(self.images_to_label):
            img_path = str(self.images_to_label[self.current_idx])
            self.labels[img_path] = 'offline'
            print(f"Labeled as OFFLINE: {img_path}")
            self.next_image()
    
    def label_active(self, event):
        """Label current image as active."""
        if self.current_idx < len(self.images_to_label):
            img_path = str(self.images_to_label[self.current_idx])
            self.labels[img_path] = 'active'
            print(f"Labeled as ACTIVE: {img_path}")
            self.next_image()
    
    def skip_image(self, event):
        """Skip current image without labeling."""
        print(f"Skipped: {self.images_to_label[self.current_idx]}")
        self.next_image()
    
    def previous_image(self, event):
        """Go back to previous image."""
        if self.current_idx > 0:
            self.current_idx -= 1
            self.show_current_image()
    
    def next_image(self):
        """Move to next image."""
        self.current_idx += 1
        if self.current_idx >= len(self.images_to_label):
            print("\nLabeling session complete!")
            self.save_labels()
            self.show_summary()
            plt.close(self.fig)
        else:
            self.show_current_image()
    
    def show_current_image(self):
        """Display current image with labeling interface."""
        if self.current_idx >= len(self.images_to_label):
            return
        
        img_path = self.images_to_label[self.current_idx]
        
        # Clear and update
        self.ax.clear()
        
        try:
            img = Image.open(img_path)
            self.ax.imshow(img)
            
            # Show progress and path
            progress = f"Image {self.current_idx + 1}/{len(self.images_to_label)}"
            path_info = f"{img_path.parent.name}/{img_path.name}"
            
            # Check if already labeled
            existing_label = self.labels.get(str(img_path), None)
            label_info = f" [Previously: {existing_label}]" if existing_label else ""
            
            self.ax.set_title(f"{progress} - {path_info}{label_info}", fontsize=10)
            self.ax.axis('off')
            
            self.fig.canvas.draw()
        except Exception as e:
            self.ax.text(0.5, 0.5, f"Error loading image:\n{e}", 
                        ha='center', va='center', transform=self.ax.transAxes)
            self.ax.axis('off')
            self.fig.canvas.draw()
    
    def show_summary(self):
        """Show summary of labeled data."""
        offline_count = sum(1 for label in self.labels.values() if label == 'offline')
        active_count = sum(1 for label in self.labels.values() if label == 'active')
        
        print("\n=== Labeling Summary ===")
        print(f"Total labeled: {len(self.labels)}")
        print(f"  Offline: {offline_count}")
        print(f"  Active: {active_count}")
        print(f"Labels saved to: {self.labels_file}")
    
    def start(self):
        """Start the labeling interface."""
        if not self.images_to_label:
            print("No images to label!")
            self.show_summary()
            return
        
        # Create figure and axes
        self.fig = plt.figure(figsize=(14, 10))
        
        # Main image axes
        self.ax = plt.axes([0.1, 0.2, 0.8, 0.75])
        
        # Button axes
        btn_offline_ax = plt.axes([0.15, 0.05, 0.15, 0.075])
        btn_active_ax = plt.axes([0.35, 0.05, 0.15, 0.075])
        btn_skip_ax = plt.axes([0.55, 0.05, 0.15, 0.075])
        btn_prev_ax = plt.axes([0.75, 0.05, 0.1, 0.075])
        
        # Create buttons
        btn_offline = Button(btn_offline_ax, 'OFFLINE (O)', color='lightcoral')
        btn_active = Button(btn_active_ax, 'ACTIVE (A)', color='lightgreen')
        btn_skip = Button(btn_skip_ax, 'Skip (S)', color='lightgray')
        btn_prev = Button(btn_prev_ax, 'Back (B)', color='lightyellow')
        
        # Connect buttons
        btn_offline.on_clicked(self.label_offline)
        btn_active.on_clicked(self.label_active)
        btn_skip.on_clicked(self.skip_image)
        btn_prev.on_clicked(self.previous_image)
        
        # Keyboard shortcuts
        def on_key(event):
            if event.key == 'o':
                self.label_offline(None)
            elif event.key == 'a':
                self.label_active(None)
            elif event.key == 's':
                self.skip_image(None)
            elif event.key == 'b':
                self.previous_image(None)
            elif event.key == 'q':
                self.save_labels()
                plt.close(self.fig)
        
        self.fig.canvas.mpl_connect('key_press_event', on_key)
        
        # Show first image
        self.show_current_image()
        
        plt.show()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Label images for training")
    parser.add_argument('--sample-size', type=int, default=100,
                       help='Number of images to label in this session')
    parser.add_argument('--random', action='store_true', default=True,
                       help='Randomly sample images')
    parser.add_argument('--sequential', action='store_true',
                       help='Sample images sequentially instead of randomly')
    parser.add_argument('--base-dir', type=str, default='printer-timelapses',
                       help='Base directory containing images')
    parser.add_argument('--labels-file', type=str, default='data/labels.json',
                       help='Path to labels JSON file')
    
    args = parser.parse_args()
    
    random_sample = not args.sequential
    
    labeler = ImageLabeler(
        base_dir=args.base_dir,
        labels_file=args.labels_file,
        sample_size=args.sample_size,
        random_sample=random_sample
    )
    
    labeler.start()

