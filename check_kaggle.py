import kagglehub
import os

path = kagglehub.dataset_download("vencerlanz09/cattle-diseases-datasets")
print(f"Dataset downloaded to: {path}")

for root, dirs, files in os.walk(path):
    if dirs:
        print(f"Current Dir: {root}")
        print(f"Subdirs: {dirs}")
        break
