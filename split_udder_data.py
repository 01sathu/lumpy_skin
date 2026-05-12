import os
import shutil
import random

BASE_DIR = r"c:\lumpyskin\udder_research\dataset"
TRAIN_DIR = r"c:\lumpyskin\udder_research\train"
TEST_DIR = r"c:\lumpyskin\udder_research\test"
SPLIT_RATIO = 0.8

def create_split():
    for d in [TRAIN_DIR, TEST_DIR]:
        if os.path.exists(d):
            shutil.rmtree(d)
        os.makedirs(d, exist_ok=True)
        
    classes = ["mastitis", "healthy"]
    
    for cls in classes:
        os.makedirs(os.path.join(TRAIN_DIR, cls), exist_ok=True)
        os.makedirs(os.path.join(TEST_DIR, cls), exist_ok=True)
        
        cls_dir = os.path.join(BASE_DIR, cls)
        if not os.path.exists(cls_dir):
            continue
            
        images = [f for f in os.listdir(cls_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        random.shuffle(images)
        
        split_idx = int(len(images) * SPLIT_RATIO)
        train_imgs = images[:split_idx]
        test_imgs = images[split_idx:]
        
        for img in train_imgs:
            shutil.copy(os.path.join(cls_dir, img), os.path.join(TRAIN_DIR, cls, img))
            
        for img in test_imgs:
            shutil.copy(os.path.join(cls_dir, img), os.path.join(TEST_DIR, cls, img))
            
        print(f"Class '{cls}': {len(train_imgs)} train, {len(test_imgs)} test images.")

if __name__ == "__main__":
    create_split()
