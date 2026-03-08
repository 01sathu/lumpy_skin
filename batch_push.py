import os
import subprocess

def push_in_batches(directory, category, batch_size=100):
    path = os.path.join(directory, category)
    if not os.path.exists(path):
        return
    
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    files.sort()
    
    for i in range(0, len(files), batch_size):
        batch = files[i:i+batch_size]
        print(f"Processing {category} batch {i//batch_size + 1}...")
        for f in batch:
            file_path = os.path.join(directory, category, f)
            subprocess.run(['git', 'add', file_path])
        
        subprocess.run(['git', 'commit', '-m', f"Dataset: {category} batch {i//batch_size + 1}"])
        result = subprocess.run(['git', 'push', 'origin', 'main'])
        if result.returncode != 0:
            print(f"Push failed at {category} batch {i//batch_size + 1}. Retrying once...")
            subprocess.run(['git', 'push', 'origin', 'main'])

print("Starting batch push for training data...")
push_in_batches('train', 'NormalSkin', 100)
push_in_batches('train', 'LumpySkin', 100)
print("Batch push complete.")
