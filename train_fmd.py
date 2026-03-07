from ultralytics import YOLO
import os

# Path to the FMD dataset
data_path = r"c:\lumpyskin\fmd_research"

# Initialize model
model = YOLO('yolov8s-cls.pt')

print("Starting training for Foot and Mouth Disease (FMD) classification...")

# Train the model
results = model.train(
    data=data_path, 
    epochs=100,
    imgsz=224, 
    project=r"c:\lumpyskin\runs\fmd_project",
    name="fmd_classification",
    patience=20,
    batch=16,
    augment=True,
    exist_ok=True
)

print(f"Training complete. Results saved in c:\\lumpyskin\\runs\\fmd_project\\fmd_classification")

# Validation
print("Running validation...")
metrics = model.val()
print(f"FMD Top-1 Accuracy: {metrics.top1}")
