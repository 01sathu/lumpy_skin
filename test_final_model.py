from ultralytics import YOLO
import os

model = YOLO(r"c:\lumpyskin\runs\lumpy_classification\weights\best.pt")
test_dir = r"C:\Users\91725\.gemini\antigravity\brain\8f4feceb-7bcf-41f6-9847-def653eb6459"
images = ["healthy_cow_mud_splashes_1772693450072.png", "healthy_cow_small_scars_flies_not_lsd_skin_detail_1772693470115.png"]

for img in images:
    path = os.path.join(test_dir, img)
    if os.path.exists(path):
        results = model.predict(source=path, conf=0.25)
        for r in results:
            class_idx = r.probs.top1
            class_name = r.names[class_idx]
            conf = r.probs.top1conf
            print(f"Image: {img} -> Predicted: {class_name} ({conf:.2f}%)")
