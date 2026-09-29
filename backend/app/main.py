from pathlib import Path
import io
import uuid

from fastapi import (
    Depends,
    FastAPI,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, UnidentifiedImageError
from sqlalchemy import func
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from . import models
from .auth import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from .inference import detector
from .quality import assess_inspection


# ==================================================
# DATABASE INITIALIZATION
# ==================================================

Base.metadata.create_all(bind=engine)


# ==================================================
# FASTAPI APPLICATION
# ==================================================

app = FastAPI(
    title="VisionInspect AI",
    description="PCB Manufacturing Defect Detection API",
    version="1.0.0",
)


# ==================================================
# CORS
# ==================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://visioninspect-frontend-gta6.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================================================
# UPLOAD CONFIGURATION
# ==================================================

UPLOAD_DIR = Path("backend/uploads")

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

# Maximum uploaded image size: 10 MB
MAX_UPLOAD_SIZE = 10 * 1024 * 1024

ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
}

ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
}


# ==================================================
# HEALTH CHECK
# ==================================================

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "VisionInspect AI",
    }


# ==================================================
# AUTHENTICATION
# ==================================================

@app.post("/auth/register")
def register(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    role: str = Form("QUALITY_ENGINEER"),
    db: Session = Depends(get_db),
):
    """
    Register a new VisionInspect AI user.
    """

    allowed_roles = {
        "QUALITY_ENGINEER",
        "SUPERVISOR",
    }

    role = role.upper()

    if role not in allowed_roles:
        raise HTTPException(
            status_code=400,
            detail="Invalid role.",
        )

    # --------------------------------------------------
    # Check username
    # --------------------------------------------------

    existing_username = (
        db.query(models.User)
        .filter(
            models.User.username == username
        )
        .first()
    )

    if existing_username:
        raise HTTPException(
            status_code=400,
            detail="Username already registered.",
        )

    # --------------------------------------------------
    # Check email
    # --------------------------------------------------

    existing_email = (
        db.query(models.User)
        .filter(
            models.User.email == email
        )
        .first()
    )

    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Email already registered.",
        )

    # --------------------------------------------------
    # Create user
    # --------------------------------------------------

    user = models.User(
        username=username,
        email=email,
        hashed_password=hash_password(password),
        role=role,
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "message": "User registered successfully.",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
        },
    }


# ==================================================
# LOGIN
# ==================================================

@app.post("/auth/login")
def login(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    """
    Authenticate a user and return a JWT access token.
    """

    user = (
        db.query(models.User)
        .filter(
            models.User.username == username
        )
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password.",
        )

    if not verify_password(
        password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="Inactive user.",
        )

    access_token = create_access_token(
        data={
            "sub": user.username,
            "role": user.role,
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
        },
    }


# ==================================================
# CURRENT USER
# ==================================================

@app.get("/auth/me")
def get_me(
    current_user: models.User = Depends(
        get_current_user
    ),
):
    """
    Return the currently authenticated user.
    """

    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role,
        "is_active": current_user.is_active,
    }


# ==================================================
# PREDICTION / INSPECTION
# ==================================================

