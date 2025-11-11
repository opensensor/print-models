#!/usr/bin/env python3
"""
Real-time print monitoring script.
Polls for new images and classifies them using both models:
1. Printer offline detection
2. Failed print detection (if active)
"""

import os
import sys
import time
import json
from pathlib import Path
from datetime import datetime
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import argparse


class PrintMonitor:
    def __init__(self, 
                 image_dir,
                 offline_model_path='models/printer_offline_detector.pth',
                 failed_model_path='models/failed_print_detector.pth',
                 poll_interval=30,
                 offline_threshold=0.7,
                 failed_threshold=0.6):
        """
        Initialize the print monitor.
        
        Args:
            image_dir: Directory to monitor for new images
            offline_model_path: Path to printer offline detection model
            failed_model_path: Path to failed print detection model
            poll_interval: Seconds between checks for new images
            offline_threshold: Confidence threshold for "active" classification
            failed_threshold: Confidence threshold for "failed" classification
        """
        self.image_dir = Path(image_dir)
        self.poll_interval = poll_interval
        self.offline_threshold = offline_threshold
        self.failed_threshold = failed_threshold
        
        # Track processed images
        self.processed_images = set()
        self.state_file = Path('data/monitor_state.json')
        self.load_state()
        
        # Setup device
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"Using device: {self.device}")
        
        # Load models
        print("Loading models...")
        self.offline_model = self.load_model(offline_model_path)
        self.failed_model = self.load_model(failed_model_path) if Path(failed_model_path).exists() else None
        
        if self.failed_model is None:
            print("⚠️  Failed print model not found. Only offline detection will be used.")
        
        # Image transforms
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        print(f"Monitoring directory: {self.image_dir}")
        print(f"Poll interval: {self.poll_interval} seconds")
        print(f"Offline threshold: {self.offline_threshold}")
        print(f"Failed threshold: {self.failed_threshold}")
        print()
    
    def load_model(self, model_path):
        """Load a trained model."""
        if not Path(model_path).exists():
            return None
        
        # Create model architecture
        model = models.resnet18(pretrained=False)
        num_features = model.fc.in_features
        model.fc = nn.Linear(num_features, 2)
        
        # Load weights
        checkpoint = torch.load(model_path, map_location=self.device)
        model.load_state_dict(checkpoint['model_state_dict'])
        model = model.to(self.device)
        model.eval()
        
        return model
    
    def load_state(self):
        """Load previously processed images from state file."""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                state = json.load(f)
                self.processed_images = set(state.get('processed_images', []))
            print(f"Loaded state: {len(self.processed_images)} previously processed images")
    
    def save_state(self):
        """Save processed images to state file."""
        os.makedirs(self.state_file.parent, exist_ok=True)
        with open(self.state_file, 'w') as f:
            json.dump({
                'processed_images': list(self.processed_images),
                'last_update': datetime.now().isoformat()
            }, f, indent=2)
    
    def classify_image(self, image_path, model):
        """Classify a single image."""
        try:
            image = Image.open(image_path).convert('RGB')
            image_tensor = self.transform(image).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                outputs = model(image_tensor)
                probabilities = torch.nn.functional.softmax(outputs, dim=1)
                confidence, predicted = torch.max(probabilities, 1)
            
            return predicted.item(), confidence.item()
        except Exception as e:
            print(f"Error classifying {image_path}: {e}")
            return None, None
    
    def get_new_images(self):
        """Find new images that haven't been processed."""
        if not self.image_dir.exists():
            return []
        
        # Find all jpg/png images
        all_images = []
        for ext in ['*.jpg', '*.jpeg', '*.png']:
            all_images.extend(self.image_dir.glob(ext))
        
        # Filter to new images only
        new_images = [img for img in all_images if str(img) not in self.processed_images]
        
        # Sort by modification time (oldest first)
        new_images.sort(key=lambda x: x.stat().st_mtime)
        
        return new_images
    
    def format_timestamp(self, image_path):
        """Extract timestamp from image filename or use modification time."""
        filename = image_path.stem
        
        # Try to parse timestamp from filename (format: 20251110T123456)
        try:
            if 'T' in filename:
                date_part, time_part = filename.split('T')
                year = date_part[:4]
                month = date_part[4:6]
                day = date_part[6:8]
                hour = time_part[:2]
                minute = time_part[2:4]
                second = time_part[4:6]
                return f"{year}-{month}-{day} {hour}:{minute}:{second}"
        except:
            pass
        
        # Fallback to modification time
        mtime = image_path.stat().st_mtime
        return datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
    

    def run(self):
        """Main monitoring loop - tail -f style."""
        print("=" * 60)
        print("🖨️  PRINT MONITOR STARTED")
        print("=" * 60)
        print(f"Monitoring: {self.image_dir}")
        print(f"Polling every {self.poll_interval} seconds...")
        print("Press Ctrl+C to stop")
        print("=" * 60)
        print()

        last_status = None

        try:
            while True:
                # Check for new images
                new_images = self.get_new_images()

                if new_images:
                    for image_path in new_images:
                        # Process and display inline (tail -f style)
                        timestamp = self.format_timestamp(image_path)
                        filename = image_path.name

                        # Stage 1: Offline detection
                        offline_pred, offline_conf = self.classify_image(image_path, self.offline_model)

                        if offline_pred is None:
                            continue

                        is_active = offline_pred == 1 and offline_conf >= self.offline_threshold

                        # Only print status changes or active prints
                        if is_active:
                            # Stage 2: Failed print detection
                            if self.failed_model is not None:
                                failed_pred, failed_conf = self.classify_image(image_path, self.failed_model)

                                if failed_pred is not None:
                                    is_failed = failed_pred == 1 and failed_conf >= self.failed_threshold

                                    if is_failed:
                                        print(f"🚨 [{timestamp}] {filename}")
                                        print(f"   ⚠️  FAILED PRINT DETECTED! (confidence: {failed_conf:.1%})")
                                        print(f"   🔔 CHECK YOUR PRINTER NOW!")
                                        print()
                                    else:
                                        print(f"🟢 [{timestamp}] {filename} - Print OK (good: {1-failed_conf:.1%})")
                                else:
                                    print(f"🟢 [{timestamp}] {filename} - Active")
                            else:
                                print(f"🟢 [{timestamp}] {filename} - Active (offline conf: {offline_conf:.1%})")

                            last_status = "active"
                        else:
                            # Only print offline status if it changed from active
                            if last_status == "active":
                                print(f"⚫ [{timestamp}] {filename} - Printer went offline")
                                last_status = "offline"

                        # Mark as processed
                        self.processed_images.add(str(image_path))

                    # Save state after processing
                    self.save_state()

                # Wait for next poll
                time.sleep(self.poll_interval)

        except KeyboardInterrupt:
            print()
            print("=" * 60)
            print("🛑 MONITOR STOPPED")
            print("=" * 60)
            print(f"Total images processed: {len(self.processed_images)}")
            self.save_state()
            print("State saved.")


