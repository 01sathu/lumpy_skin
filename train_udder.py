from ultralytics import YOLO

if __name__ == '__main__':
    # Load a model
    model = YOLO('yolov8n-cls.pt')

    # Train the model
    results = model.train(
        data=r'c:\lumpyskin\udder_research',
        epochs=15,
        imgsz=224,
        batch=16,
        project='runs/udder_project',
        name='udder_classification'
    )
