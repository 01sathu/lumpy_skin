from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
import shutil
import os
from ultralytics import YOLO
import tempfile

app = FastAPI(title="Lumpy Skin Disease Detector")

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "runs", "lumpy_classification", "weights", "best.pt")
STATIC_DIR = os.path.join(BASE_DIR, "web", "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "web", "templates")

# Ensure directories exist
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)

# Load Model
if not os.path.exists(MODEL_PATH):
    # Fallback to a placeholder or generic if not found (though it should be there)
    print(f"Warning: Model not found at {MODEL_PATH}")
    model = None
else:
    model = YOLO(MODEL_PATH)

# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    if not model:
        raise HTTPException(status_code=500, detail="Model not loaded. Please train the model first.")
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name
    
    try:
        # Run inference
        results = model.predict(source=tmp_path, conf=0.25)
        
        # Parse result (Classification)
        result = results[0]
        # YOLOv8cls probs check
        top1_idx = result.probs.top1
        top1_conf = float(result.probs.top1conf)
        class_name = result.names[top1_idx]
        
        # Mapping names if necessary
        # Class 0: LumpySkin, Class 1: NormalSkin (based on folder names in training)
        pretty_name = "Lumpy Skin Disease Detected" if "Lumpy" in class_name else "Healthy - Normal Skin"
        is_healthy = "Normal" in class_name
        
        return {
            "prediction": pretty_name,
            "confidence": f"{top1_conf * 100:.2f}%",
            "is_healthy": is_healthy,
            "class_raw": class_name
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
