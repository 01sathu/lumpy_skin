import os
import shutil
import random

# Source paths from the Zenodo download
source_base = r"c:\lumpyskin\downloads\FMD_Cattle\FMD_Cattle"
source_diseased = os.path.join(source_base, "1")
source_healthy = os.path.join(source_base, "0")

# Target research paths (within workspace)
target_base = r"c:\lumpyskin\fmd_research"
target_train = os.path.join(target_base, "train")
target_test = os.path.join(target_base, "test")

def setup_dirs():
    for base in [target_train, target_test]:
        for cat in ["FootAndMouth", "NormalSkin"]:
            path = os.path.join(base, cat)
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)
            else:
                # Clear existing files to ensure a clean split
                for f in os.listdir(path):
                    file_path = os.path.join(path, f)
                    if os.path.isfile(file_path):
                        os.remove(file_path)

def process_category(source_dir, cat_name):
    files = [f for f in os.listdir(source_dir) if os.path.isfile(os.path.join(source_dir, f))]
    random.seed(42)
    random.shuffle(files)
    
    # 80/20 split
    split = int(len(files) * 0.8)
    train_files = files[:split]
    test_files = files[split:]
    
    for f in train_files:
        shutil.copy(os.path.join(source_dir, f), os.path.join(target_train, cat_name, f))
    
    for f in test_files:
        shutil.copy(os.path.join(source_dir, f), os.path.join(target_test, cat_name, f))
    
    print(f"Processed {cat_name}: {len(train_files)} training, {len(test_files)} testing.")

if __name__ == "__main__":
    setup_dirs()
    process_category(source_diseased, "FootAndMouth")
    process_category(source_healthy, "NormalSkin")
    print("FMD Project Dataset Ready in c:\\lumpyskin\\fmd_research")
