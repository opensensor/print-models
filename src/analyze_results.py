#!/usr/bin/env python3
"""
Analyze labeling and prediction results.
Provides statistics and visualizations to understand model performance.
"""

import json
from pathlib import Path
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np


def analyze_labels(labels_file="data/labels.json", label_type="printer-offline"):
    """Analyze the labeled dataset."""
    if not Path(labels_file).exists():
        print(f"Labels file not found: {labels_file}")
        return None

    with open(labels_file, 'r') as f:
        labels = json.load(f)

    print(f"\n=== {label_type.title()} Label Analysis ===")
    print(f"Total labeled images: {len(labels)}")

    label_counts = Counter(labels.values())
    for label, count in sorted(label_counts.items()):
        percentage = 100 * count / len(labels)
        print(f"  {label}: {count} ({percentage:.1f}%)")

    # Check balance
    if len(label_counts) == 2:
        counts = list(label_counts.values())
        ratio = max(counts) / min(counts)
        print(f"\nClass balance ratio: {ratio:.2f}:1")
        if ratio > 3:
            print("  ⚠️  Warning: Classes are imbalanced. Consider labeling more examples of the minority class.")
        else:
            print("  ✓ Classes are reasonably balanced.")

    # Group by date (if paths contain dates)
    by_date = {}
    for img_path in labels.keys():
        path = Path(img_path)
        # Try to extract date from path
        if len(path.parts) > 1:
            date = path.parent.name
            by_date[date] = by_date.get(date, 0) + 1

    if by_date:
        print(f"\nLabeled images by date:")
        for date in sorted(by_date.keys()):
            print(f"  {date}: {by_date[date]} images")
    
    return labels


def analyze_predictions(predictions_file="data/predictions.json"):
    """Analyze model predictions."""
    if not Path(predictions_file).exists():
        print(f"Predictions file not found: {predictions_file}")
        return None
    
    with open(predictions_file, 'r') as f:
        predictions = json.load(f)
    
    print("\n=== Prediction Analysis ===")
    print(f"Total predictions: {len(predictions)}")
    
    # Count by label
    label_counts = Counter(pred['label'] for pred in predictions.values())
    for label, count in sorted(label_counts.items()):
        percentage = 100 * count / len(predictions)
        print(f"  {label}: {count} ({percentage:.1f}%)")
    
    # Confidence statistics
    confidences = [pred['confidence'] for pred in predictions.values()]
    print(f"\nConfidence statistics:")
    print(f"  Mean: {np.mean(confidences):.3f}")
    print(f"  Median: {np.median(confidences):.3f}")
    print(f"  Min: {np.min(confidences):.3f}")
    print(f"  Max: {np.max(confidences):.3f}")
    
    # Low confidence predictions
    low_conf_threshold = 0.6
    low_conf = [p for p in predictions.values() if p['confidence'] < low_conf_threshold]
    print(f"\nLow confidence predictions (< {low_conf_threshold}): {len(low_conf)} ({100*len(low_conf)/len(predictions):.1f}%)")
    
    # Group by date
    by_date = {}
    for img_path, pred in predictions.items():
        path = Path(img_path)
        date = path.parent.name
        if date not in by_date:
            by_date[date] = {'offline': 0, 'active': 0}
        by_date[date][pred['label']] += 1
    
    print(f"\nPredictions by date:")
    for date in sorted(by_date.keys()):
        offline = by_date[date]['offline']
        active = by_date[date]['active']
        total = offline + active
        print(f"  {date}: {total} total ({offline} offline, {active} active)")
    
    return predictions


def compare_labels_predictions(labels_file="data/labels.json", 
                               predictions_file="data/predictions.json"):
    """Compare labels with predictions to estimate accuracy."""
    if not Path(labels_file).exists() or not Path(predictions_file).exists():
        print("Both labels and predictions files needed for comparison.")
        return
    
    with open(labels_file, 'r') as f:
        labels = json.load(f)
    
    with open(predictions_file, 'r') as f:
        predictions = json.load(f)
    
    # Find common images
    common_images = set(labels.keys()) & set(predictions.keys())
    
    if not common_images:
        print("\nNo common images between labels and predictions.")
        return
    
    print(f"\n=== Label vs Prediction Comparison ===")
    print(f"Common images: {len(common_images)}")
    
    correct = 0
    incorrect = 0
    confusion = {'offline': {'offline': 0, 'active': 0}, 
                'active': {'offline': 0, 'active': 0}}
    
    for img_path in common_images:
        true_label = labels[img_path]
        pred_label = predictions[img_path]['label']
        
        if true_label == pred_label:
            correct += 1
        else:
            incorrect += 1
        
        confusion[true_label][pred_label] += 1
    
    accuracy = 100 * correct / len(common_images)
    print(f"\nAccuracy on labeled data: {accuracy:.2f}% ({correct}/{len(common_images)})")
    
    print(f"\nConfusion Matrix:")
    print(f"                Predicted")
    print(f"              Offline  Active")
    print(f"True Offline  {confusion['offline']['offline']:6d}  {confusion['offline']['active']:6d}")
    print(f"     Active   {confusion['active']['offline']:6d}  {confusion['active']['active']:6d}")
    
    # Calculate per-class metrics
    if confusion['offline']['offline'] + confusion['offline']['active'] > 0:
        offline_recall = confusion['offline']['offline'] / (confusion['offline']['offline'] + confusion['offline']['active'])
        print(f"\nOffline recall: {100*offline_recall:.1f}%")
    
    if confusion['active']['active'] + confusion['active']['offline'] > 0:
        active_recall = confusion['active']['active'] / (confusion['active']['active'] + confusion['active']['offline'])
        print(f"Active recall: {100*active_recall:.1f}%")


