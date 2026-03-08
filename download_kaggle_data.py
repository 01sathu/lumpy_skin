import kagglehub
import os
import shutil

# Download the dataset
path = kagglehub.dataset_download("vencerlanz09/cattle-diseases-datasets")

print(f"Dataset downloaded to: {path}")

# Source folder for FMD
# Based on search, it should have a 'foot-and-mouth' folder.
# Let's list the directory contents first.
for root, dirs, files in os.walk(path):
    if dirs:
        print(f"Current Dir: {root}")
        print(f"Subdirs: {dirs}")
        # Stop after first level of dirs to keep it clean
        break

# We will move only the foot-and-mouth images to our project
target_dir = r"c:\lumpyskin\downloads\kaggle_fmd"
os.makedirs(target_dir, exist_ok=True)

# Find 'foot-and-mouth' or 'FMD' directory
found = False
for root, dirs, files in os.walk(path):
    for d in dirs:
        if "foot" in d.lower() and "mouth" in d.lower():
            source_path = os.path.join(root, d)
            print(f"Found FMD directory: {source_path}")
            # Copy all images
            for f in os.listdir(source_path):
                if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                    shutil.copy(os.path.join(source_path, f), os.path.join(target_dir, f))
            found = True
            break
    if found: break

if found:
    count = len(os.listdir(target_dir))
    print(f"Successfully extracted {count} FMD images to {target_dir}")
else:
    print("Could not find FMD directory in the downloaded dataset.")
