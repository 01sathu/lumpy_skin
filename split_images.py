import os
import random
import shutil

# Paths
source_dir = r"c:\lumpyskin"
train_dir = os.path.join(source_dir, "train")
test_dir = os.path.join(source_dir, "test")

# Create directories if they don't exist
os.makedirs(train_dir, exist_ok=True)
os.makedirs(test_dir, exist_ok=True)

# Image extensions to include
image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp')

# Get all image files in the source directory
all_files = [f for f in os.listdir(source_dir) if f.lower().endswith(image_extensions)]

# Shuffle the filenames
random.seed(42)  # For reproducibility
random.shuffle(all_files)

# Calculate split point
split_point = int(len(all_files) * 0.8)

# Split into train and test
train_files = all_files[:split_point]
test_files = all_files[split_point:]

print(f"Total images found: {len(all_files)}")
print(f"Moving {len(train_files)} to train...")
print(f"Moving {len(test_files)} to test...")

# Function to move files
def move_files(files, destination):
    for f in files:
        src_path = os.path.join(source_dir, f)
        dest_path = os.path.join(destination, f)
        try:
            shutil.move(src_path, dest_path)
        except Exception as e:
            print(f"Error moving {f}: {e}")

# Perform the move
move_files(train_files, train_dir)
move_files(test_files, test_dir)

print("Split complete!")
