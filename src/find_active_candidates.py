#!/usr/bin/env python3
"""
Find candidate images that might show active printing.
Uses sequence detection - active images appear in continuous sequences.
"""

import json
from pathlib import Path
from PIL import Image
import numpy as np
from tqdm import tqdm


def detect_active_sequences(base_dir="printer-timelapses", min_sequence_length=10,
                           change_threshold=3.0, sample_interval=3):
    """
    Detect sequences of images with continuous changes (likely active printing).

    Active printing shows consistent small changes between consecutive frames.
    Offline periods show no changes (static images).
    """
    all_images = []
    for date_dir in sorted(Path(base_dir).iterdir()):
        if date_dir.is_dir():
            images = sorted(date_dir.glob("*.jpg"))
            all_images.extend(images)

    print(f"Analyzing {len(all_images)} images for active sequences...")
    print(f"Looking for sequences of {min_sequence_length}+ images with continuous changes...")

    # Calculate differences between consecutive images
    changes = []
    print("Calculating frame-to-frame differences...")

    for i in tqdm(range(0, len(all_images) - 1, sample_interval)):
        try:
            # Downsample for speed
            img1 = np.array(Image.open(all_images[i]).convert('L').resize((160, 90)))
            img2 = np.array(Image.open(all_images[i+1]).convert('L').resize((160, 90)))

            # Calculate mean absolute difference
            diff = np.abs(img1.astype(float) - img2.astype(float)).mean()
            changes.append((i, diff))
        except Exception as e:
            changes.append((i, 0))

    # Find sequences where there are consistent changes
    print("\nDetecting active sequences...")
    sequences = []
    current_sequence = []

    for idx, (i, diff) in enumerate(changes):
        if diff > change_threshold:
            # Active frame
            if not current_sequence:
                current_sequence = [i]
            else:
                # Check if continuous with previous
                if i - current_sequence[-1] <= sample_interval * 2:
                    current_sequence.append(i)
                else:
                    # Gap detected, save previous sequence if long enough
                    if len(current_sequence) >= min_sequence_length:
                        sequences.append(current_sequence)
                    current_sequence = [i]
        else:
            # Inactive frame - end sequence if we have one
            if len(current_sequence) >= min_sequence_length:
                sequences.append(current_sequence)
            current_sequence = []

    # Don't forget the last sequence
    if len(current_sequence) >= min_sequence_length:
        sequences.append(current_sequence)

    print(f"\nFound {len(sequences)} active sequences")

    # Convert to actual image paths and get representative samples
    sequence_info = []
    for seq_idx, seq in enumerate(sequences):
        start_idx = seq[0]
        end_idx = seq[-1]
        length = len(seq)

        # Get start, middle, and end images from sequence
        mid_idx = seq[len(seq)//2]

        sequence_info.append({
            'sequence_id': seq_idx,
            'start_image': all_images[start_idx],
            'mid_image': all_images[mid_idx],
            'end_image': all_images[end_idx],
            'length': length,
            'indices': seq
        })

    return sequence_info, all_images


def get_sample_images_from_sequences(sequences, all_images, samples_per_sequence=3):
    """Get representative sample images from each sequence."""
    candidates = []

    for seq_info in sequences:
        # Sample from beginning, middle, and end of each sequence
        seq_indices = seq_info['indices']
        length = len(seq_indices)

        # Get evenly spaced samples
        if length >= samples_per_sequence:
            step = length // samples_per_sequence
            sample_positions = [seq_indices[i * step] for i in range(samples_per_sequence)]
        else:
            sample_positions = seq_indices

        for pos in sample_positions:
            candidates.append({
                'image': all_images[pos],
                'sequence_id': seq_info['sequence_id'],
                'sequence_length': length
            })

    return candidates


def filter_unlabeled(candidates, labels_file="data/labels.json"):
    """Filter out already labeled images."""
    if Path(labels_file).exists():
        with open(labels_file, 'r') as f:
            labels = json.load(f)
        labeled_set = set(labels.keys())
    else:
        labeled_set = set()

    unlabeled = [c for c in candidates if str(c['image']) not in labeled_set]
    return unlabeled


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Find candidate active images using sequence detection")
    parser.add_argument('--base-dir', type=str, default='printer-timelapses')
    parser.add_argument('--labels-file', type=str, default='data/labels.json')
    parser.add_argument('--output', type=str, default='data/active_candidates.txt')
    parser.add_argument('--min-sequence-length', type=int, default=10,
                       help='Minimum number of changing frames to consider a sequence')
    parser.add_argument('--change-threshold', type=float, default=3.0,
                       help='Threshold for detecting frame changes')
    parser.add_argument('--samples-per-sequence', type=int, default=3,
                       help='Number of sample images to take from each sequence')

    args = parser.parse_args()

    # Detect active sequences
    sequences, all_images = detect_active_sequences(
        args.base_dir,
        min_sequence_length=args.min_sequence_length,
        change_threshold=args.change_threshold
    )

    if not sequences:
        print("\nNo active sequences found. Try adjusting --change-threshold or --min-sequence-length")
        exit(0)

    # Get sample images from sequences
    candidates = get_sample_images_from_sequences(sequences, all_images, args.samples_per_sequence)

    print(f"\nExtracted {len(candidates)} sample images from {len(sequences)} sequences")

    # Filter unlabeled
    unlabeled = filter_unlabeled(candidates, args.labels_file)

    print(f"Found {len(unlabeled)} unlabeled candidates")

    # Save candidates
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, 'w') as f:
        f.write("# Candidate active images from detected sequences\n")
        f.write("# Format: sequence_id | sequence_length | path\n\n")
        for c in unlabeled:
            f.write(f"Seq {c['sequence_id']:3d} (len={c['sequence_length']:4d}) | {c['image']}\n")

    print(f"Saved {len(unlabeled)} candidates to {args.output}")

    # Show sequence summary
    print(f"\n=== Sequence Summary ===")
    for i, seq_info in enumerate(sequences[:10]):  # Show first 10
        start_img = seq_info['start_image']
        print(f"Sequence {i}: {seq_info['length']} frames - {start_img.parent.name}/{start_img.name}")

    if len(sequences) > 10:
        print(f"... and {len(sequences) - 10} more sequences")

