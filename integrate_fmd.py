import os
import shutil
import random

# Paths
source_fmd_0 = r"c:\lumpyskin\downloads\FMD_Cattle\FMD_Cattle\0" # Healthy in FMD dataset
source_fmd_1 = r"c:\lumpyskin\downloads\FMD_Cattle\FMD_Cattle\1" # Diseased in FMD dataset

target_base = r"c:\lumpyskin"
target_train = os.path.join(target_base, "train")
target_test = os.path.join(target_base, "test")

# Ensure categories exist
categories = ["LumpySkin", "NormalSkin", "FootAndMouth"]
for d in [target_train, target_test]:
    for cat in categories:
        os.makedirs(os.path.join(d, cat), exist_ok=True)

def process_fmd(source_dir, category_name):
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
    
    print(f"Added to {category_name}: {len(train_files)} train, {len(test_files)} test.")

# Map FMD dataset '1' to FootAndMouth
process_fmd(source_fmd_1, "FootAndMouth")
# Map FMD dataset '0' to NormalSkin (supplementing current NormalSkin)
process_fmd(source_fmd_0, "NormalSkin")

print("FMD data integration complete.")
