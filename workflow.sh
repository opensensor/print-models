#!/bin/bash
# Workflow script for printer-offline detection model development

set -e

echo "=== Printer-Offline Detection Workflow ==="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import torch" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
else
    echo "Dependencies already installed."
fi

echo ""
echo "Available commands:"
echo ""
echo "1. Explore data:"
echo "   python src/explore_images.py --mode stats"
echo "   python src/explore_images.py --mode random --num-samples 12"
echo "   python src/explore_images.py --mode temporal --date 20251110 --start-idx 0"
echo ""
echo "2. Label images (interactive):"
echo "   python src/label_images.py --sample-size 100"
echo ""
echo "3. Train model:"
echo "   python src/train_model.py --epochs 20 --batch-size 32"
echo ""
echo "4. Run inference:"
echo "   python src/inference.py --organize --filter-active"
echo ""
echo "5. Quick start (label 100 images):"
echo "   python src/label_images.py --sample-size 100"
echo ""

# Parse command line argument
if [ "$1" == "explore" ]; then
    echo "Running data exploration..."
    python src/explore_images.py --mode stats
    
elif [ "$1" == "label" ]; then
    SAMPLE_SIZE=${2:-100}
    echo "Starting labeling tool for $SAMPLE_SIZE images..."
    python src/label_images.py --sample-size $SAMPLE_SIZE
    
elif [ "$1" == "train" ]; then
    echo "Training model..."
    python src/train_model.py --epochs 20 --batch-size 32
    
elif [ "$1" == "inference" ]; then
    echo "Running inference..."
    python src/inference.py --organize --filter-active
    
elif [ "$1" == "all" ]; then
    echo "Running full workflow..."
    echo ""
    echo "Step 1: Exploring data..."
    python src/explore_images.py --mode stats
    echo ""
    echo "Step 2: Please label images using:"
    echo "  python src/label_images.py --sample-size 100"
    echo ""
    echo "After labeling, run: ./workflow.sh train"
    
else
    echo "Usage: ./workflow.sh [explore|label|train|inference|all]"
    echo ""
    echo "Or run commands manually as shown above."
fi

