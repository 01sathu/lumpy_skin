from ultralytics import YOLO
import os

# Path to the dataset (relative to the script location)
data_path = os.path.dirname(os.path.abspath(__file__))

# Use YOLOv8-Small classification model for better feature extraction (still fast, but more accurate)
model = YOLO('yolov8s-cls.pt')

# Train the model with higher resolution and advanced hyperparameters for IEEE standards
print("Starting final research-grade training for 95%+ Accuracy...")
results = model.train(
    data=data_path, 
    epochs=150,      # More epochs for deep learning
    imgsz=416,      # High resolution for skin pathologies
    project=r'c:\lumpyskin\runs', 
    name='lumpy_classification',
    patience=50,     # Allow more time to escape local minima
    batch=16,       # Stable gradients
    lr0=0.005,      # Stable starting LR
    augment=True,    # Use built-in classification augmentations
    exist_ok=True    # Overwrite/Refine existing run
)

print("Training complete. Results saved in c:\\lumpyskin\\runs\\lumpy_classification")

# Run validation/testing
print("Running validation on test set...")
metrics = model.val()

print(f"Top-1 Accuracy: {metrics.top1}")
print(f"Top-5 Accuracy: {metrics.top5}")

# Run prediction on a few test images to show output
test_lumpy_dir = os.path.join(data_path, 'test', 'LumpySkin')
test_files = [os.path.join(test_lumpy_dir, f) for f in os.listdir(test_lumpy_dir)[:3]]

print("Running inference on 3 test images...")
preds = model.predict(source=test_files)

for i, r in enumerate(preds):
    print(f"Image {i}: Predicted class {r.probs.top1} with confidence {r.probs.top1conf:.2f}")

print("All tasks completed.")
