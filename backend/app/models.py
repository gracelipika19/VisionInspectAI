from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    username: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="QUALITY_ENGINEER",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )


class Inspection(Base):
    __tablename__ = "inspections"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    defect_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    # Quality assessment fields
    severity: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="NONE",
    )

    risk: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="LOW",
    )

    decision: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="PASS",
    )

    recommendation: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="No defects detected",
    )

    inspected_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    detections: Mapped[list["Detection"]] = relationship(
        back_populates="inspection",
        cascade="all, delete-orphan",
    )


class Detection(Base):
    __tablename__ = "detections"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    inspection_id: Mapped[int] = mapped_column(
        ForeignKey("inspections.id"),
        nullable=False,
    )

    class_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    class_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    x1: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    y1: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    x2: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    y2: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    inspection: Mapped["Inspection"] = relationship(
        back_populates="detections",
    )