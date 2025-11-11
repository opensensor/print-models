#!/usr/bin/env python3
"""
Train a model to detect failed prints vs good prints.
Uses transfer learning with ResNet18.
"""

import json
import os
import argparse
from pathlib import Path
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import models, transforms
from PIL import Image
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from tqdm import tqdm


class FailedPrintDataset(Dataset):
    """Dataset for failed print detection."""
    
    def __init__(self, image_paths, labels, transform=None):
        """
        Args:
            image_paths: List of image file paths
            labels: List of labels ('good' or 'failed')
            transform: Optional transform to apply to images
        """
        self.image_paths = image_paths
        self.labels = labels
        self.transform = transform
        
        # Map labels to integers
        self.label_map = {'good': 0, 'failed': 1}
    
    def __len__(self):
        return len(self.image_paths)
    
    def __getitem__(self, idx):
        img_path = self.image_paths[idx]
        label = self.labels[idx]
        
        # Load image
        image = Image.open(img_path).convert('RGB')
        
        # Apply transforms
        if self.transform:
            image = self.transform(image)
        
        # Convert label to integer
        label_int = self.label_map[label]
        
        return image, label_int


def load_labels(labels_file):
    """Load labels from JSON file."""
    with open(labels_file, 'r') as f:
        labels_dict = json.load(f)
    
    image_paths = []
    labels = []
    
    for path, label in labels_dict.items():
        if os.path.exists(path):
            image_paths.append(path)
            labels.append(label)
        else:
            print(f"Warning: Image not found: {path}")
    
    return image_paths, labels


def create_model(num_classes=2):
    """Create ResNet18 model for binary classification."""
    model = models.resnet18(pretrained=True)
    
    # Freeze early layers
    for param in model.parameters():
        param.requires_grad = False
    
    # Replace final layer
    num_features = model.fc.in_features
    model.fc = nn.Linear(num_features, num_classes)
    
    # Unfreeze layer4 and fc for fine-tuning
    for param in model.layer4.parameters():
        param.requires_grad = True
    for param in model.fc.parameters():
        param.requires_grad = True
    
    return model


def train_epoch(model, dataloader, criterion, optimizer, device):
    """Train for one epoch."""
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0
    
    pbar = tqdm(dataloader, desc='Training')
    for images, labels in pbar:
        images = images.to(device)
        labels = labels.to(device)
        
        # Forward pass
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        
        # Backward pass
        loss.backward()
        optimizer.step()
        
        # Statistics
        running_loss += loss.item()
        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()
        
        # Update progress bar
        pbar.set_postfix({
            'loss': f'{loss.item():.4f}',
            'acc': f'{100 * correct / total:.1f}%'
        })
    
    epoch_loss = running_loss / len(dataloader)
    epoch_acc = 100 * correct / total
    
    return epoch_loss, epoch_acc


def validate(model, dataloader, criterion, device):
    """Validate the model."""
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0
    
    with torch.no_grad():
        pbar = tqdm(dataloader, desc='Validation')
        for images, labels in pbar:
            images = images.to(device)
            labels = labels.to(device)
            
            outputs = model(images)
            loss = criterion(outputs, labels)
            
            running_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
    
    val_loss = running_loss / len(dataloader)
    val_acc = 100 * correct / total
    
    return val_loss, val_acc


def plot_training_history(history, save_path):
    """Plot training history."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    
    # Plot loss
    ax1.plot(history['train_loss'], label='Train Loss')
    ax1.plot(history['val_loss'], label='Val Loss')
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Loss')
    ax1.set_title('Training and Validation Loss')
    ax1.legend()
    ax1.grid(True)
    
    # Plot accuracy
    ax2.plot(history['train_acc'], label='Train Acc')
    ax2.plot(history['val_acc'], label='Val Acc')
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('Accuracy (%)')
    ax2.set_title('Training and Validation Accuracy')
    ax2.legend()
    ax2.grid(True)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"Saved training history plot to {save_path}")


def main(labels_file, model_save_path, batch_size=32, epochs=20, learning_rate=0.001, val_split=0.2):
    """Main training function."""
    
    # Set device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Load labels
    print(f"Loading labels from {labels_file}...")
    image_paths, labels = load_labels(labels_file)
    
    if len(image_paths) == 0:
        print("Error: No labeled images found!")
        return
    
    # Print label distribution
    good_count = labels.count('good')
    failed_count = labels.count('failed')
    print(f"Total labeled images: {len(labels)}")
    print(f"  Good: {good_count}")
    print(f"  Failed: {failed_count}")
    print()
    
    if good_count == 0 or failed_count == 0:
        print("Error: Need at least one example of each class!")
        return
    
    # Split into train and validation
    train_paths, val_paths, train_labels, val_labels = train_test_split(
        image_paths, labels, test_size=val_split, random_state=42, stratify=labels
    )
    
    print(f"Train set: {len(train_paths)} images")
    print(f"Validation set: {len(val_paths)} images")
    print()
    
    # Define transforms
    train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(10),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    val_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    # Create datasets
    train_dataset = FailedPrintDataset(train_paths, train_labels, train_transform)
    val_dataset = FailedPrintDataset(val_paths, val_labels, val_transform)
    
    # Create dataloaders
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=2)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=2)
    
    # Create model
    print("Creating model...")
    model = create_model(num_classes=2)
    model = model.to(device)
    
    # Loss and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', patience=3)
    
    # Training history
    history = {
        'train_loss': [],
        'train_acc': [],
        'val_loss': [],
        'val_acc': []
    }
    
    best_val_acc = 0.0
    
    print(f"\nStarting training for {epochs} epochs...")
    print()
    
    for epoch in range(epochs):
        print(f"Epoch {epoch + 1}/{epochs}")
        
        # Train
        train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer, device)
        
        # Validate
        val_loss, val_acc = validate(model, val_loader, criterion, device)
        
        # Update scheduler
        scheduler.step(val_loss)
        
        # Save history
        history['train_loss'].append(train_loss)
        history['train_acc'].append(train_acc)
        history['val_loss'].append(val_loss)
        history['val_acc'].append(val_acc)
        
        print(f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.2f}%")
        print(f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}%")
        
        # Save best model
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            os.makedirs(os.path.dirname(model_save_path), exist_ok=True)
            torch.save({
                'model_state_dict': model.state_dict(),
                'val_acc': val_acc,
                'label_map': {'good': 0, 'failed': 1}
            }, model_save_path)
            print(f"Saved best model with validation accuracy: {val_acc:.2f}%")
        
        print()
    
    print(f"Training complete! Best validation accuracy: {best_val_acc:.2f}%")
    
    # Plot training history
    plot_path = model_save_path.replace('.pth', '_history.png')
    plot_training_history(history, plot_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Train failed print detection model')
    parser.add_argument('--labels-file', type=str, default='data/failed_print_labels.json',
                       help='Path to labels JSON file')
    parser.add_argument('--model-save-path', type=str, default='models/failed_print_detector.pth',
                       help='Path to save trained model')
    parser.add_argument('--batch-size', type=int, default=32,
                       help='Batch size for training')
    parser.add_argument('--epochs', type=int, default=20,
                       help='Number of epochs to train')
    parser.add_argument('--lr', type=float, default=0.001,
                       help='Learning rate')
    parser.add_argument('--val-split', type=float, default=0.2,
                       help='Validation split ratio')
    
    args = parser.parse_args()
    
    main(
        labels_file=args.labels_file,
        model_save_path=args.model_save_path,
        batch_size=args.batch_size,
        epochs=args.epochs,
        learning_rate=args.lr,
        val_split=args.val_split
    )

