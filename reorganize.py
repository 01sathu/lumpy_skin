import os
import shutil

base_dir = r"c:\lumpyskin"
train_dir = os.path.join(base_dir, "train")
test_dir = os.path.join(base_dir, "test")

# Re-organize Lumpy images into subdirectories
def organize_lumpy(directory):
    lumpy_subdir = os.path.join(directory, "LumpySkin")
    os.makedirs(lumpy_subdir, exist_ok=True)
    for f in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, f)) and f.lower().endswith(('.jpg', '.jpeg', '.png')):
            shutil.move(os.path.join(directory, f), os.path.join(lumpy_subdir, f))

organize_lumpy(train_dir)
organize_lumpy(test_dir)

print("Re-organization complete.")
