import os
import shutil
from PIL import Image

SOURCE_DIR = r"c:\lumpyskin\downloads\THERMOMAST"
DATASET_DIR = r"c:\lumpyskin\udder_research\dataset"

# Clean old synthetic dataset
if os.path.exists(DATASET_DIR):
    shutil.rmtree(DATASET_DIR)
os.makedirs(os.path.join(DATASET_DIR, "healthy"), exist_ok=True)
os.makedirs(os.path.join(DATASET_DIR, "mastitis"), exist_ok=True)

healthy_count = 0
mastitis_count = 0

def augment_and_save(img_path, save_dir, base_name, class_counter):
    try:
        img = Image.open(img_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Save original
        orig_path = os.path.join(save_dir, f"{base_name}_{class_counter}.jpg")
        img.save(orig_path)
        class_counter += 1
        
        # Save flipped
        flipped = img.transpose(Image.FLIP_LEFT_RIGHT)
        flip_path = os.path.join(save_dir, f"{base_name}_{class_counter}_flip.jpg")
        flipped.save(flip_path)
        class_counter += 1
        
        # Save rotated
        rotated = img.rotate(15)
        rot_path = os.path.join(save_dir, f"{base_name}_{class_counter}_rot.jpg")
        rotated.save(rot_path)
        class_counter += 1
        
        return class_counter
    except Exception as e:
        print(f"Error processing {img_path}: {e}")
        return class_counter

for root, dirs, files in os.walk(SOURCE_DIR):
    for f in files:
        if f.lower().endswith(('.jpg', '.png', '.jpeg')):
            src = os.path.join(root, f)
            # Determine class based on folder name
            if "healthy" in root.lower() or "health" in f.lower():
                healthy_count = augment_and_save(src, os.path.join(DATASET_DIR, "healthy"), "healthy", healthy_count)
            elif "mastitis" in root.lower() or "mast" in f.lower():
                mastitis_count = augment_and_save(src, os.path.join(DATASET_DIR, "mastitis"), "mastitis", mastitis_count)
            else:
                # Default assume mastitis if it's from the THERMOMAST repo and not specifically healthy
                mastitis_count = augment_and_save(src, os.path.join(DATASET_DIR, "mastitis"), "mastitis", mastitis_count)

print(f"Total Healthy images: {healthy_count}")
print(f"Total Mastitis images: {mastitis_count}")
print(f"Total dataset size: {healthy_count + mastitis_count}")