def plot_confidence_distribution(predictions_file="data/predictions.json", 
                                 output_file="data/confidence_distribution.png"):
    """Plot confidence distribution by class."""
    if not Path(predictions_file).exists():
        print(f"Predictions file not found: {predictions_file}")
        return
    
    with open(predictions_file, 'r') as f:
        predictions = json.load(f)
    
    offline_conf = [p['confidence'] for p in predictions.values() if p['label'] == 'offline']
    active_conf = [p['confidence'] for p in predictions.values() if p['label'] == 'active']
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    
    # Histogram
    ax1.hist(offline_conf, bins=20, alpha=0.5, label='Offline', color='red')
    ax1.hist(active_conf, bins=20, alpha=0.5, label='Active', color='green')
    ax1.set_xlabel('Confidence')
    ax1.set_ylabel('Count')
    ax1.set_title('Confidence Distribution by Class')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Box plot
    ax2.boxplot([offline_conf, active_conf], labels=['Offline', 'Active'])
    ax2.set_ylabel('Confidence')
    ax2.set_title('Confidence Box Plot')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\nSaved confidence distribution plot to {output_file}")


def find_uncertain_images(predictions_file="data/predictions.json",
                         threshold=0.6,
                         output_file="data/uncertain_images.txt"):
    """Find images with low confidence predictions."""
    if not Path(predictions_file).exists():
        print(f"Predictions file not found: {predictions_file}")
        return
    
    with open(predictions_file, 'r') as f:
        predictions = json.load(f)
    
    uncertain = []
    for img_path, pred in predictions.items():
        if pred['confidence'] < threshold:
            uncertain.append((img_path, pred['label'], pred['confidence']))
    
    # Sort by confidence
    uncertain.sort(key=lambda x: x[2])
    
    print(f"\n=== Uncertain Images (confidence < {threshold}) ===")
    print(f"Found {len(uncertain)} uncertain images")
    
    # Save to file
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w') as f:
        f.write(f"# Uncertain images (confidence < {threshold})\n")
        f.write(f"# Format: confidence | label | path\n\n")
        for img_path, label, conf in uncertain:
            f.write(f"{conf:.3f} | {label:8s} | {img_path}\n")
    
    print(f"Saved list to {output_file}")
    
    # Show some examples
    if uncertain:
        print(f"\nLowest confidence predictions:")
        for img_path, label, conf in uncertain[:10]:
            print(f"  {conf:.3f} | {label:8s} | {Path(img_path).name}")
    
    return uncertain


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze labeling and prediction results")
    parser.add_argument('--labels-file', type=str, default='data/labels.json',
                       help='Path to labels JSON file')
    parser.add_argument('--predictions-file', type=str, default='data/predictions.json',
                       help='Path to predictions JSON file')
    parser.add_argument('--mode', choices=['labels', 'predictions', 'compare', 'all', 'failed-labels'],
                       default='all', help='Analysis mode')
    parser.add_argument('--plot-confidence', action='store_true',
                       help='Plot confidence distribution')
    parser.add_argument('--find-uncertain', action='store_true',
                       help='Find uncertain predictions')
    parser.add_argument('--uncertainty-threshold', type=float, default=0.6,
                       help='Threshold for uncertain predictions')
    
    args = parser.parse_args()

    if args.mode in ['labels', 'all']:
        analyze_labels(args.labels_file, label_type="printer-offline")

    if args.mode == 'failed-labels':
        analyze_labels('data/failed_print_labels.json', label_type="failed-print")

    if args.mode in ['predictions', 'all']:
        analyze_predictions(args.predictions_file)

    if args.mode in ['compare', 'all']:
        compare_labels_predictions(args.labels_file, args.predictions_file)
    
    if args.plot_confidence:
        plot_confidence_distribution(args.predictions_file)
    
    if args.find_uncertain:
        find_uncertain_images(args.predictions_file, args.uncertainty_threshold)

