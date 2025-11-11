.PHONY: help setup explore label train inference analyze clean

help:
	@echo "Printer-Offline Detection Model - Available Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make setup          - Create venv and install dependencies"
	@echo ""
	@echo "Data Exploration:"
	@echo "  make explore        - Show dataset statistics"
	@echo "  make explore-visual - Visualize random samples"
	@echo "  make explore-time   - View temporal sequence"
	@echo ""
	@echo "Labeling:"
	@echo "  make label          - Label 100 images (interactive)"
	@echo "  make label-50       - Label 50 images"
	@echo "  make label-200      - Label 200 images"
	@echo ""
	@echo "Training:"
	@echo "  make train          - Train model (20 epochs)"
	@echo "  make train-quick    - Quick training (10 epochs)"
	@echo "  make train-long     - Extended training (30 epochs)"
	@echo ""
	@echo "Inference:"
	@echo "  make inference      - Run inference on all images"
	@echo "  make inference-org  - Run inference and organize images"
	@echo ""
	@echo "Analysis:"
	@echo "  make analyze        - Analyze labels and predictions"
	@echo "  make analyze-conf   - Plot confidence distribution"
	@echo "  make analyze-uncertain - Find uncertain predictions"
	@echo ""
	@echo "Phase 2 - Failed Print Detection:"
	@echo "  make label-failed   - Label active images as good/failed"
	@echo "  make train-failed   - Train failed print detection model"
	@echo "  make status-failed  - Show failed print detection status"
	@echo ""
	@echo "Real-time Monitoring (tail -f style):"
	@echo "  make monitor        - Monitor today's prints (30s poll)"
	@echo "  make monitor-fast   - Monitor with 10s poll"
	@echo "  make monitor-date DATE=YYYYMMDD - Monitor specific date"
	@echo "  ./demo_monitor.sh   - Demo with existing images"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean          - Remove generated files (keep labels)"
	@echo "  make clean-all      - Remove all generated files"
	@echo "  make status         - Show project status"

setup:
	python3 -m venv venv
	./venv/bin/pip install -r requirements.txt
	@echo "Setup complete! Activate with: source venv/bin/activate"

explore:
	./venv/bin/python src/explore_images.py --mode stats

explore-visual:
	./venv/bin/python src/explore_images.py --mode random --num-samples 12

explore-time:
	./venv/bin/python src/explore_images.py --mode temporal --date 20251110

label:
	./venv/bin/python src/label_images.py --sample-size 100

label-50:
	./venv/bin/python src/label_images.py --sample-size 50

label-200:
	./venv/bin/python src/label_images.py --sample-size 200

train:
	./venv/bin/python src/train_model.py --epochs 20 --batch-size 32

train-quick:
	./venv/bin/python src/train_model.py --epochs 10 --batch-size 32

train-long:
	./venv/bin/python src/train_model.py --epochs 30 --batch-size 32

inference:
	./venv/bin/python src/inference.py

inference-org:
	./venv/bin/python src/inference.py --organize --filter-active

analyze:
	./venv/bin/python src/analyze_results.py --mode all

analyze-conf:
	./venv/bin/python src/analyze_results.py --mode predictions --plot-confidence

analyze-uncertain:
	./venv/bin/python src/analyze_results.py --find-uncertain --uncertainty-threshold 0.6

# Phase 2: Failed Print Detection
label-failed:
	./venv/bin/python src/label_failed_prints.py

train-failed:
	./venv/bin/python src/train_failed_print_model.py --epochs 20 --batch-size 32

