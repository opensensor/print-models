#!/usr/bin/env python3
"""
Export labeled images to a versioned dataset directory for Git LFS.

This script copies labeled images from the printer-timelapses symlink
to a structured dataset directory that can be version controlled.
"""

import json
import shutil
import argparse
from pathlib import Path
from datetime import datetime
from collections import Counter


def export_dataset(labels_file, output_dir, version, description, dataset_type="offline-detection"):
    """
    Export labeled images to a versioned dataset directory.
    
    Args:
        labels_file: Path to labels JSON file
        output_dir: Output directory for dataset
        version: Version string (e.g., "1.0", "2.0")
        description: Description of this dataset version
        dataset_type: Type of dataset ("offline-detection" or "failed-print-detection")
    """
    # Load labels
    with open(labels_file, 'r') as f:
        labels = json.load(f)
    
    print(f"Loaded {len(labels)} labeled images from {labels_file}")
    
    # Create output directory structure
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Determine class names based on dataset type
    if dataset_type == "offline-detection":
        class_map = {
            'active': 'active',
            'offline': 'offline',
            1: 'active',  # Handle numeric labels
            0: 'offline'
        }
    elif dataset_type == "failed-print-detection":
        class_map = {
            'good': 'good',
            'failed': 'failed',
            0: 'good',  # Handle numeric labels
            1: 'failed'
        }
    else:
        raise ValueError(f"Unknown dataset type: {dataset_type}")
    
    # Create class directories
    class_dirs = {}
    for class_name in set(class_map.values()):
        class_dir = output_path / class_name
        class_dir.mkdir(exist_ok=True)
        class_dirs[class_name] = class_dir
    
    # Copy images to class directories
    copied_count = 0
    skipped_count = 0
    class_counts = Counter()
    
    for img_path_str, label in labels.items():
        img_path = Path(img_path_str)
        
        # Check if image exists
        if not img_path.exists():
            print(f"Warning: Image not found: {img_path}")
            skipped_count += 1
            continue
        
        # Get class name
        class_name = class_map.get(label)
        if class_name is None:
            print(f"Warning: Unknown label '{label}' for {img_path}")
            skipped_count += 1
            continue
        
        # Copy image to class directory
        dest_path = class_dirs[class_name] / img_path.name
        shutil.copy2(img_path, dest_path)
        copied_count += 1
        class_counts[class_name] += 1
    
    print(f"\nCopied {copied_count} images to {output_path}")
    print(f"Skipped {skipped_count} images")
    
    # Save labels.json to dataset directory
    labels_output = output_path / "labels.json"
    with open(labels_output, 'w') as f:
        json.dump(labels, f, indent=2)
    print(f"Saved labels to {labels_output}")
    
    # Generate README.md
    readme_path = output_path / "README.md"
    generate_readme(
        readme_path,
        version=version,
        description=description,
        total_images=copied_count,
        class_counts=class_counts,
        dataset_type=dataset_type,
        source_labels=labels_file
    )
    print(f"Generated README at {readme_path}")
    
    # Generate dataset_info.json for programmatic access
    info_path = output_path / "dataset_info.json"
    dataset_info = {
        "version": version,
        "description": description,
        "created": datetime.now().isoformat(),
        "total_images": copied_count,
        "classes": dict(class_counts),
        "dataset_type": dataset_type,
        "source_labels": str(labels_file)
    }
    with open(info_path, 'w') as f:
        json.dump(dataset_info, f, indent=2)
    print(f"Generated dataset info at {info_path}")
    
    return copied_count, class_counts


