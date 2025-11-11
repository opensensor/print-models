#!/usr/bin/env python3
"""
Label images from candidate list (likely active images).
This helps balance the dataset by focusing on active examples.
"""

import json
from pathlib import Path
import sys

# Import the labeling tool
from label_images import ImageLabeler


def load_candidates(candidates_file="data/active_candidates.txt"):
    """Load candidate images from file."""
    candidates = []
    
    with open(candidates_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                # Parse: "Seq 0 (len=44) | path"
                parts = line.split('|')
                if len(parts) >= 2:
                    img_path = parts[1].strip()
                    candidates.append(Path(img_path))
    
    return candidates


def expand_candidates_with_neighbors(candidates, window=10):
    """
    Expand candidate list to include neighboring images.
    Since active images appear in sequences, neighbors are likely active too.
    """
    expanded = set()
    
    for img_path in candidates:
        # Add the candidate itself
        expanded.add(img_path)
        
        # Get all images in the same directory
        date_dir = img_path.parent
        all_images = sorted(date_dir.glob("*.jpg"))
        
        # Find the index of current image
        try:
            idx = all_images.index(img_path)
            
            # Add neighbors within window
            start_idx = max(0, idx - window)
            end_idx = min(len(all_images), idx + window + 1)
            
            for i in range(start_idx, end_idx):
                expanded.add(all_images[i])
        except ValueError:
            continue
    
    return sorted(expanded)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Label candidate active images")
    parser.add_argument('--candidates-file', type=str, default='data/active_candidates.txt',
                       help='Path to candidates file')
    parser.add_argument('--labels-file', type=str, default='data/labels.json',
                       help='Path to labels JSON file')
    parser.add_argument('--expand-window', type=int, default=10,
                       help='Number of neighboring images to include (0 = only candidates)')
    parser.add_argument('--sample-size', type=int, default=50,
                       help='Maximum number of images to label in this session')
    
    args = parser.parse_args()
    
    # Load candidates
    print("Loading candidates...")
    candidates = load_candidates(args.candidates_file)
    print(f"Found {len(candidates)} candidate images")
    
    # Expand with neighbors if requested
    if args.expand_window > 0:
        print(f"Expanding with ±{args.expand_window} neighbors...")
        candidates = expand_candidates_with_neighbors(candidates, args.expand_window)
        print(f"Expanded to {len(candidates)} images")
    
    # Load existing labels to filter
    labels_file = Path(args.labels_file)
    if labels_file.exists():
        with open(labels_file, 'r') as f:
            existing_labels = json.load(f)
        labeled_set = set(existing_labels.keys())
    else:
        labeled_set = set()
    
    # Filter unlabeled
    unlabeled = [img for img in candidates if str(img) not in labeled_set]
    print(f"Unlabeled candidates: {len(unlabeled)}")
    
    if not unlabeled:
        print("\nAll candidates are already labeled!")
        sys.exit(0)
    
    # Limit to sample size
    to_label = unlabeled[:args.sample_size]
    
    print(f"\nWill label {len(to_label)} images from active sequences")
    print("These are likely to be ACTIVE images, but verify each one!")
    print("")
    
    # Create a custom labeler with our specific image list
    class CandidateLabeler(ImageLabeler):
        def __init__(self, images_to_label, labels_file):
            self.base_dir = Path(".")
            self.labels_file = Path(labels_file)
            self.labels = self.load_labels()
            self.all_images = images_to_label
            self.images_to_label = images_to_label
            self.current_idx = 0
            self.fig = None
            self.ax = None
    
    labeler = CandidateLabeler(to_label, args.labels_file)
    labeler.start()