status-failed:
	@echo "=== Failed Print Detection Status ==="
	@echo ""
	@if [ -f "data/active_images.txt" ]; then \
		echo "✓ Active images list exists"; \
		echo "  Total active images: $$(wc -l < data/active_images.txt)"; \
	else \
		echo "✗ No active images list (run: make inference-org)"; \
	fi
	@if [ -f "data/failed_print_labels.json" ]; then \
		echo "✓ Failed print labels exist"; \
		echo "  Labeled images: $$(cat data/failed_print_labels.json | grep -o '"good"' | wc -l | xargs echo -n) good, $$(cat data/failed_print_labels.json | grep -o '"failed"' | wc -l | xargs echo -n) failed"; \
	else \
		echo "✗ No failed print labels yet (run: make label-failed)"; \
	fi
	@if [ -f "models/failed_print_detector.pth" ]; then echo "✓ Failed print model exists"; else echo "✗ No failed print model (run: make train-failed)"; fi
	@echo ""

# Real-time Monitoring
monitor:
	@TODAY=$$(date +%Y%m%d); \
	if [ -d "printer-timelapses/$$TODAY" ]; then \
		./venv/bin/python src/monitor_print.py --image-dir printer-timelapses/$$TODAY --interval 30; \
	else \
		echo "Error: Directory printer-timelapses/$$TODAY not found"; \
		echo "Available dates:"; \
		ls -1 printer-timelapses/ | grep -E '^[0-9]{8}$$' | tail -5; \
	fi

monitor-fast:
	@TODAY=$$(date +%Y%m%d); \
	if [ -d "printer-timelapses/$$TODAY" ]; then \
		./venv/bin/python src/monitor_print.py --image-dir printer-timelapses/$$TODAY --interval 10; \
	else \
		echo "Error: Directory printer-timelapses/$$TODAY not found"; \
		echo "Available dates:"; \
		ls -1 printer-timelapses/ | grep -E '^[0-9]{8}$$' | tail -5; \
	fi

monitor-date:
	@if [ -z "$(DATE)" ]; then \
		echo "Error: DATE parameter required"; \
		echo "Usage: make monitor-date DATE=20251110"; \
		echo "Available dates:"; \
		ls -1 printer-timelapses/ | grep -E '^[0-9]{8}$$' | tail -5; \
	elif [ -d "printer-timelapses/$(DATE)" ]; then \
		./venv/bin/python src/monitor_print.py --image-dir printer-timelapses/$(DATE) --interval 30; \
	else \
		echo "Error: Directory printer-timelapses/$(DATE) not found"; \
		echo "Available dates:"; \
		ls -1 printer-timelapses/ | grep -E '^[0-9]{8}$$' | tail -5; \
	fi

status:
	@echo "=== Project Status ==="
	@echo ""
	@if [ -d "venv" ]; then echo "✓ Virtual environment exists"; else echo "✗ Virtual environment missing (run: make setup)"; fi
	@if [ -f "data/labels.json" ]; then \
		echo "✓ Labels file exists"; \
		echo "  Labeled images: $$(cat data/labels.json | grep -o '"offline"' | wc -l | xargs echo -n) offline, $$(cat data/labels.json | grep -o '"active"' | wc -l | xargs echo -n) active"; \
	else \
		echo "✗ No labels yet (run: make label)"; \
	fi
	@if [ -f "models/printer_offline_detector.pth" ]; then echo "✓ Trained model exists"; else echo "✗ No trained model (run: make train)"; fi
	@if [ -f "data/predictions.json" ]; then \
		echo "✓ Predictions exist"; \
		echo "  Total predictions: $$(cat data/predictions.json | grep -o '"label"' | wc -l)"; \
	else \
		echo "✗ No predictions yet (run: make inference)"; \
	fi
	@echo ""
	@if [ -L "printer-timelapses" ]; then \
		echo "Dataset: $$(find -L printer-timelapses -name '*.jpg' 2>/dev/null | wc -l) images"; \
	else \
		echo "Dataset: $$(find printer-timelapses -name '*.jpg' 2>/dev/null | wc -l) images"; \
	fi

clean:
	rm -rf data/organized/
	rm -f data/predictions.json
	rm -f data/active_images.txt
	rm -f data/uncertain_images.txt
	rm -f data/*.png
	rm -f models/training_history.png
	@echo "Cleaned generated files (kept labels and model)"

clean-all: clean
	rm -f data/labels.json
	rm -f models/*.pth
	@echo "Cleaned all generated files"

