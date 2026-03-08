import os
import shutil
import random

train_dir = r"c:\lumpyskin\train\NormalSkin"
test_dir = r"c:\lumpyskin\test\NormalSkin"

test_files = [f for f in os.listdir(test_dir) if os.path.isfile(os.path.join(test_dir, f))]
# Move 60 images from test to train to balance NormalSkin class
random.seed(42)
to_move = random.sample(test_files, 60)

for f in to_move:
    shutil.move(os.path.join(test_dir, f), os.path.join(train_dir, f))

print(f"Moved {len(to_move)} images from NormalSkin test to train.")
