"""
WildNode AI - Custom YOLO11 Training Script
===========================================
Use this script to fine-tune the YOLO11 model on your own dataset.

Requirements:
pip install ultralytics

Usage:
1. Place your dataset in the `dataset/` folder (images and labels).
2. Update `data.yaml` if you added or removed classes.
3. Run this script: python train_custom_yolo.py
"""

import os
from ultralytics import YOLO

def main():
    # 1. Load the pre-trained YOLO11-nano model
    # Using the pre-trained model ensures we don't start from scratch
    print("[INFO] Loading base model yolo11n.pt...")
    model = YOLO("yolo11n.pt") 

    # 2. Train the model on our custom dataset
    print("[INFO] Starting training...")
    
    # We use absolute path for data.yaml to avoid any path confusion
    data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.yaml")
    
    results = model.train(
        data=data_path,        # Path to dataset configuration file
        epochs=50,             # Number of training epochs (increase if underfitting)
        imgsz=640,             # Image size
        batch=16,              # Batch size (reduce if you run out of GPU memory)
        name="wildnode_custom",# Name of the output folder (saved in runs/detect/)
        device="",             # Device to run on ('0' for GPU, 'cpu' for CPU. Blank = auto-detect)
        workers=4,             # Number of worker threads for data loading
        patience=10            # Early stopping patience
    )

    print("\n[SUCCESS] Training complete!")
    print("[INFO] Your custom model weights are saved in: runs/detect/wildnode_custom/weights/best.pt")
    print("[INFO] Copy 'best.pt' to your main folder to use it in the dashboard.")

if __name__ == "__main__":
    main()