def main():
    parser = argparse.ArgumentParser(description='Monitor printer for new images and classify them')
    parser.add_argument('--image-dir', type=str, required=True,
                       help='Directory to monitor for new images (e.g., printer-timelapses/20251110)')
    parser.add_argument('--offline-model', type=str, default='models/printer_offline_detector.pth',
                       help='Path to offline detection model')
    parser.add_argument('--failed-model', type=str, default='models/failed_print_detector.pth',
                       help='Path to failed print detection model')
    parser.add_argument('--interval', type=int, default=30,
                       help='Poll interval in seconds (default: 30)')
    parser.add_argument('--offline-threshold', type=float, default=0.7,
                       help='Confidence threshold for active classification (default: 0.7)')
    parser.add_argument('--failed-threshold', type=float, default=0.6,
                       help='Confidence threshold for failed classification (default: 0.6)')
    parser.add_argument('--reset', action='store_true',
                       help='Reset state and process all images from scratch')
    
    args = parser.parse_args()
    
    # Reset state if requested
    if args.reset:
        state_file = Path('data/monitor_state.json')
        if state_file.exists():
            state_file.unlink()
            print("State reset. Will process all images.")
    
    # Create and run monitor
    monitor = PrintMonitor(
        image_dir=args.image_dir,
        offline_model_path=args.offline_model,
        failed_model_path=args.failed_model,
        poll_interval=args.interval,
        offline_threshold=args.offline_threshold,
        failed_threshold=args.failed_threshold
    )
    
    monitor.run()


if __name__ == '__main__':
    main()

