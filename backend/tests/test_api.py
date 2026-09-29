from io import BytesIO
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from PIL import Image
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.main import app
from backend.app.database import Base, get_db
from backend.app.auth import get_current_user
from backend.app.models import User


# ==================================================
# TEST DATABASE
# ==================================================

TEST_DATABASE_URL = "sqlite://"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
)


# ==================================================
# TEST DATABASE SETUP / CLEANUP
# ==================================================

@pytest.fixture(scope="function", autouse=True)
def setup_test_database():
    """
    Create a fresh SQLite database for every test.
    """

    Base.metadata.create_all(bind=test_engine)

    yield

    Base.metadata.drop_all(bind=test_engine)


def override_get_db():
    """
    Use the isolated SQLite database during tests.
    """

    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


# ==================================================
# TEST AUTHENTICATION
# ==================================================

def override_get_current_user():
    """
    Provide a fake authenticated user for API tests.

    This bypasses real JWT authentication only inside
    the test environment.
    """

    return User(
        id=1,
        username="test_user",
        email="test@example.com",
        hashed_password="test",
        role="QUALITY_ENGINEER",
        is_active=True,
    )


# Apply dependency overrides
app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[
    get_current_user
] = override_get_current_user

client = TestClient(app)


# ==================================================
# HEALTH CHECK
# ==================================================

def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"
    assert data["service"] == "VisionInspect AI"


# ==================================================
# STATISTICS
# ==================================================

def test_get_stats():
    response = client.get("/stats")

    assert response.status_code == 200

    data = response.json()

    assert "total_inspections" in data
    assert "defective_inspections" in data
    assert "passed_inspections" in data
    assert "total_defects" in data
    assert "defect_distribution" in data
    assert "severity_distribution" in data
    assert "decision_distribution" in data


# ==================================================
# INSPECTION HISTORY
# ==================================================

def test_get_inspections():
    response = client.get("/inspections")

    assert response.status_code == 200

    data = response.json()

    assert "total_inspections" in data
    assert "inspections" in data

    assert isinstance(
        data["inspections"],
        list,
    )


# ==================================================
# MISSING INSPECTION
# ==================================================

def test_get_missing_inspection():
    response = client.get(
        "/inspections/999999"
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == "Inspection not found."


# ==================================================
# INVALID FILE VALIDATION
# ==================================================

def test_predict_rejects_invalid_file():
    response = client.post(
        "/predict",
        files={
            "file": (
                "test.txt",
                b"This is not an image.",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400

    data = response.json()

    assert (
        data["detail"]
        == "Unsupported image format. "
           "Use JPG, JPEG, or PNG."
    )


# ==================================================
# VALID IMAGE PREDICTION
# ==================================================

def test_predict_with_valid_image():
    # --------------------------------------------------
    # Create test image
    # --------------------------------------------------

    image = Image.new(
        "RGB",
        (300, 300),
        color="white",
    )

    image_bytes = BytesIO()

    image.save(
        image_bytes,
        format="JPEG",
    )

    image_bytes.seek(0)

    # --------------------------------------------------
    # Mock YOLO detection
    # --------------------------------------------------

    mock_detections = [
        {
            "class_id": 1,
            "class_name": "mouse_bite",
            "confidence": 0.95,
            "bbox": [
                10.0,
                20.0,
                50.0,
                60.0,
            ],
        }
    ]

    # Mock YOLO inference so this test
    # does not run the actual model.
    with patch(
        "backend.app.main.detector.predict",
        return_value=mock_detections,
    ):
        response = client.post(
            "/predict",
            files={
                "file": (
                    "test.jpg",
                    image_bytes,
                    "image/jpeg",
                )
            },
        )

    # --------------------------------------------------
    # Response status
    # --------------------------------------------------

    assert response.status_code == 200

    data = response.json()

    # --------------------------------------------------
    # Basic response validation
    # --------------------------------------------------

    assert "inspection_id" in data
    assert "filename" in data
    assert "inspected_by" in data
    assert "image_width" in data
    assert "image_height" in data
    assert "defect_count" in data
    assert "status" in data
    assert "detections" in data

    # --------------------------------------------------
    # Quality assessment fields
    # --------------------------------------------------

    assert "severity" in data
    assert "risk" in data
    assert "decision" in data
    assert "recommendation" in data

    # --------------------------------------------------
    # Image information
    # --------------------------------------------------

    assert data["filename"] == "test.jpg"
    assert data["image_width"] == 300
    assert data["image_height"] == 300

    # --------------------------------------------------
    # User information
    # --------------------------------------------------

    assert data["inspected_by"] == "test_user"

    # --------------------------------------------------
    # Inspection result
    # --------------------------------------------------

    assert data["defect_count"] == 1
    assert data["status"] == "DEFECTIVE"

    # 0.95 confidence falls into the
    # CRITICAL / HIGH / REJECT category
    # according to quality.py.
    assert data["severity"] == "CRITICAL"
    assert data["risk"] == "HIGH"
    assert data["decision"] == "REJECT"
    assert data["recommendation"] == "Reject PCB"

    # --------------------------------------------------
    # Detection information
    # --------------------------------------------------

    assert len(data["detections"]) == 1

    detection = data["detections"][0]

    assert detection["class_id"] == 1
    assert detection["class_name"] == "mouse_bite"
    assert detection["confidence"] == 0.95

    assert detection["bbox"] == [
        10.0,
        20.0,
        50.0,
        60.0,
    ]