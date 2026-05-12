from bing_image_downloader import downloader
import os
import shutil

BASE_DIR = r"c:\lumpyskin\udder_research\dataset"
os.makedirs(BASE_DIR, exist_ok=True)

# We will download images directly into the dataset folder.
# bing_image_downloader creates its own folders, we can reorganize.

queries = {
    "mastitis": ["bovine mastitis udder", "cow mastitis disease"],
    "healthy": ["healthy cow udder close up", "normal cow teat"]
}

for cls, q_list in queries.items():
    cls_dir = os.path.join(BASE_DIR, cls)
    os.makedirs(cls_dir, exist_ok=True)
    
    for q in q_list:
        print(f"Downloading {q} for {cls}...")
        downloader.download(q, limit=40, output_dir=BASE_DIR, adult_filter_off=False, force_replace=False, timeout=10)
        
        # Move images from the query folder to the class folder
        downloaded_folder = os.path.join(BASE_DIR, q)
        if os.path.exists(downloaded_folder):
            for i, f in enumerate(os.listdir(downloaded_folder)):
                src = os.path.join(downloaded_folder, f)
                # Create unique name
                dst = os.path.join(cls_dir, f"{q.replace(' ', '_')}_{i}.jpg")
                if not os.path.exists(dst):
                    shutil.move(src, dst)
            shutil.rmtree(downloaded_folder)

print("Finished downloading images!")
