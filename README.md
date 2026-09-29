# VisionInspect AI

### AI-Powered PCB Defect Detection & Quality Inspection System

[![GitHub Repository](https://img.shields.io/badge/GitHub-VisionInspectAI-black?logo=github)](https://github.com/gracelipika19/VisionInspectAI)
![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-Vite-61DAFB?logo=react&logoColor=black)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)
![Tests](https://img.shields.io/badge/tests-8%20passed-brightgreen)

I built **VisionInspect AI** as an end-to-end computer vision quality inspection system for detecting and localizing manufacturing defects on Printed Circuit Boards (PCBs).

The project combines a custom-trained **YOLO11s object detection model** with a **FastAPI backend, PostgreSQL database, JWT authentication, role-based access control, and React frontend** to create a complete PCB inspection workflow.

The system allows users to upload PCB images, automatically detect defects, visualize their locations, assess inspection severity, store results, and review previous inspections.

---

## 📑 Table of Contents

- [Project Links](#-project-links)
- [What I Built](#-what-i-built)
- [Application Screenshots](#-application-screenshots)
- [Architecture](#-architecture)
- [Inspection Workflow](#-inspection-workflow)
- [PCB Defects Detected](#-pcb-defects-detected)
- [YOLO11s Model](#-yolo11s-model)
- [Model Performance](#-model-performance)
- [Quality Assessment](#-quality-assessment)
- [Authentication & Role-Based Access](#-authentication--role-based-access)
- [PostgreSQL Database](#%EF%B8%8F-postgresql-database)
- [FastAPI Backend](#-fastapi-backend)
- [Image Validation](#%EF%B8%8F-image-validation)
- [React Frontend](#%EF%B8%8F-react-frontend)
- [Docker](#-docker)
- [Testing](#-testing)
- [Running the Project Locally](#%EF%B8%8F-running-the-project-locally)
- [Security](#-security)
- [Limitations](#%EF%B8%8F-limitations)
- [Future Improvements](#-future-improvements)

---

## 🔗 Project Links

- **GitHub Repository:** [VisionInspectAI](https://github.com/gracelipika19/VisionInspectAI)
- **Live Demo:** https://visioninspect-frontend-gta6.onrender.com
- **Backend API:**  https://visioninspectai-rtft.onrender.com

---

## 🚀 What I Built

- Trained a YOLO11s model to detect **6 types of PCB defects**
- Built an image inspection pipeline for PCB defect detection and localization
- Developed a **FastAPI REST API** for model inference and inspection management
- Added image validation before running inference
- Implemented **JWT-based authentication**
- Implemented role-based authorization for Quality Engineers and Supervisors
- Designed PostgreSQL tables for users, inspections, and individual detections
- Built a React dashboard for uploading PCB images and viewing inspection results
- Added bounding-box visualization for detected defects
- Implemented confidence-based severity, risk, and quality decisions
- Added inspection history and detailed inspection views
- Containerized the backend using Docker
- Added automated backend tests using Pytest
- Built the React frontend for production using Vite

---

## 🖼️ Application Screenshots

### AI-Powered PCB Inspection

The system accepts a PCB image and uses the trained YOLO11 model to detect and localize manufacturing defects with confidence scores.

![AI-Powered PCB Inspection](docs/screenshots/ai-inspection.png)

### Quality Inspection Dashboard

The dashboard provides an overview of inspection activity and defect distribution across inspected PCBs.

![Quality Inspection Dashboard](docs/screenshots/dashboard.png)

### Inspection Result & Quality Assessment

Each inspection produces a persistent quality assessment including severity, risk, decision, recommendation, and detected defects.

![Inspection Result and Quality Assessment](docs/screenshots/inspection-result.png)

---

## 🏗️ Architecture

```text
                    ┌──────────────────────────┐
                    │      React Frontend      │
                    │        Vite + React      │
                    │                          │
                    │  Login / Dashboard       │
                    │  New Inspection          │
                    │  History / Details       │
                    │  Detection Visualization │
                    └────────────┬─────────────┘
                                 │
                              REST API
                                 │
                    ┌────────────▼─────────────┐
                    │      FastAPI Backend     │
                    │                          │
                    │ JWT Authentication       │
                    │ Role Authorization       │
                    │ Image Validation         │
                    │ YOLO11s Inference        │
                    │ Quality Assessment       │
                    └────────────┬─────────────┘
                                 │
                    ┌────────────┴─────────────┐
                    │                          │
          ┌─────────▼─────────┐     ┌─────────▼─────────┐
          │      YOLO11s      │     │    PostgreSQL     │
          │      best.pt      │     │                   │
          │                   │     │ Users             │
          │ 6 Defect Classes  │     │ Inspections       │
          │ Bounding Boxes    │     │ Detections        │
          └───────────────────┘     └───────────────────┘
```

---

## 🔄 Inspection Workflow

I designed the inspection pipeline around the following workflow:

```text
User Login
    ↓
Upload PCB Image
    ↓
Image Validation
    ↓
YOLO11s Inference
    ↓
Defect Detection & Localization
    ↓
Confidence-Based Assessment
    ↓
Severity / Risk Evaluation
    ↓
Quality Decision
    ↓
Store Inspection & Detections
    ↓
View Results / History / Analytics
```

---

## 🔍 PCB Defects Detected

I trained the model to detect six PCB defect categories:

| Class ID | Defect          |
|:--------:|-----------------|
| 0        | Missing Hole    |
| 1        | Mouse Bite      |
| 2        | Open Circuit    |
| 3        | Short           |
| 4        | Spur            |
| 5        | Spurious Copper |

For each detection, the model returns:

- Defect class
- Confidence score
- Bounding-box coordinates

---

## 🤖 YOLO11s Model

I trained a YOLO11s object detection model using the Ultralytics framework and PyTorch.

### Training Configuration

| Parameter        | Value            |
|------------------|------------------|
| Model            | YOLO11s          |
| Image Size       | 1280             |
| Epochs           | 50               |
| Batch Size       | 4                |
| Training Device  | NVIDIA Tesla T4  |
| Random Seed      | 42               |
| Dataset Split    | 70 / 20 / 10     |

The trained model is stored as:

```text
models/best.pt
```

---

## 📊 Model Performance

I evaluated the trained model on a held-out test set containing:

- **72 images**
- **304 annotated objects**

### Test Results

| Metric        | Result |
|---------------|-------:|
| Precision     | 98.0%  |
| Recall        | 98.8%  |
| mAP@50        | 98.9%  |
| mAP@50-95     | 58.3%  |

> These are object-detection evaluation metrics. I use **mAP@50** rather than describing the result as classification accuracy.

### Per-Class Performance

| Defect          | Precision | Recall | mAP@50 | mAP@50-95 |
|-----------------|----------:|-------:|-------:|----------:|
| Missing Hole    | 97.2%     | 100.0% | 98.0%  | 60.0%     |
| Mouse Bite      | 98.2%     | 99.5%  | 99.5%  | 58.7%     |
| Open Circuit    | 99.8%     | 97.7%  | 99.0%  | 61.0%     |
| Short           | 99.3%     | 100.0% | 99.5%  | 57.0%     |
| Spur            | 95.3%     | 96.2%  | 98.4%  | 56.3%     |
| Spurious Copper | 98.2%     | 99.7%  | 99.0%  | 56.6%     |

---

## 🧠 Quality Assessment

After YOLO inference, I added a **rule-based quality assessment layer**.

The YOLO model provides the defect confidence score, and I use that confidence to determine the inspection severity, risk, and recommended action.

| Confidence | Severity | Risk   | Action            |
|:----------:|----------|--------|-------------------|
| ≥ 95%      | Critical | High   | Reject PCB        |
| ≥ 85%      | High     | High   | Rework Required   |
| ≥ 70%      | Medium   | Medium | Manual Inspection |
| < 70%      | Low      | Low    | Accept / Review   |

When an inspection contains multiple defects, I use the **highest detected severity** as the overall inspection severity.

### Example Inspection

During an actual end-to-end test, I processed `01_missing_hole_01.jpg`.

The system detected three `missing_hole` defects with confidences of **78.52%**, **78.13%**, and **75.42%**.

The resulting inspection was:

```text
Status:          DEFECTIVE
Defect Count:    3
Severity:        MEDIUM
Risk:            MEDIUM
Decision:        MANUAL_INSPECTION
Recommendation:  Manual Inspection
```

I intentionally implemented this as a rule-based quality layer rather than a trained severity prediction model.

---

## 🔐 Authentication & Role-Based Access

I implemented JWT-based authentication in the FastAPI backend.

### Quality Engineer

The Quality Engineer workflow supports:

- Login
- Dashboard
- PCB image upload
- AI inspection
- Inspection history
- Inspection details
- Inspection statistics

### Supervisor

The Supervisor role is supported through backend role authorization and protected resources.

### Authentication Flow

```text
Username + Password
        ↓
Password Verification
        ↓
JWT Token Generation
        ↓
Bearer Authentication
        ↓
Protected API Endpoint
```

Passwords are stored as hashes rather than plain-text passwords.

---

## 🗄️ PostgreSQL Database

I used PostgreSQL to persist inspection data instead of relying only on temporary API responses.

### Users

Stores: User ID, Username, Email, Password hash, Role, Active status

### Inspections

Stores: Inspection ID, Filename, Status, Defect count, Severity, Risk, Decision, Recommendation, Inspection timestamp

### Detections

Stores: Detection ID, Inspection ID, Defect class, Confidence, Bounding-box coordinates

Bounding boxes are stored using `x1`, `y1`, `x2`, `y2`.

---

## 🔌 FastAPI Backend

I developed the backend using FastAPI.

### Main API Endpoints

| Method | Endpoint                       | Description                    |
|--------|--------------------------------|--------------------------------|
| GET    | `/health`                      | Health check                   |
| POST   | `/auth/register`               | Register a new user            |
| POST   | `/auth/login`                  | Login and receive a JWT        |
| GET    | `/auth/me`                     | Get the current user           |
| POST   | `/predict`                     | Run a PCB inspection           |
| GET    | `/inspections`                 | List inspections               |
| GET    | `/inspections/{inspection_id}` | Get inspection details         |
| GET    | `/stats`                       | Inspection statistics          |

The `/predict` endpoint performs the complete inspection workflow:

```text
Authentication
     ↓
File Validation
     ↓
Image Verification
     ↓
YOLO11s Inference
     ↓
Detection Processing
     ↓
Quality Assessment
     ↓
PostgreSQL Persistence
     ↓
JSON Response
```

---

## 🖼️ Image Validation

Before running YOLO inference, I added validation for uploaded images.

Supported formats: `.jpg`, `.jpeg`, `.png`

The backend validates:

- File extension
- MIME type
- Actual image contents
- File size

The current maximum upload size is **10 MB**.

I also use UUID-based temporary filenames when processing uploaded images.

---

## ⚛️ React Frontend

I built the frontend using React and Vite.

The frontend includes:

- Login and Registration
- Dashboard
- New Inspection with PCB image upload
- Detection visualization
- Inspection history and details
- Quality assessment display
- Navigation and protected routes

The frontend communicates with the FastAPI backend through REST APIs using Axios.

---

## 🐳 Docker

I containerized the FastAPI backend using Docker.

The backend Docker image includes:

- Python 3.11
- FastAPI
- Uvicorn
- Ultralytics
- YOLO11s
- OpenCV Headless
- SQLAlchemy
- PostgreSQL connectivity

PostgreSQL runs as a separate Docker container:

```text
visioninspect-backend
visioninspect-postgres
```

The containers communicate through a dedicated Docker network.

---

## 🧪 Testing

I added automated backend tests using Pytest.

**Current test result: `8 passed`**

The test suite covers:

- Health endpoint
- Statistics endpoint
- Inspection listing
- Missing inspection handling
- Invalid image validation
- Valid image inspection
- YOLO model availability
- Actual model inference

Run the tests:

```powershell
.\.venv\Scripts\python.exe -m pytest backend/tests -v
```

### Production Build

I also verified the React production build using Vite:

```bash
cd frontend
npm run build
```

The production build completed successfully.

---

## 📁 Project Structure

```text
VisionInspectAI/
│
├── backend/
│   ├── app/
│   │   ├── auth.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── inference.py
│   │   ├── main.py
│   │   ├── models.py
│   │   └── quality.py
│   │
│   ├── tests/
│   │   ├── test_api.py
│   │   └── test_inference.py
│   │
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── App.jsx
│   │   └── index.css
│   │
│   └── package.json
│
├── models/
│   └── best.pt
│
├── scripts/
│   ├── prepare_dataset.py
│   └── visualize_yolo.py
│
├── requirements.txt
├── .dockerignore
├── .gitignore
└── README.md
```

---

## ⚙️ Running the Project Locally

### 1. Clone the Repository

```bash
git clone https://github.com/gracelipika19/VisionInspectAI.git
cd VisionInspectAI
```

### 2. Create a Python Virtual Environment

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

### 3. Install Backend Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql+psycopg://visioninspect:your_password@127.0.0.1:15432/visioninspect_db
SECRET_KEY=your_secret_key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

> ⚠️ Do not commit `.env` to Git.

### 5. Start PostgreSQL

```powershell
docker run --name visioninspect-postgres `
  -e POSTGRES_USER=visioninspect `
  -e POSTGRES_PASSWORD=your_password `
  -e POSTGRES_DB=visioninspect_db `
  -p 15432:5432 `
  -d postgres:16
```

### 6. Start the Backend

From the project root:

```bash
uvicorn backend.app.main:app --reload
```

- Backend: http://localhost:8000
- Health check: http://localhost:8000/health

### 7. Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

- Frontend: http://localhost:5173

---

## 🐳 Running the Backend with Docker

Build the backend image:

```powershell
docker build -f backend/Dockerfile -t visioninspect-backend .
```

Create the Docker network and connect PostgreSQL:

```powershell
docker network create visioninspect-network
docker network connect visioninspect-network visioninspect-postgres
```

Run the backend:

```powershell
docker run --name visioninspect-backend `
  --network visioninspect-network `
  -p 8000:8000 `
  --env-file .env `
  -e DATABASE_URL="postgresql+psycopg://visioninspect:your_password@visioninspect-postgres:5432/visioninspect_db" `
  -d visioninspect-backend:latest
```

Check backend logs:

```powershell
docker logs visioninspect-backend
```

Test the API:

```powershell
curl.exe http://localhost:8000/health
```

Expected response:

```json
{
  "status": "healthy",
  "service": "VisionInspect AI"
}
```

---

## 📈 End-to-End Verification

I verified the complete inspection flow using a real PCB image.

```text
React / API Request
        ↓
JWT Authentication
        ↓
FastAPI
        ↓
Image Validation
        ↓
YOLO11s Inference
        ↓
3 Defect Detections
        ↓
Quality Assessment
        ↓
PostgreSQL Persistence
```

The resulting inspection was stored in PostgreSQL along with all three individual detections and their bounding-box coordinates.

---

## 🔒 Security

For this project, I implemented:

- JWT authentication
- Password hashing
- Protected API endpoints
- Role-based authorization
- Image validation
- File-size limits
- UUID-based temporary filenames
- Environment-based configuration
- `.env` exclusion from Git

For a production deployment, I would additionally use HTTPS, production secret management, stricter CORS configuration, database access restrictions, and stronger account policies.

---

## ⚠️ Limitations

- Severity and risk assessment are currently rule-based rather than learned from a separate severity-labeled dataset.
- The held-out test set contains 72 images, so the reported metrics should be interpreted in the context of this dataset size.
- The current system focuses on PCB image inspection rather than direct integration with a physical manufacturing production line.
- GPU inference would be preferable for high-throughput inspection workloads.
- Additional production hardening would be required before deploying the system in a real manufacturing environment.

---

## 🔮 Future Improvements

- Real-time camera-based PCB inspection
- Production-line integration
- Automated inspection reports
- Defect trend analytics
- Larger and more diverse PCB datasets
- ONNX / TensorRT model optimization
- Edge deployment
- Continuous model evaluation and retraining
- More specialized role-based dashboards

---

## 👩‍💻 About the Project

I developed VisionInspect AI as a practical **AI + full-stack + computer vision** project, taking the system from model training to API development, database integration, authentication, frontend visualization, automated testing, and Dockerization.

**Skills and tools used:** Computer Vision · Object Detection · PyTorch · YOLO11 · FastAPI · React · PostgreSQL · SQLAlchemy · JWT Authentication · Docker · REST APIs · Automated Testing · GitHub

---

**Repository:** https://github.com/gracelipika19/VisionInspectAI

Built by **Grace Lipika Sakilay**