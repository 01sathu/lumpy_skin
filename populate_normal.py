import os
import shutil

artifact_dir = r"C:\Users\91725\.gemini\antigravity\brain\d9508514-d902-4d14-ab29-2040a7c34555"
train_normal = r"c:\lumpyskin\train\NormalSkin"
test_normal = r"c:\lumpyskin\test\NormalSkin"

os.makedirs(train_normal, exist_ok=True)
os.makedirs(test_normal, exist_ok=True)

files = [f for f in os.listdir(artifact_dir) if f.startswith("healthy_cow") and f.endswith(".png")]
files.sort()

# Distribute 80/20 approximately
split = int(len(files) * 0.8)
train_files = files[:split]
test_files = files[split:]

for i, f in enumerate(train_files):
    shutil.copy(os.path.join(artifact_dir, f), os.path.join(train_normal, f"h_{i}.png"))

for i, f in enumerate(test_files):
    shutil.copy(os.path.join(artifact_dir, f), os.path.join(test_normal, f"ht_{i}.png"))

print(f"Copied {len(train_files)} to train and {len(test_files)} to test.")
