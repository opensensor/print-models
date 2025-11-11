#!/usr/bin/env python3
"""
Run inference on all images to detect printer-offline vs active.
Organizes images based on predictions.
"""

import json
import shutil
from pathlib import Path
from PIL import Image
import numpy as np
from tqdm import tqdm

import torch
import torch.nn.functional as F
from torchvision import transforms, models
import torch.nn as nn


def load_model(model_path, device):
    """Load trained model from checkpoint."""
    # Create model architecture
    model = models.resnet18(pretrained=False)
    num_features = model.fc.in_features
    model.fc = nn.Linear(num_features, 2)
    
    # Load checkpoint
    checkpoint = torch.load(model_path, map_location=device)
    model.load_state_dict(checkpoint['model_state_dict'])
    model = model.to(device)
    model.eval()
    
    print(f"Loaded model from {model_path}")
    print(f"Model validation accuracy: {checkpoint.get('val_acc', 'N/A'):.2f}%")
    
    return model


def get_all_images(base_dir="printer-timelapses"):
    """Recursively find all image files."""
    base_path = Path(base_dir)
    image_extensions = {'.jpg', '.jpeg', '.png'}
    
    images = []
    for ext in image_extensions:
        images.extend(base_path.rglob(f'*{ext}'))
        images.extend(base_path.rglob(f'*{ext.upper()}'))
    
    return sorted(images)


def predict_image(model, image_path, transform, device):
    """Predict whether an image shows printer offline or active."""
    try:
        image = Image.open(image_path).convert('RGB')
        image_tensor = transform(image).unsqueeze(0).to(device)
        
        with torch.no_grad():
            outputs = model(image_tensor)
            probabilities = F.softmax(outputs, dim=1)
            confidence, predicted = probabilities.max(1)
        
        # 0 = offline, 1 = active
        label = 'offline' if predicted.item() == 0 else 'active'
        confidence_score = confidence.item()
        
        return label, confidence_score
    
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return None, 0.0


def run_inference(model_path="models/printer_offline_detector.pth",
                 base_dir="printer-timelapses",
                 output_json="data/predictions.json",
                 organize_images=False,
                 output_dir="data/organized"):
    """Run inference on all images and optionally organize them."""
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Load model
    model = load_model(model_path, device)
    
    # Define transform
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    # Get all images
    print(f"\nScanning for images in {base_dir}...")
    all_images = get_all_images(base_dir)
    print(f"Found {len(all_images)} images")
    
    # Run predictions
    predictions = {}
    offline_count = 0
    active_count = 0
    
    print("\nRunning inference...")
    for img_path in tqdm(all_images):
        label, confidence = predict_image(model, img_path, transform, device)
        
        if label:
            predictions[str(img_path)] = {
                'label': label,
                'confidence': float(confidence)
            }
            
            if label == 'offline':
                offline_count += 1
            else:
                active_count += 1
    
    # Save predictions
    Path(output_json).parent.mkdir(parents=True, exist_ok=True)
    with open(output_json, 'w') as f:
        json.dump(predictions, f, indent=2)
    
    print(f"\n=== Inference Results ===")
    print(f"Total images processed: {len(predictions)}")
    print(f"  Offline: {offline_count} ({100*offline_count/len(predictions):.1f}%)")
    print(f"  Active: {active_count} ({100*active_count/len(predictions):.1f}%)")
    print(f"Predictions saved to: {output_json}")
    
    # Organize images if requested
    if organize_images:
        organize_by_prediction(predictions, output_dir)
    
    return predictions


def organize_by_prediction(predictions, output_dir="data/organized", 
                          copy_files=True, confidence_threshold=0.5):
    """Organize images into folders based on predictions."""
    output_path = Path(output_dir)
    offline_dir = output_path / 'offline'
    active_dir = output_path / 'active'
    uncertain_dir = output_path / 'uncertain'
    
    # Create directories
    offline_dir.mkdir(parents=True, exist_ok=True)
    active_dir.mkdir(parents=True, exist_ok=True)
    uncertain_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\nOrganizing images to {output_dir}...")
    
    offline_count = 0
    active_count = 0
    uncertain_count = 0
    
    for img_path_str, pred_data in tqdm(predictions.items()):
        img_path = Path(img_path_str)
        label = pred_data['label']
        confidence = pred_data['confidence']
        
        # Determine destination
        if confidence < confidence_threshold:
            dest_dir = uncertain_dir
            uncertain_count += 1
        elif label == 'offline':
            dest_dir = offline_dir
            offline_count += 1
        else:
            dest_dir = active_dir
            active_count += 1
        
        # Create subdirectory by date
        date_subdir = dest_dir / img_path.parent.name
        date_subdir.mkdir(parents=True, exist_ok=True)
        
        # Copy or move file
        dest_path = date_subdir / img_path.name
        
        try:
            if copy_files:
                shutil.copy2(img_path, dest_path)
            else:
                shutil.move(str(img_path), str(dest_path))
        except Exception as e:
            print(f"Error organizing {img_path}: {e}")
    
    print(f"\n=== Organization Complete ===")
    print(f"Offline images: {offline_count}")
    print(f"Active images: {active_count}")
    print(f"Uncertain images (confidence < {confidence_threshold}): {uncertain_count}")
    print(f"Images organized in: {output_dir}")


def filter_active_images(predictions_json="data/predictions.json",
                        output_list="data/active_images.txt",
                        confidence_threshold=0.7):
    """Create a list of active images for further processing."""
    with open(predictions_json, 'r') as f:
        predictions = json.load(f)
    
    active_images = []
    
    for img_path, pred_data in predictions.items():
        if pred_data['label'] == 'active' and pred_data['confidence'] >= confidence_threshold:
            active_images.append(img_path)
    
    # Save list
    Path(output_list).parent.mkdir(parents=True, exist_ok=True)
    with open(output_list, 'w') as f:
        for img_path in sorted(active_images):
            f.write(f"{img_path}\n")
    
    print(f"\n=== Active Images Filter ===")
    print(f"Found {len(active_images)} active images with confidence >= {confidence_threshold}")
    print(f"List saved to: {output_list}")
    
    return active_images


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run inference on printer images")
    parser.add_argument('--model-path', type=str, default='models/printer_offline_detector.pth',
                       help='Path to trained model')
    parser.add_argument('--base-dir', type=str, default='printer-timelapses',
                       help='Base directory containing images')
    parser.add_argument('--output-json', type=str, default='data/predictions.json',
                       help='Path to save predictions JSON')
    parser.add_argument('--organize', action='store_true',
                       help='Organize images into folders by prediction')
    parser.add_argument('--output-dir', type=str, default='data/organized',
                       help='Output directory for organized images')
    parser.add_argument('--copy', action='store_true', default=True,
                       help='Copy files instead of moving them')
    parser.add_argument('--confidence-threshold', type=float, default=0.5,
                       help='Confidence threshold for uncertain classification')
    parser.add_argument('--filter-active', action='store_true',
                       help='Create a filtered list of active images')
    parser.add_argument('--filter-threshold', type=float, default=0.7,
                       help='Confidence threshold for active image filter')
    
    args = parser.parse_args()
    
    # Run inference
    predictions = run_inference(
        model_path=args.model_path,
        base_dir=args.base_dir,
        output_json=args.output_json,
        organize_images=args.organize,
        output_dir=args.output_dir
    )
    
    # Filter active images if requested
    if args.filter_active:
        filter_active_images(
            predictions_json=args.output_json,
            confidence_threshold=args.filter_threshold
        )

