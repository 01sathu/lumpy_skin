import os
from PIL import Image, ImageDraw, ImageFont
import random

BASE_DIR = r"c:\lumpyskin\udder_research\dataset"

def generate_images(cls_name, color_range, count=50):
    os.makedirs(os.path.join(BASE_DIR, cls_name), exist_ok=True)
    for i in range(count):
        # vary color slightly
        r = random.randint(color_range[0][0], color_range[1][0])
        g = random.randint(color_range[0][1], color_range[1][1])
        b = random.randint(color_range[0][2], color_range[1][2])
        
        img = Image.new('RGB', (224, 224), color=(r,g,b))
        d = ImageDraw.Draw(img)
        d.text((10,10), f"{cls_name} sample {i}", fill=(255,255,255))
        
        # Add some noise/spots to simulate different textures
        for _ in range(20):
            x = random.randint(0, 224)
            y = random.randint(0, 224)
            rad = random.randint(5, 15)
            d.ellipse([x, y, x+rad, y+rad], fill=(r-20, g-20, b-20))
            
        img.save(os.path.join(BASE_DIR, cls_name, f"{cls_name}_{i}.jpg"))

if __name__ == "__main__":
    # Mastitis: reddish, inflamed simulated colors
    generate_images("mastitis", [(150, 50, 50), (220, 100, 100)], count=60)
    # Healthy: normal pinkish/tan simulated colors
    generate_images("healthy", [(200, 150, 150), (240, 200, 200)], count=60)
    print("Synthetic dataset generated.")
