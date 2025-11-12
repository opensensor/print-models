#!/bin/bash
# Setup Git LFS for dataset and model version control

set -e  # Exit on error

echo "============================================================"
echo "Setting up Git LFS for print-models repository"
echo "============================================================"
echo

# Check if git-lfs is installed
if ! command -v git-lfs &> /dev/null; then
    echo "❌ Git LFS is not installed"
    echo
    echo "Please install Git LFS first:"
    echo "  Ubuntu/Debian: sudo apt-get install git-lfs"
    echo "  macOS: brew install git-lfs"
    echo "  Or visit: https://git-lfs.github.com/"
    exit 1
fi

echo "✓ Git LFS is installed"
echo

# Initialize Git LFS
echo "Initializing Git LFS..."
git lfs install
echo "✓ Git LFS initialized"
echo

# Configure LFS tracking
echo "Configuring Git LFS to track large files..."

# Track dataset images
git lfs track "datasets/**/*.jpg"
git lfs track "datasets/**/*.png"
git lfs track "datasets/**/*.jpeg"

# Track versioned models
git lfs track "models/versions/*.pth"
git lfs track "models/versions/*.pt"

# Track training history plots (optional, but nice to have)
git lfs track "models/versions/*.png"

echo "✓ Configured LFS tracking patterns"
echo

# Show what will be tracked
echo "Files that will be tracked by Git LFS:"
cat .gitattributes
echo

# Create directory structure
echo "Creating directory structure..."
mkdir -p datasets/offline-detection
mkdir -p datasets/failed-print-detection
mkdir -p models/versions
mkdir -p scripts
echo "✓ Created directories"
echo

# Update .gitignore if needed
echo "Updating .gitignore..."

# Check if .gitignore exists
if [ ! -f .gitignore ]; then
    echo "Creating .gitignore..."
    cat > .gitignore << 'EOF'
# Python
venv/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info/
dist/
build/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Data files (transient)
data/monitor_state.json
data/predictions.json
data/active_candidates.txt
data/active_images.txt
data/organized/

# Camera symlink - don't track live camera data
printer-timelapses/

# Keep these tracked (managed by Git LFS):
# datasets/
# models/versions/
EOF
else
    # Check if printer-timelapses is already in .gitignore
    if ! grep -q "printer-timelapses" .gitignore; then
        echo "" >> .gitignore
        echo "# Camera symlink - don't track live camera data" >> .gitignore
        echo "printer-timelapses/" >> .gitignore
    fi
fi

echo "✓ Updated .gitignore"
echo

# Stage .gitattributes
echo "Staging .gitattributes..."
git add .gitattributes
echo "✓ Staged .gitattributes"
echo

echo "============================================================"
echo "✓ Git LFS setup complete!"
echo "============================================================"
echo
echo "Next steps:"
echo
echo "1. Export your current dataset:"
echo "   python scripts/export_dataset.py \\"
echo "       --labels-file data/labels.json \\"
echo "       --output-dir datasets/offline-detection/v1 \\"
echo "       --version '1.0' \\"
echo "       --description 'Initial training set: 60 active, 90 offline' \\"
echo "       --dataset-type offline-detection"
echo
echo "2. Export failed print dataset:"
echo "   python scripts/export_dataset.py \\"
echo "       --labels-file data/failed_print_labels.json \\"
echo "       --output-dir datasets/failed-print-detection/v1 \\"
echo "       --version '1.0' \\"
echo "       --description 'Initial failed print dataset: 175 good, 21 failed' \\"
echo "       --dataset-type failed-print-detection"
echo
echo "3. Copy current models to versions:"
echo "   cp models/printer_offline_detector.pth models/versions/offline_detector_v1.pth"
echo "   cp models/failed_print_detector.pth models/versions/failed_detector_v1.pth"
echo
echo "4. Commit everything:"
echo "   git add datasets/ models/versions/"
echo "   git commit -m 'Add versioned datasets and models with Git LFS'"
echo
echo "5. Push to remote (LFS files will be uploaded):"
echo "   git push"
echo
echo "============================================================"
echo
echo "Git LFS Storage Info:"
echo "  - Free tier: 1 GB storage, 1 GB/month bandwidth"
echo "  - Estimated dataset size: ~150 MB (well within limits)"
echo "  - Check usage: https://github.com/settings/billing"
echo
echo "============================================================"

