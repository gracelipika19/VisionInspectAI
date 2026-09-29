from pathlib import Path

from ultralytics import YOLO

from .config import (
    MODEL_PATH,
    IMAGE_SIZE,
    CONFIDENCE_THRESHOLD,
)


class PCBDefectDetector:
    def __init__(self, model_path: Path):
        if not model_path.exists():
            raise FileNotFoundError(
                f"YOLO model not found: {model_path}"
            )

        self.model = YOLO(str(model_path))

    def predict(self, image_path: str):
        results = self.model.predict(
            source=image_path,
            imgsz=512,
            conf=CONFIDENCE_THRESHOLD,
            device="cpu",
            verbose=False,
        )

        result = results[0]

        detections = []

        if result.boxes is not None:
            for cls, conf, box in zip(
                result.boxes.cls,
                result.boxes.conf,
                result.boxes.xyxy,
            ):
                class_id = int(cls.item())
                confidence = float(conf.item())

                x1, y1, x2, y2 = [
                    round(float(value), 2)
                    for value in box.tolist()
                ]

                detections.append(
                    {
                        "class_id": class_id,
                        "class_name": self.model.names[class_id],
                        "confidence": round(confidence, 4),
                        "bbox": [x1, y1, x2, y2],
                    }
                )

        return detections


detector = PCBDefectDetector(MODEL_PATH)