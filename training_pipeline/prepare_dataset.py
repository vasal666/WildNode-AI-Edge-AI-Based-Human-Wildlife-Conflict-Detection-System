import os
import shutil
import random
from PIL import Image

def prepare_dataset():
    input_dir = r"c:\Users\misfa\Desktop\dataset"
    output_dir = r"c:\Users\misfa\Downloads\wildnode_ai-main\wildnode_ai-main\training_pipeline\dataset"
    
    # 8 strict target classes in data.yaml
    CLASS_MAP = {
        "wild_boar": 0, "Wild Boar": 0, "wild boar": 0, "Wild_Boar": 0, "wildboar": 0,
        "elephant": 1, "Elephant": 1,
        "tiger": 2, "Tiger": 2,
        "bear": 3, "Bear": 3,
        "fox": 4, "Fox": 4,
        "monkey": 5, "Monkey": 5,
        "lion": 6, "Lion": 6,
        "leopard": 7, "Leopard": 7
    }
    
    print(f"Reading input dataset from: {input_dir}")
    print(f"Target dataset directory: {output_dir}")
    
    # Clear existing target directory to ensure clean run
    if os.path.exists(output_dir):
        print(f"Cleaning up existing target directory: {output_dir}")
        shutil.rmtree(output_dir)

    # Create target directories
    for split in ['train', 'val']:
        os.makedirs(os.path.join(output_dir, 'images', split), exist_ok=True)
        os.makedirs(os.path.join(output_dir, 'labels', split), exist_ok=True)
        
    all_files = os.listdir(input_dir)
    images = [f for f in all_files if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    annotations = [f for f in all_files if f.lower().endswith('.txt')]
    
    # Pair images and annotations
    valid_pairs = []
    for img in images:
        base_name = os.path.splitext(img)[0]
        ann = base_name + ".txt"
        if ann in annotations:
            valid_pairs.append((img, ann))
            
    print(f"Found {len(valid_pairs)} matching image/annotation pairs.")
    
    # Shuffle and split (80% train, 20% validation)
    random.seed(42)
    random.shuffle(valid_pairs)
    
    split_idx = int(len(valid_pairs) * 0.8)
    train_pairs = valid_pairs[:split_idx]
    val_pairs = valid_pairs[split_idx:]
    
    print(f"Split: {len(train_pairs)} training pairs, {len(val_pairs)} validation pairs.")
    
    def process_and_copy(pairs, split):
        processed_count = 0
        skipped_count = 0
        class_stats = {i: 0 for i in range(8)}
        
        for img_file, ann_file in pairs:
            img_src = os.path.join(input_dir, img_file)
            ann_src = os.path.join(input_dir, ann_file)
            
            # Target paths
            img_dst = os.path.join(output_dir, 'images', split, img_file)
            ann_dst = os.path.join(output_dir, 'labels', split, ann_file)
            
            # Read image dimensions
            try:
                with Image.open(img_src) as img_obj:
                    img_w, img_h = img_obj.size
            except Exception as e:
                print(f"[ERROR] Could not open image {img_src}: {e}")
                skipped_count += 1
                continue
                
            is_roboflow = img_file.lower().startswith('z')
            yolo_lines = []
            valid_file = True
            
            with open(ann_src, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                
            for line_idx, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue
                
                parts = line.split()
                if len(parts) < 5:
                    print(f"[WARNING] Skipping malformed line in {ann_file}:{line_idx+1}")
                    continue
                
                if is_roboflow:
                    # Roboflow files start with class index '0' which user confirmed is 'wild_boar'
                    try:
                        cls_idx = int(parts[0])
                        if cls_idx == 0:
                            target_idx = 0 # wild_boar
                        else:
                            # If there are other numbers, map them to wild_boar as well, or skip
                            target_idx = 0
                        
                        # Roboflow is already in normalized YOLO format: class x_center y_center w h
                        x_c, y_c, w, h = [float(x) for x in parts[1:5]]
                        
                        # Validate range
                        if not (0 <= x_c <= 1 and 0 <= y_c <= 1 and 0 <= w <= 1 and 0 <= h <= 1):
                            print(f"[WARNING] Out-of-bounds normalized coordinates in Roboflow file {ann_file}")
                            
                        yolo_lines.append(f"{target_idx} {x_c:.6f} {y_c:.6f} {w:.6f} {h:.6f}\n")
                        class_stats[target_idx] += 1
                    except Exception as e:
                        print(f"[ERROR] Failed to parse Roboflow line in {ann_file}: {e}")
                        valid_file = False
                else:
                    # Custom coordinate format: ClassName xmin ymin xmax ymax
                    try:
                        class_name = " ".join(parts[:-4])
                        coords = [float(x) for x in parts[-4:]]
                        
                        if class_name in CLASS_MAP:
                            target_idx = CLASS_MAP[class_name]
                            
                            xmin, ymin, xmax, ymax = coords
                            
                            # Convert to YOLO format
                            w = xmax - xmin
                            h = ymax - ymin
                            x_center = xmin + w / 2
                            y_center = ymin + h / 2
                            
                            # Normalize
                            x_center_norm = x_center / img_w
                            y_center_norm = y_center / img_h
                            width_norm = w / img_w
                            height_norm = h / img_h
                            
                            # Clamp values to [0.0, 1.0] just in case of rounding errors
                            x_center_norm = max(0.0, min(1.0, x_center_norm))
                            y_center_norm = max(0.0, min(1.0, y_center_norm))
                            width_norm = max(0.0, min(1.0, width_norm))
                            height_norm = max(0.0, min(1.0, height_norm))
                            
                            yolo_lines.append(f"{target_idx} {x_center_norm:.6f} {y_center_norm:.6f} {width_norm:.6f} {height_norm:.6f}\n")
                            class_stats[target_idx] += 1
                        else:
                            print(f"[WARNING] Skipping unknown class name '{class_name}' in {ann_file}")
                    except Exception as e:
                        print(f"[ERROR] Failed to parse pixel coordinate line in {ann_file}: {e}")
                        valid_file = False
                        
            if valid_file and yolo_lines:
                # Copy image
                shutil.copy2(img_src, img_dst)
                # Write YOLO format label
                with open(ann_dst, 'w', encoding='utf-8') as f:
                    f.writelines(yolo_lines)
                processed_count += 1
            else:
                skipped_count += 1
                
        print(f"  Processed {processed_count} pairs for split '{split}' (Skipped {skipped_count}).")
        print("  Class distribution:")
        for idx, count in class_stats.items():
            class_name = [name for name, i in CLASS_MAP.items() if i == idx][0]
            print(f"    - {class_name} (Class {idx}): {count}")
            
    print("\n--- Processing Training Split ---")
    process_and_copy(train_pairs, 'train')
    
    print("\n--- Processing Validation Split ---")
    process_and_copy(val_pairs, 'val')
    
    print("\n[SUCCESS] Dataset preparation and YOLO format conversion completed!")

if __name__ == '__main__':
    prepare_dataset()
