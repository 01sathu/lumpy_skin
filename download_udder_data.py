import os
import requests
from duckduckgo_search import DDGS
from concurrent.futures import ThreadPoolExecutor

CLASSES = {
    "mastitis": ["bovine mastitis udder", "cow mastitis infection", "cow udder disease mastitis"],
    "healthy": ["healthy cow udder close up", "normal cow udder", "clean cow teat"]
}

BASE_DIR = r"c:\lumpyskin\udder_research\dataset"

def download_image(url, save_path):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            with open(save_path, "wb") as f:
                f.write(response.content)
            return True
    except Exception:
        pass
    return False

def collect_data():
    os.makedirs(BASE_DIR, exist_ok=True)
    with DDGS() as ddgs:
        for cls, queries in CLASSES.items():
            class_dir = os.path.join(BASE_DIR, cls)
            os.makedirs(class_dir, exist_ok=True)
            print(f"Collecting images for {cls}...")
            
            urls = []
            for query in queries:
                try:
                    results = ddgs.images(query, max_results=80)
                    urls.extend([r["image"] for r in results])
                except Exception as e:
                    print(f"Error fetching for query {query}: {e}")
            
            urls = list(set(urls))[:200]
            
            print(f"Found {len(urls)} URLs for {cls}, downloading...")
            
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = []
                for idx, url in enumerate(urls):
                    save_path = os.path.join(class_dir, f"{cls}_{idx}.jpg")
                    futures.append(executor.submit(download_image, url, save_path))
                
                successes = sum(f.result() for f in futures)
            
            print(f"Successfully downloaded {successes} images for {cls}.")

if __name__ == "__main__":
    collect_data()