@app.post("/predict")
async def predict(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(
        get_current_user
    ),
):
    """
    Run YOLO defect detection on an uploaded PCB image.

    Authentication required.

    Workflow:
        Upload
        -> File Validation
        -> Image Validation
        -> YOLO Inference
        -> Defect Detection
        -> Quality Assessment
        -> Database Storage
        -> Response
    """

    image_path = None

    try:

        # --------------------------------------------------
        # Validate filename
        # --------------------------------------------------

        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="A filename is required.",
            )

        # --------------------------------------------------
        # Validate file extension
        # --------------------------------------------------

        extension = Path(
            file.filename
        ).suffix.lower()

        if extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Unsupported image format. "
                    "Use JPG, JPEG, or PNG."
                ),
            )

        # --------------------------------------------------
        # Validate declared MIME type
        # --------------------------------------------------

        if file.content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Unsupported content type. "
                    "Use JPEG or PNG images."
                ),
            )

        # --------------------------------------------------
        # Read uploaded file
        # --------------------------------------------------

        contents = await file.read()

        # --------------------------------------------------
        # Validate file is not empty
        # --------------------------------------------------

        if len(contents) == 0:
            raise HTTPException(
                status_code=400,
                detail="Uploaded image is empty.",
            )

        # --------------------------------------------------
        # Validate file size
        # --------------------------------------------------

        if len(contents) > MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=413,
                detail=(
                    "Image is too large. "
                    "Maximum allowed size is 10 MB."
                ),
            )

        # --------------------------------------------------
        # Validate actual image contents
        # --------------------------------------------------

        try:

            # First verify that the bytes represent
            # a valid image.
            with Image.open(
                io.BytesIO(contents)
            ) as image:
                image.verify()

            # verify() closes the image state, so
            # reopen the bytes to safely obtain dimensions.
            with Image.open(
                io.BytesIO(contents)
            ) as image:
                image_width, image_height = image.size

        except (
            UnidentifiedImageError,
            OSError,
        ):
            raise HTTPException(
                status_code=400,
                detail="Invalid or corrupted image file.",
            )

        # --------------------------------------------------
        # Generate unique filename
        # --------------------------------------------------

        unique_filename = (
            f"{uuid.uuid4().hex}{extension}"
        )

        image_path = (
            UPLOAD_DIR / unique_filename
        )

        # --------------------------------------------------
        # Save validated image
        # --------------------------------------------------

        with image_path.open("wb") as buffer:
            buffer.write(contents)

        # --------------------------------------------------
        # YOLO inference
        # --------------------------------------------------

        detections = detector.predict(
            str(image_path)
        )

        # --------------------------------------------------
        # Basic inspection status
        # --------------------------------------------------

        status = (
            "DEFECTIVE"
            if detections
            else "PASS"
        )

        # --------------------------------------------------
        # Quality assessment
        # --------------------------------------------------

        quality_result = assess_inspection(
            detections
        )

        # --------------------------------------------------
        # Create inspection record
        # --------------------------------------------------

        inspection = models.Inspection(
            filename=file.filename,
            status=status,
            defect_count=len(detections),

            severity=quality_result["severity"],
            risk=quality_result["risk"],
            decision=quality_result["decision"],
            recommendation=quality_result[
                "recommendation"
            ],
        )

        db.add(inspection)

        # Get generated inspection ID
        db.flush()

        # --------------------------------------------------
        # Store individual detections
        # --------------------------------------------------

        for detection in detections:

            x1, y1, x2, y2 = detection["bbox"]

            detection_record = models.Detection(
                inspection_id=inspection.id,
                class_id=detection["class_id"],
                class_name=detection["class_name"],
                confidence=detection["confidence"],
                x1=x1,
                y1=y1,
                x2=x2,
                y2=y2,
            )

            db.add(detection_record)

        # --------------------------------------------------
        # Commit transaction
        # --------------------------------------------------

        db.commit()

        # --------------------------------------------------
        # Return inspection result
        # --------------------------------------------------

        return {
            "inspection_id": inspection.id,
            "filename": file.filename,
            "inspected_by": current_user.username,

            "image_width": image_width,
            "image_height": image_height,

            "defect_count": len(detections),
            "status": status,

            "severity": quality_result["severity"],
            "risk": quality_result["risk"],
            "decision": quality_result["decision"],
            "recommendation": quality_result[
                "recommendation"
            ],

            "detections": detections,
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise

    finally:

        # --------------------------------------------------
        # Delete temporary uploaded image
        # --------------------------------------------------

        if (
            image_path is not None
            and image_path.exists()
        ):
            image_path.unlink()


# ==================================================
# INSPECTION HISTORY
# ==================================================

@app.get("/inspections")
def get_inspections(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(
        get_current_user
    ),
):
    """
    Return inspection history.

    Authentication required.
    """

    inspections = (
        db.query(models.Inspection)
        .order_by(
            models.Inspection.inspected_at.desc()
        )
        .all()
    )

    results = []

    for inspection in inspections:

        results.append(
            {
                "inspection_id": inspection.id,
                "filename": inspection.filename,
                "status": inspection.status,
                "defect_count": inspection.defect_count,

                "severity": inspection.severity,
                "risk": inspection.risk,
                "decision": inspection.decision,
                "recommendation": (
                    inspection.recommendation
                ),

                "inspected_at": inspection.inspected_at,

                "detections": [
                    {
                        "class_id": detection.class_id,
                        "class_name": detection.class_name,
                        "confidence": detection.confidence,
                        "bbox": [
                            detection.x1,
                            detection.y1,
                            detection.x2,
                            detection.y2,
                        ],
                    }
                    for detection
                    in inspection.detections
                ],
            }
        )

    return {
        "total_inspections": len(results),
        "inspections": results,
    }


# ==================================================
# SINGLE INSPECTION
# ==================================================

@app.get("/inspections/{inspection_id}")
def get_inspection(
    inspection_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(
        get_current_user
    ),
):
    """
    Return a single inspection.

    Authentication required.
    """

    inspection = (
        db.query(models.Inspection)
        .filter(
            models.Inspection.id
            == inspection_id
        )
        .first()
    )

    if inspection is None:
        raise HTTPException(
            status_code=404,
            detail="Inspection not found.",
        )

    return {
        "inspection_id": inspection.id,
        "filename": inspection.filename,
        "status": inspection.status,
        "defect_count": inspection.defect_count,

        "severity": inspection.severity,
        "risk": inspection.risk,
        "decision": inspection.decision,
        "recommendation": inspection.recommendation,

        "inspected_at": inspection.inspected_at,

        "detections": [
            {
                "class_id": detection.class_id,
                "class_name": detection.class_name,
                "confidence": detection.confidence,
                "bbox": [
                    detection.x1,
                    detection.y1,
                    detection.x2,
                    detection.y2,
                ],
            }
            for detection
            in inspection.detections
        ],
    }


# ==================================================
# STATISTICS
# ==================================================

@app.get("/stats")
def get_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(
        get_current_user
    ),
):
    """
    Return inspection and defect statistics.

    Authentication required.
    """

    # --------------------------------------------------
    # Inspection counts
    # --------------------------------------------------

    total_inspections = (
        db.query(models.Inspection)
        .count()
    )

    defective_inspections = (
        db.query(models.Inspection)
        .filter(
            models.Inspection.status
            == "DEFECTIVE"
        )
        .count()
    )

    passed_inspections = (
        db.query(models.Inspection)
        .filter(
            models.Inspection.status
            == "PASS"
        )
        .count()
    )

    # --------------------------------------------------
    # Total defects
    # --------------------------------------------------

    total_defects = (
        db.query(models.Detection)
        .count()
    )

    # --------------------------------------------------
    # Defect distribution
    # --------------------------------------------------

    defect_distribution = (
        db.query(
            models.Detection.class_name,
            func.count(
                models.Detection.id
            ),
        )
        .group_by(
            models.Detection.class_name
        )
        .all()
    )

    defect_counts = {
        class_name: count
        for class_name, count
        in defect_distribution
    }

    # --------------------------------------------------
    # Severity distribution
    # --------------------------------------------------

    severity_distribution = (
        db.query(
            models.Inspection.severity,
            func.count(
                models.Inspection.id
            ),
        )
        .group_by(
            models.Inspection.severity
        )
        .all()
    )

    severity_counts = {
        severity: count
        for severity, count
        in severity_distribution
    }

    # --------------------------------------------------
    # Decision distribution
    # --------------------------------------------------

    decision_distribution = (
        db.query(
            models.Inspection.decision,
            func.count(
                models.Inspection.id
            ),
        )
        .group_by(
            models.Inspection.decision
        )
        .all()
    )

    decision_counts = {
        decision: count
        for decision, count
        in decision_distribution
    }

    # --------------------------------------------------
    # Response
    # --------------------------------------------------

    return {
        "total_inspections": total_inspections,
        "defective_inspections": defective_inspections,
        "passed_inspections": passed_inspections,
        "total_defects": total_defects,

        "defect_distribution": defect_counts,

        "severity_distribution": severity_counts,

        "decision_distribution": decision_counts,
    }