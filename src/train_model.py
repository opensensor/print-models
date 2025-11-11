#!/usr/bin/env python3
"""
Train a printer-offline detection model using labeled images.
Uses transfer learning with a pre-trained ResNet model.
"""

import json
import random
from pathlib import Path
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms, models
from sklearn.model_selection import train_test_split
from tqdm import tqdm


class PrinterImageDataset(Dataset):
    """Dataset for printer timelapse images."""
    
    def __init__(self, image_paths, labels, transform=None):
        self.image_paths = image_paths
        self.labels = labels  # 0 for offline, 1 for active
        self.transform = transform
    
    def __len__(self):
        return len(self.image_paths)
    
    def __getitem__(self, idx):
        img_path = self.image_paths[idx]
        label = self.labels[idx]
        
        try:
            image = Image.open(img_path).convert('RGB')
            
            if self.transform:
                image = self.transform(image)
            
            return image, label
        except Exception as e:
            print(f"Error loading {img_path}: {e}")
            # Return a blank image on error
            blank = Image.new('RGB', (224, 224), color='black')
            if self.transform:
                blank = self.transform(blank)
            return blank, label


def load_labeled_data(labels_file="data/labels.json"):
    """Load labeled data from JSON file."""
    with open(labels_file, 'r') as f:
        labels_dict = json.load(f)
    
    image_paths = []
    labels = []
    
    label_map = {'offline': 0, 'active': 1}
    
    for img_path, label_str in labels_dict.items():
        if label_str in label_map:
            image_paths.append(img_path)
            labels.append(label_map[label_str])
    
    return image_paths, labels


def create_model(num_classes=2, pretrained=True):
    """Create a ResNet18 model for binary classification."""
    model = models.resnet18(pretrained=pretrained)
    
    # Modify the final layer for binary classification
    num_features = model.fc.in_features
    model.fc = nn.Linear(num_features, num_classes)
    
    return model


def train_epoch(model, dataloader, criterion, optimizer, device):
    """Train for one epoch."""
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0
    
    pbar = tqdm(dataloader, desc='Training')
    for images, labels in pbar:
        images, labels = images.to(device), labels.to(device)
        
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        
        running_loss += loss.item()
        _, predicted = outputs.max(1)
        total += labels.size(0)
        correct += predicted.eq(labels).sum().item()
        
        pbar.set_postfix({'loss': running_loss / (pbar.n + 1), 
                         'acc': 100. * correct / total})
    
    epoch_loss = running_loss / len(dataloader)
    epoch_acc = 100. * correct / total
    
    return epoch_loss, epoch_acc


def validate(model, dataloader, criterion, device):
    """Validate the model."""
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0
    
    with torch.no_grad():
        for images, labels in tqdm(dataloader, desc='Validation'):
            images, labels = images.to(device), labels.to(device)
            
            outputs = model(images)
            loss = criterion(outputs, labels)
            
            running_loss += loss.item()
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
    
    val_loss = running_loss / len(dataloader)
    val_acc = 100. * correct / total
    
    return val_loss, val_acc


def plot_training_history(history, save_path='models/training_history.png'):
    """Plot training and validation metrics."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    
    epochs = range(1, len(history['train_loss']) + 1)
    
    # Loss plot
    ax1.plot(epochs, history['train_loss'], 'b-', label='Training Loss')
    ax1.plot(epochs, history['val_loss'], 'r-', label='Validation Loss')
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Loss')
    ax1.set_title('Training and Validation Loss')
    ax1.legend()
    ax1.grid(True)
    
    # Accuracy plot
    ax2.plot(epochs, history['train_acc'], 'b-', label='Training Accuracy')
    ax2.plot(epochs, history['val_acc'], 'r-', label='Validation Accuracy')
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('Accuracy (%)')
    ax2.set_title('Training and Validation Accuracy')
    ax2.legend()
    ax2.grid(True)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"Saved training history plot to {save_path}")


def main(labels_file="data/labels.json", model_save_path="models/printer_offline_detector.pth",
         batch_size=32, num_epochs=20, learning_rate=0.001, val_split=0.2):
    
    # Set device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Load labeled data
    print(f"Loading labels from {labels_file}...")
    image_paths, labels = load_labeled_data(labels_file)
    
    print(f"Total labeled images: {len(image_paths)}")
    print(f"  Offline: {labels.count(0)}")
    print(f"  Active: {labels.count(1)}")
    
    if len(image_paths) < 10:
        print("ERROR: Not enough labeled data. Please label more images first.")
        return
    
    # Split data
    train_paths, val_paths, train_labels, val_labels = train_test_split(
        image_paths, labels, test_size=val_split, random_state=42, stratify=labels
    )
    
    print(f"\nTrain set: {len(train_paths)} images")
    print(f"Validation set: {len(val_paths)} images")
    
    # Data transforms
    train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(5),
        transforms.ColorJitter(brightness=0.2, contrast=0.2),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    val_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    # Create datasets and dataloaders
    train_dataset = PrinterImageDataset(train_paths, train_labels, train_transform)
    val_dataset = PrinterImageDataset(val_paths, val_labels, val_transform)
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=4)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=4)
    
    # Create model
    print("\nCreating model...")
    model = create_model(num_classes=2, pretrained=True)
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
    
    # Training loop
    print(f"\nStarting training for {num_epochs} epochs...")
    for epoch in range(num_epochs):
        print(f"\nEpoch {epoch + 1}/{num_epochs}")
        
        train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer, device)
        val_loss, val_acc = validate(model, val_loader, criterion, device)
        
        history['train_loss'].append(train_loss)
        history['train_acc'].append(train_acc)
        history['val_loss'].append(val_loss)
        history['val_acc'].append(val_acc)
        
        print(f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.2f}%")
        print(f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}%")
        
        scheduler.step(val_loss)
        
        # Save best model
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            Path(model_save_path).parent.mkdir(parents=True, exist_ok=True)
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_acc': val_acc,
                'val_loss': val_loss,
            }, model_save_path)
            print(f"Saved best model with validation accuracy: {val_acc:.2f}%")
    
    print(f"\nTraining complete! Best validation accuracy: {best_val_acc:.2f}%")
    
    # Plot training history
    plot_training_history(history)
    
    return model, history


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Train printer-offline detection model")
    parser.add_argument('--labels-file', type=str, default='data/labels.json',
                       help='Path to labels JSON file')
    parser.add_argument('--model-save-path', type=str, default='models/printer_offline_detector.pth',
                       help='Path to save trained model')
    parser.add_argument('--batch-size', type=int, default=32,
                       help='Batch size for training')
    parser.add_argument('--epochs', type=int, default=20,
                       help='Number of training epochs')
    parser.add_argument('--lr', type=float, default=0.001,
                       help='Learning rate')
    parser.add_argument('--val-split', type=float, default=0.2,
                       help='Validation split ratio')
    
    args = parser.parse_args()
    
    main(
        labels_file=args.labels_file,
        model_save_path=args.model_save_path,
        batch_size=args.batch_size,
        num_epochs=args.epochs,
        learning_rate=args.lr,
        val_split=args.val_split
    )

