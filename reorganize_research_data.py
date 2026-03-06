import os
import shutil
import random

# Paths
source_lumpy = r"c:\lumpyskin\downloads\Lumpy_disease\training\LumpyVillage\Lumpy Skin"
source_normal = r"c:\lumpyskin\downloads\Lumpy_disease\training\LumpyVillage\Normal Skin"

target_base = r"c:\lumpyskin"
target_train = os.path.join(target_base, "train")
target_test = os.path.join(target_base, "test")

# Clear existing folders
def clear_folder(path):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(os.path.join(path, "LumpySkin"), exist_ok=True)
    os.makedirs(os.path.join(path, "NormalSkin"), exist_ok=True)

clear_folder(target_train)
clear_folder(target_test)

def process_category(source_dir, category_name):
    files = [f for f in os.listdir(source_dir) if os.path.isfile(os.path.join(source_dir, f))]
    random.seed(42)
    random.shuffle(files)
    
    split = int(len(files) * 0.8)
    train_files = files[:split]
    test_files = files[split:]
    
    # Move train
    for f in train_files:
        shutil.copy(os.path.join(source_dir, f), os.path.join(target_train, category_name, f))
    
    # Move test
    for f in test_files:
        shutil.copy(os.path.join(source_dir, f), os.path.join(target_test, category_name, f))
    
    print(f"Category {category_name}: {len(train_files)} train, {len(test_files)} test.")

process_category(source_lumpy, "LumpySkin")
process_category(source_normal, "NormalSkin")

print("Dataset re-organization complete.")
