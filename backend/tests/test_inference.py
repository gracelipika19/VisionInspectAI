from pathlib import Path

from PIL import Image

from backend.app.config import MODEL_PATH
from backend.app.inference import PCBDefectDetector


def test_model_file_exists():
    assert MODEL_PATH.exists()
    assert MODEL_PATH.is_file()


def test_model_inference():
    detector = PCBDefectDetector(MODEL_PATH)

    # Create a temporary test image
    image_path = Path("backend/tests/test_pcb.jpg")

    image = Image.new(
        "RGB",
        (640, 640),
        color="white",
    )

    image.save(image_path)

    try:
        detections = detector.predict(
            str(image_path)
        )

        assert isinstance(detections, list)

        for detection in detections:
            assert "class_id" in detection
            assert "class_name" in detection
            assert "confidence" in detection
            assert "bbox" in detection

            assert isinstance(
                detection["class_id"],
                int,
            )

            assert isinstance(
                detection["class_name"],
                str,
            )

            assert 0 <= detection["confidence"] <= 1

            assert len(detection["bbox"]) == 4

    finally:
        if image_path.exists():
            image_path.unlink()