def generate_readme(output_path, version, description, total_images, class_counts, dataset_type, source_labels):
    """Generate README.md for the dataset."""
    
    # Calculate percentages
    class_percentages = {
        class_name: (count / total_images * 100) if total_images > 0 else 0
        for class_name, count in class_counts.items()
    }
    
    # Determine dataset title
    if dataset_type == "offline-detection":
        title = "Offline Detection Dataset"
    elif dataset_type == "failed-print-detection":
        title = "Failed Print Detection Dataset"
    else:
        title = "Dataset"
    
    readme_content = f"""# {title} v{version}

**Created:** {datetime.now().strftime('%Y-%m-%d')}
**Total Images:** {total_images}
**Description:** {description}

## Classes

"""
    
    for class_name in sorted(class_counts.keys()):
        count = class_counts[class_name]
        percentage = class_percentages[class_name]
        readme_content += f"- **{class_name.capitalize()}:** {count} images ({percentage:.1f}%)\n"
    
    readme_content += f"""

## Directory Structure

```
{output_path.name}/
"""
    
    for class_name in sorted(class_counts.keys()):
        count = class_counts[class_name]
        readme_content += f"├── {class_name}/          # {count} images\n"
    
    readme_content += f"""├── labels.json       # Original labels file
├── dataset_info.json # Dataset metadata
└── README.md         # This file
```

## Source

- **Labels File:** `{source_labels}`
- **Images:** Copied from printer timelapse storage

## Usage

### Training with this dataset

```python
# Load dataset
from pathlib import Path
import json

dataset_dir = Path("{output_path.name}")
with open(dataset_dir / "dataset_info.json") as f:
    info = json.load(f)

print(f"Dataset version: {{info['version']}}")
print(f"Total images: {{info['total_images']}}")
print(f"Classes: {{info['classes']}}")
```

### Training script

```bash
# Train model on this specific dataset version
python src/train_model.py \\
    --dataset-dir {output_path} \\
    --epochs 20 \\
    --batch-size 32
```

## Model Performance

*To be filled in after training*

- **Model:** ResNet18 transfer learning
- **Validation Accuracy:** TBD
- **Training Date:** TBD
- **Model File:** `models/versions/{dataset_type.replace('-', '_')}_v{version}.pth`

## Notes

- Images are stored in class subdirectories for easy loading with PyTorch ImageFolder
- Original labels.json preserved for reference
- All images are 1920x1080 JPEG format from printer timelapse camera

## Version History

### v{version} ({datetime.now().strftime('%Y-%m-%d')})
- {description}
"""
    
    with open(output_path, 'w') as f:
        f.write(readme_content)


def main():
    parser = argparse.ArgumentParser(
        description="Export labeled images to a versioned dataset directory"
    )
    parser.add_argument(
        '--labels-file',
        type=str,
        required=True,
        help='Path to labels JSON file'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        required=True,
        help='Output directory for dataset'
    )
    parser.add_argument(
        '--version',
        type=str,
        required=True,
        help='Dataset version (e.g., "1.0", "2.0")'
    )
    parser.add_argument(
        '--description',
        type=str,
        required=True,
        help='Description of this dataset version'
    )
    parser.add_argument(
        '--dataset-type',
        type=str,
        choices=['offline-detection', 'failed-print-detection'],
        default='offline-detection',
        help='Type of dataset'
    )
    
    args = parser.parse_args()
    
    print("="*60)
    print(f"Exporting Dataset v{args.version}")
    print("="*60)
    print(f"Type: {args.dataset_type}")
    print(f"Labels: {args.labels_file}")
    print(f"Output: {args.output_dir}")
    print(f"Description: {args.description}")
    print("="*60)
    print()
    
    copied_count, class_counts = export_dataset(
        labels_file=args.labels_file,
        output_dir=args.output_dir,
        version=args.version,
        description=args.description,
        dataset_type=args.dataset_type
    )
    
    print()
    print("="*60)
    print("✓ Dataset export complete!")
    print("="*60)
    print(f"Total images: {copied_count}")
    for class_name, count in sorted(class_counts.items()):
        print(f"  {class_name}: {count}")
    print()
    print("Next steps:")
    print("1. Review the generated README.md")
    print("2. Add to Git LFS: git add " + args.output_dir)
    print("3. Commit: git commit -m 'Add dataset v" + args.version + "'")
    print("="*60)


if __name__ == "__main__":
    main()

