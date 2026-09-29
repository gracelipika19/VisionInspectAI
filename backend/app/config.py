from pathlib import Path


# VisionInspectAI/
# ├── backend/
# │   └── app/
# │       └── config.py
# └── models/
#     └── best.pt

PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODEL_PATH = PROJECT_ROOT / "models" / "best.pt"

IMAGE_SIZE = 1280
CONFIDENCE_THRESHOLD = 0.25