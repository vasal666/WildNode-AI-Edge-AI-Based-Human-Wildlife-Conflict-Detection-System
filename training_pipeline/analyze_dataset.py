import os
from collections import Counter

def analyze_dataset(dataset_dir):
    print(f"Analyzing dataset in: {dataset_dir}")
    
    all_files = os.listdir(dataset_dir)
    images = [f for f in all_files if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    annotations = [f for f in all_files if f.lower().endswith('.txt')]
    others = [f for f in all_files if not f.lower().endswith(('.jpg', '.jpeg', '.png', '.txt'))]
    
    print(f"Total images found: {len(images)}")
    print(f"Total annotation files found: {len(annotations)}")
    print(f"Other files found: {others}")
    
    # Check matching
    img_names = {os.path.splitext(f)[0] for f in images}
    ann_names = {os.path.splitext(f)[0] for f in annotations}
    
    missing_annotations = img_names - ann_names
    missing_images = ann_names - img_names
    
    print(f"Images without annotations: {len(missing_annotations)}")
    print(f"Annotations without images: {len(missing_images)}")
    
    class_counter = Counter()
    total_boxes = 0
    inconsistent_lines = []
    
    for ann in annotations:
        ann_path = os.path.join(dataset_dir, ann)
        with open(ann_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            for line_idx, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue
                parts = line.split()
                if len(parts) < 5:
                    inconsistent_lines.append((ann, line_idx + 1, line))
                    continue
                
                try:
                    coords = [float(x) for x in parts[-4:]]
                    class_name = " ".join(parts[:-4])
                    class_counter[class_name] += 1
                    total_boxes += 1
                except ValueError:
                    inconsistent_lines.append((ann, line_idx + 1, line))
                    
    print("\n--- Bounding Box Counts by Class ---")
    for cls, count in sorted(class_counter.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cls}: {count}")
        
    print(f"\nTotal bounding boxes: {total_boxes}")
    
    if inconsistent_lines:
        print(f"\nFound {len(inconsistent_lines)} inconsistent or unparseable lines:")
        for file, line, content in inconsistent_lines[:10]:
            print(f"  {file}:{line} -> {content}")
        if len(inconsistent_lines) > 10:
            print("  ...")
    else:
        print("\nAll parsed annotation lines are valid (ClassName xmin ymin xmax ymax)!")

if __name__ == '__main__':
    dataset_path = r"c:\Users\misfa\Desktop\dataset"
    analyze_dataset(dataset_path)

