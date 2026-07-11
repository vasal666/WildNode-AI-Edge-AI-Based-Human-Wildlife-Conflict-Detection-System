# Custom Wildlife Training Pipeline

This folder contains the templates and scripts needed to train a custom YOLO11 model for WildNode AI. By fine-tuning, the AI will learn exactly what your target animals look like, removing the need for hacky class mappings and vastly improving accuracy.

## 1. Prepare Your Data
You need images of the animals you want to detect, along with "bounding box" labels.

The easiest way to do this is using **[Roboflow](https://roboflow.com/)**:
1. Create a free account and start a new **Object Detection** project.
2. Upload images of your specific local threats (e.g., elephants, nilgai, wild boars).
3. Draw bounding boxes around the animals in the tool.
4. Click "Generate Dataset" and export it in **YOLOv8/YOLO11 format**.

## 2. Structure Your Folder
Once downloaded, place the `images` and `labels` folders inside a `dataset/` directory here:
```text
training_pipeline/
│
├── data.yaml                  <-- Update class names here to match your Roboflow project
├── train_custom_yolo.py       <-- Training script
│
└── dataset/                   <-- Create this folder and put your Roboflow export here
    ├── images/
    │   ├── train/             <-- Training images (.jpg)
    │   └── val/               <-- Validation images (.jpg)
    └── labels/
        ├── train/             <-- Training labels (.txt)
        └── val/               <-- Validation labels (.txt)
```

## 3. Run Training
Open your terminal, navigate to this `training_pipeline` folder, and run:
```bash
python train_custom_yolo.py
```

*Note: Training on a CPU can take several hours. If you have an NVIDIA GPU, make sure PyTorch with CUDA is installed for it to train in minutes.*

## 4. Use Your New Model
Once training finishes, Ultralytics will save a file called `best.pt` in the `runs/detect/wildnode_custom/weights/` folder.
1. Copy `best.pt` into your main `wildnode_ai-main` folder.
2. Update your `app.py` or `wildlife_detector.py` to load `best.pt` instead of `yolo11n.pt`.
3. You can now delete the old `WILDLIFE_CLASS_MAP` mappings because your model will output exact names naturally!
