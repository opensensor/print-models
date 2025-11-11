#!/usr/bin/env python3
"""
Interactive labeling tool for failed print detection.
Labels active printing images as 'good' or 'failed'.
"""

import json
import os
import sys
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.widgets import Button
import argparse


class FailedPrintLabeler:
    def __init__(self, image_list_file, labels_file="data/failed_print_labels.json", start_index=0):
        """
        Initialize the labeler.
        
        Args:
            image_list_file: Path to file containing list of active images
            labels_file: Path to save labels JSON
            start_index: Index to start labeling from
        """
        self.labels_file = labels_file
        self.start_index = start_index
        
        # Load image list
        with open(image_list_file, 'r') as f:
            self.image_paths = [line.strip() for line in f if line.strip()]
        
        print(f"Loaded {len(self.image_paths)} active images")
        
        # Load existing labels if they exist
        self.labels = {}
        if os.path.exists(labels_file):
            with open(labels_file, 'r') as f:
                self.labels = json.load(f)
            print(f"Loaded {len(self.labels)} existing labels")
        
        # Filter to unlabeled images or start from specified index
        if start_index > 0:
            self.current_index = start_index
        else:
            # Find first unlabeled image
            self.current_index = 0
            for i, path in enumerate(self.image_paths):
                if path not in self.labels:
                    self.current_index = i
                    break
        
        print(f"Starting at index {self.current_index}")
        
        # Setup matplotlib
        self.fig, self.ax = plt.subplots(figsize=(12, 8))
        self.fig.canvas.manager.set_window_title('Failed Print Labeler')
        plt.subplots_adjust(bottom=0.15)
        
        # Create buttons
        button_width = 0.12
        button_height = 0.05
        button_y = 0.05
        
        ax_good = plt.axes([0.2, button_y, button_width, button_height])
        ax_failed = plt.axes([0.35, button_y, button_width, button_height])
        ax_skip = plt.axes([0.5, button_y, button_width, button_height])
        ax_back = plt.axes([0.65, button_y, button_width, button_height])
        ax_quit = plt.axes([0.8, button_y, button_width, button_height])
        
        self.btn_good = Button(ax_good, 'Good (G)', color='lightgreen')
        self.btn_failed = Button(ax_failed, 'Failed (F)', color='lightcoral')
        self.btn_skip = Button(ax_skip, 'Skip (S)', color='lightyellow')
        self.btn_back = Button(ax_back, 'Back (B)', color='lightblue')
        self.btn_quit = Button(ax_quit, 'Quit (Q)', color='lightgray')
        
        self.btn_good.on_clicked(lambda event: self.label_image('good'))
        self.btn_failed.on_clicked(lambda event: self.label_image('failed'))
        self.btn_skip.on_clicked(lambda event: self.skip_image())
        self.btn_back.on_clicked(lambda event: self.go_back())
        self.btn_quit.on_clicked(lambda event: self.quit())
        
        # Connect keyboard events
        self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)
        
        # Display first image
        self.display_current_image()
    
    def display_current_image(self):
        """Display the current image with metadata."""
        self.ax.clear()
        
        if self.current_index >= len(self.image_paths):
            self.ax.text(0.5, 0.5, 'All images labeled!', 
                        ha='center', va='center', fontsize=20)
            self.ax.set_xlim(0, 1)
            self.ax.set_ylim(0, 1)
            self.ax.axis('off')
            plt.draw()
            return
        
        img_path = self.image_paths[self.current_index]
        
        # Check if image exists
        if not os.path.exists(img_path):
            print(f"Warning: Image not found: {img_path}")
            self.skip_image()
            return
        
        # Load and display image
        try:
            img = mpimg.imread(img_path)
            self.ax.imshow(img)
            self.ax.axis('off')
            
            # Get existing label if any
            existing_label = self.labels.get(img_path, "unlabeled")
            
            # Count labels
            good_count = sum(1 for v in self.labels.values() if v == 'good')
            failed_count = sum(1 for v in self.labels.values() if v == 'failed')
            
            # Display info
            filename = os.path.basename(img_path)
            title = f"Image {self.current_index + 1}/{len(self.image_paths)}\n"
            title += f"{filename}\n"
            title += f"Current: {existing_label} | Total: {good_count} good, {failed_count} failed"
            
            self.ax.set_title(title, fontsize=12, pad=10)
            
            plt.draw()
        except Exception as e:
            print(f"Error loading image {img_path}: {e}")
            self.skip_image()
    
    def label_image(self, label):
        """Label the current image."""
        if self.current_index >= len(self.image_paths):
            return
        
        img_path = self.image_paths[self.current_index]
        self.labels[img_path] = label
        
        # Save labels
        self.save_labels()
        
        # Move to next image
        self.current_index += 1
        self.display_current_image()
    
    def skip_image(self):
        """Skip the current image."""
        self.current_index += 1
        self.display_current_image()
    
    def go_back(self):
        """Go back to previous image."""
        if self.current_index > 0:
            self.current_index -= 1
            self.display_current_image()
    
    def quit(self):
        """Save and quit."""
        self.save_labels()
        print(f"\nLabeling session complete!")
        print(f"Labeled {len(self.labels)} images")
        print(f"Labels saved to: {self.labels_file}")
        plt.close()
    
    def save_labels(self):
        """Save labels to JSON file."""
        os.makedirs(os.path.dirname(self.labels_file), exist_ok=True)
        with open(self.labels_file, 'w') as f:
            json.dump(self.labels, f, indent=2)
    
    def on_key_press(self, event):
        """Handle keyboard shortcuts."""
        if event.key == 'g':
            self.label_image('good')
        elif event.key == 'f':
            self.label_image('failed')
        elif event.key == 's':
            self.skip_image()
        elif event.key == 'b':
            self.go_back()
        elif event.key == 'q':
            self.quit()
    
    def run(self):
        """Start the labeling interface."""
        plt.show()


def main():
    parser = argparse.ArgumentParser(description='Label active images as good or failed prints')
    parser.add_argument('--image-list', type=str, default='data/active_images.txt',
                       help='Path to file containing list of active images')
    parser.add_argument('--labels-file', type=str, default='data/failed_print_labels.json',
                       help='Path to save labels JSON')
    parser.add_argument('--start-index', type=int, default=0,
                       help='Index to start labeling from')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.image_list):
        print(f"Error: Image list file not found: {args.image_list}")
        print("Run inference first to generate the active images list.")
        sys.exit(1)
    
    print("=== Failed Print Labeler ===")
    print("Instructions:")
    print("  G or click 'Good' - Label as good print")
    print("  F or click 'Failed' - Label as failed print")
    print("  S or click 'Skip' - Skip this image")
    print("  B or click 'Back' - Go back to previous image")
    print("  Q or click 'Quit' - Save and quit")
    print()
    
    labeler = FailedPrintLabeler(args.image_list, args.labels_file, args.start_index)
    labeler.run()


if __name__ == '__main__':
    main()

