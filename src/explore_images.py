#!/usr/bin/env python3
"""
Data exploration script for 3D printer timelapse images.
Visualizes random samples to understand printer-offline vs active patterns.
"""

import os
import random
from pathlib import Path
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np


def get_all_images(base_dir="printer-timelapses"):
    """Recursively find all image files."""
    base_path = Path(base_dir)
    image_extensions = {'.jpg', '.jpeg', '.png'}
    
    images = []
    for ext in image_extensions:
        images.extend(base_path.rglob(f'*{ext}'))
        images.extend(base_path.rglob(f'*{ext.upper()}'))
    
    return sorted(images)


def visualize_random_samples(num_samples=12, base_dir="printer-timelapses"):
    """Display a grid of random images from the dataset."""
    all_images = get_all_images(base_dir)
    
    if not all_images:
        print(f"No images found in {base_dir}")
        return
    
    print(f"Found {len(all_images)} total images")
    
    # Sample random images
    sample_images = random.sample(all_images, min(num_samples, len(all_images)))
    
    # Create grid
    rows = 3
    cols = 4
    fig, axes = plt.subplots(rows, cols, figsize=(16, 12))
    fig.suptitle('Random Sample of Timelapse Images', fontsize=16)
    
    for idx, (ax, img_path) in enumerate(zip(axes.flat, sample_images)):
        try:
            img = Image.open(img_path)
            ax.imshow(img)
            ax.set_title(f"{img_path.parent.name}/{img_path.name}", fontsize=8)
            ax.axis('off')
        except Exception as e:
            ax.text(0.5, 0.5, f"Error loading\n{img_path.name}", 
                   ha='center', va='center')
            ax.axis('off')
    
    # Hide any unused subplots
    for idx in range(len(sample_images), rows * cols):
        axes.flat[idx].axis('off')
    
    plt.tight_layout()
    plt.savefig('data/sample_exploration.png', dpi=150, bbox_inches='tight')
    print(f"Saved visualization to data/sample_exploration.png")
    plt.show()


def analyze_image_statistics(base_dir="printer-timelapses"):
    """Analyze basic statistics about the images."""
    all_images = get_all_images(base_dir)
    
    if not all_images:
        print(f"No images found in {base_dir}")
        return
    
    print(f"\n=== Image Dataset Statistics ===")
    print(f"Total images: {len(all_images)}")
    
    # Group by date
    by_date = {}
    for img_path in all_images:
        date = img_path.parent.name
        by_date[date] = by_date.get(date, 0) + 1
    
    print(f"\nImages by date:")
    for date in sorted(by_date.keys()):
        print(f"  {date}: {by_date[date]} images")
    
    # Sample a few images to check dimensions and file sizes
    sample_size = min(100, len(all_images))
    sample = random.sample(all_images, sample_size)
    
    sizes = []
    dimensions = []
    
    for img_path in sample:
        try:
            sizes.append(img_path.stat().st_size / 1024)  # KB
            with Image.open(img_path) as img:
                dimensions.append(img.size)
        except Exception as e:
            print(f"Error reading {img_path}: {e}")
    
    if sizes:
        print(f"\nFile size statistics (KB):")
        print(f"  Mean: {np.mean(sizes):.1f}")
        print(f"  Min: {np.min(sizes):.1f}")
        print(f"  Max: {np.max(sizes):.1f}")
    
    if dimensions:
        unique_dims = set(dimensions)
        print(f"\nImage dimensions:")
        for dim in unique_dims:
            count = dimensions.count(dim)
            print(f"  {dim[0]}x{dim[1]}: {count} images")


def visualize_temporal_sequence(date="20251110", start_idx=0, num_images=12, base_dir="printer-timelapses"):
    """Visualize a temporal sequence of images from a specific date."""
    date_dir = Path(base_dir) / date
    
    if not date_dir.exists():
        print(f"Date directory {date_dir} not found")
        return
    
    images = sorted(date_dir.glob('*.jpg')) + sorted(date_dir.glob('*.png'))
    
    if not images:
        print(f"No images found in {date_dir}")
        return
    
    print(f"Found {len(images)} images for {date}")
    
    # Select sequence
    end_idx = min(start_idx + num_images, len(images))
    sequence = images[start_idx:end_idx]
    
    # Create grid
    rows = 3
    cols = 4
    fig, axes = plt.subplots(rows, cols, figsize=(16, 12))
    fig.suptitle(f'Temporal Sequence - {date} (images {start_idx}-{end_idx-1})', fontsize=16)
    
    for idx, (ax, img_path) in enumerate(zip(axes.flat, sequence)):
        try:
            img = Image.open(img_path)
            ax.imshow(img)
            ax.set_title(img_path.name, fontsize=8)
            ax.axis('off')
        except Exception as e:
            ax.text(0.5, 0.5, f"Error loading\n{img_path.name}", 
                   ha='center', va='center')
            ax.axis('off')
    
    # Hide any unused subplots
    for idx in range(len(sequence), rows * cols):
        axes.flat[idx].axis('off')
    
    plt.tight_layout()
    plt.savefig(f'data/temporal_sequence_{date}_{start_idx}.png', dpi=150, bbox_inches='tight')
    print(f"Saved visualization to data/temporal_sequence_{date}_{start_idx}.png")
    plt.show()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Explore 3D printer timelapse images")
    parser.add_argument('--mode', choices=['random', 'stats', 'temporal'], default='stats',
                       help='Exploration mode')
    parser.add_argument('--num-samples', type=int, default=12,
                       help='Number of samples to visualize')
    parser.add_argument('--date', type=str, default='20251110',
                       help='Date for temporal sequence visualization')
    parser.add_argument('--start-idx', type=int, default=0,
                       help='Starting index for temporal sequence')
    parser.add_argument('--base-dir', type=str, default='printer-timelapses',
                       help='Base directory containing images')
    
    args = parser.parse_args()
    
    if args.mode == 'stats':
        analyze_image_statistics(args.base_dir)
    elif args.mode == 'random':
        visualize_random_samples(args.num_samples, args.base_dir)
    elif args.mode == 'temporal':
        visualize_temporal_sequence(args.date, args.start_idx, args.num_samples, args.base_dir)

