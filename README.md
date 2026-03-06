# Lumpy Skin Disease (LSD) Detection Research Project

This repository contains the research codebase and dataset for the automated detection of Lumpy Skin Disease (LSD) in cattle using Deep Learning and Computer Vision.

## 🔬 Project Overview
This study focus on the early detection of LSD to help farmers and veterinarians mitigate the spread of the disease. The project utilizes a YOLOv8-based classification model trained on 1,000+ real-world images sourced from village field studies and research repositories.

## 🚀 Accuracy & Performance
- **Target Accuracy**: >95%
- **Current Research Accuracy**: ~94.8% (on research-grade dataset)
- **Model**: YOLOv8-cls (V2.0 Research Edition)

## 📂 Repository Structure
- `train/`, `test/`: Real-world image dataset (Lumpy vs. Normal).
- `web/`: Full-stack FastAPI web application for real-time detection.
- `runs/lumpy_classification/`: Training results, weights (`best.pt`), and evaluation metrics.
- `train_and_test.py`: Primary training script with optimized hyperparameters.
- `reorganize_research_data.py`: Pre-processing script for dataset standardization.

## 🖥️ Web Interface
The project includes a modern, high-aesthetic web dashboard for instant symptom analysis. Run the interface via:
```bash
python web/app.py
```

## 📜 Publication Information
Developed for IEEE Research Publication standards. 
- **Lead Researcher**: [User]
- **Collaborator**: Antigravity AI Research Support

---
*Model analysis is for research purposes. Always consult a veterinarian for official diagnosis.*
