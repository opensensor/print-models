#!/bin/bash
# Demo script to test the printer-offline detection pipeline
# This creates a small demo with synthetic labels for testing

set -e

echo "=== Printer-Offline Detection Demo ==="
echo ""
echo "This demo will:"
echo "1. Check your setup"
echo "2. Create synthetic labels for testing (10 images)"
echo "3. Train a quick model (5 epochs)"
echo "4. Run inference on a subset"
echo "5. Show results"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 0
fi

# Activate virtual environment
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Run: make setup"
    exit 1
fi

source venv/bin/activate

# Check if images exist
IMAGE_COUNT=$(find -L printer-timelapses -name '*.jpg' 2>/dev/null | wc -l)
if [ "$IMAGE_COUNT" -eq 0 ]; then
    echo "No images found in printer-timelapses/"
    exit 1
fi

echo "Found $IMAGE_COUNT images"
echo ""

# Create demo labels (synthetic for testing)
echo "Creating demo labels..."
python3 << 'EOF'
import json
import random
from pathlib import Path

# Get some random images
base_dir = Path("printer-timelapses")
all_images = list(base_dir.rglob("*.jpg"))[:20]  # Just use first 20

# Create synthetic labels for demo
labels = {}
for img in all_images[:10]:
    # Randomly assign labels for demo
    label = random.choice(['offline', 'active'])
    labels[str(img)] = label

# Save
Path("data").mkdir(exist_ok=True)
with open("data/labels_demo.json", 'w') as f:
    json.dump(labels, f, indent=2)

print(f"Created {len(labels)} demo labels")
offline = sum(1 for v in labels.values() if v == 'offline')
active = sum(1 for v in labels.values() if v == 'active')
print(f"  Offline: {offline}")
print(f"  Active: {active}")
EOF

echo ""
echo "Training demo model (5 epochs, small dataset)..."
echo "Note: This is just for testing - accuracy will be low with only 10 labels!"
echo ""

python src/train_model.py \
    --labels-file data/labels_demo.json \
    --model-save-path models/demo_model.pth \
    --epochs 5 \
    --batch-size 4 \
    --val-split 0.3

echo ""
echo "Running inference on subset..."

# Get first 50 images for demo inference
python3 << 'EOF'
import json
import torch
import torch.nn as nn
from pathlib import Path
from PIL import Image
from torchvision import transforms, models
from tqdm import tqdm

# Load model
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = models.resnet18(pretrained=False)
model.fc = nn.Linear(model.fc.in_features, 2)
checkpoint = torch.load('models/demo_model.pth', map_location=device)
model.load_state_dict(checkpoint['model_state_dict'])
model = model.to(device)
model.eval()

# Transform
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# Get subset of images
base_dir = Path("printer-timelapses")
images = list(base_dir.rglob("*.jpg"))[:50]

# Run inference
predictions = {}
for img_path in tqdm(images, desc="Demo inference"):
    try:
        img = Image.open(img_path).convert('RGB')
        img_tensor = transform(img).unsqueeze(0).to(device)
        
        with torch.no_grad():
            outputs = model(img_tensor)
            probs = torch.nn.functional.softmax(outputs, dim=1)
            conf, pred = probs.max(1)
        
        label = 'offline' if pred.item() == 0 else 'active'
        predictions[str(img_path)] = {
            'label': label,
            'confidence': float(conf.item())
        }
    except Exception as e:
        print(f"Error: {e}")

# Save
with open('data/predictions_demo.json', 'w') as f:
    json.dump(predictions, f, indent=2)

# Stats
offline = sum(1 for p in predictions.values() if p['label'] == 'offline')
active = sum(1 for p in predictions.values() if p['label'] == 'active')

print(f"\nDemo Predictions:")
print(f"  Total: {len(predictions)}")
print(f"  Offline: {offline}")
print(f"  Active: {active}")
EOF

echo ""
echo "=== Demo Complete ==="
echo ""
echo "Demo files created:"
echo "  - data/labels_demo.json (10 synthetic labels)"
echo "  - models/demo_model.pth (demo model)"
echo "  - data/predictions_demo.json (50 predictions)"
echo ""
echo "Note: This was just a test with synthetic data!"
echo ""
echo "Next steps for real usage:"
echo "  1. Label real data: make label"
echo "  2. Train real model: make train"
echo "  3. Run full inference: make inference-org"
echo ""
echo "Clean up demo files with: rm data/*_demo.json models/demo_model.pth"

