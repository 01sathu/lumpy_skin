from ultralytics import YOLO
import os

# Path to the dataset (relative to the script location)
data_path = os.path.dirname(os.path.abspath(__file__))

# Use YOLOv8 classification model (nano version for speed)
model = YOLO('yolov8n-cls.pt')

# Train the model
# We increase epochs to 100 and use patience to stop when it stops improving.
# 5 epochs was not enough for the model to distinguish between classes.
# Train the model 
# Increased imgsz to 320 for better detail from real photographs.
# Epochs set to 100 with patience for optimal training.
print("Starting research-grade training...")
results = model.train(
    data=data_path, 
    epochs=100, 
    imgsz=320, 
    project=r'c:\lumpyskin\runs', 
    name='lumpy_classification',
    patience=20,  # Early stopping
    batch=32,    # Standard batch size
    exist_ok=True # Overwrite existing run
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
