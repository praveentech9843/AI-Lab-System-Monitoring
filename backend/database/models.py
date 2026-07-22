"""
Database ORM Models Module.
Defines SQLAlchemy 2.x declarative models for Students, Faculty, ExamSessions, ActivityLogs, and Alerts.
"""
import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base


class Student(Base):
    """
    Student ORM Model.

    Represents enrolled student accounts registered in the monitoring platform.
    Tracks academic details, authentication credentials, active status, and audit timestamps.
    """
    __tablename__ = "students"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )

    # Core Information
    register_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    department: Mapped[str] = mapped_column(String(100), nullable=False)
    year: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[str] = mapped_column(
        String(320),
        unique=True,
        index=True,
        nullable=False
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Relationships
    exam_sessions: Mapped[List["ExamSession"]] = relationship(
        "ExamSession",
        back_populates="student",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    activity_logs: Mapped[List["ActivityLog"]] = relationship(
        "ActivityLog",
        back_populates="student",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    alerts: Mapped[List["Alert"]] = relationship(
        "Alert",
        back_populates="student",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Student(id={self.id}, register_number='{self.register_number}')>"


class Faculty(Base):
    """
    Faculty ORM Model.

    Represents faculty members and lab instructors who supervise student monitoring and exam sessions.
    Houses credentials, administrative roles, and session ownership records.
    """
    __tablename__ = "faculty"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )

    # Core Information
    employee_id: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(
        String(320),
        unique=True,
        index=True,
        nullable=False
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="faculty", nullable=False)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Relationships
    exam_sessions: Mapped[List["ExamSession"]] = relationship(
        "ExamSession",
        back_populates="faculty",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Faculty(id={self.id}, employee_id='{self.employee_id}')>"


class ExamSession(Base):
    """
    ExamSession ORM Model.

    Tracks active and historical live supervision sessions between a student workstation and assigned faculty.
    Serves as the parent container for session activity logs and real-time anomaly alerts.
    """
    __tablename__ = "exam_sessions"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )

    # Core Information
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("students.id"),
        index=True,
        nullable=False
    )
    faculty_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("faculty.id"),
        index=True,
        nullable=True
    )

    # Status
    status: Mapped[str] = mapped_column(
        String(50),
        default="active",
        nullable=False
    )

    # Timestamps
    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    end_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    # Relationships
    student: Mapped["Student"] = relationship(
        "Student",
        back_populates="exam_sessions",
        lazy="selectin"
    )
    faculty: Mapped[Optional["Faculty"]] = relationship(
        "Faculty",
        back_populates="exam_sessions",
        lazy="selectin"
    )
    activity_logs: Mapped[List["ActivityLog"]] = relationship(
        "ActivityLog",
        back_populates="session",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    alerts: Mapped[List["Alert"]] = relationship(
        "Alert",
        back_populates="session",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<ExamSession(id={self.id}, status='{self.status}')>"


class ActivityLog(Base):
    """
    ActivityLog ORM Model.

    Logs desktop activities and detected events associated with a specific student monitoring session.
    Captures activity classifications, AI confidence scores, and audit timestamps.
    """
    __tablename__ = "activity_logs"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )

    # Core Information
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("exam_sessions.id"),
        index=True,
        nullable=False
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("students.id"),
        index=True,
        nullable=False
    )
    activity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Timestamps
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relationships
    session: Mapped["ExamSession"] = relationship(
        "ExamSession",
        back_populates="activity_logs",
        lazy="selectin"
    )
    student: Mapped["Student"] = relationship(
        "Student",
        back_populates="activity_logs",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<ActivityLog(id={self.id}, activity_type='{self.activity_type}')>"


class Alert(Base):
    """
    Alert ORM Model.

    Stores real-time AI anomaly alerts triggered during student monitoring sessions.
    Includes alert type classification, severity levels, detailed messages, and creation timestamps.
    """
    __tablename__ = "alerts"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )

    # Core Information
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("students.id"),
        index=True,
        nullable=False
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("exam_sessions.id"),
        index=True,
        nullable=False
    )
    alert_type: Mapped[str] = mapped_column(String(100), nullable=False)
    severity: Mapped[str] = mapped_column(String(50), nullable=False)
    message: Mapped[str] = mapped_column(String(500), nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relationships
    student: Mapped["Student"] = relationship(
        "Student",
        back_populates="alerts",
        lazy="selectin"
    )
    session: Mapped["ExamSession"] = relationship(
        "ExamSession",
        back_populates="alerts",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Alert(id={self.id}, alert_type='{self.alert_type}')>"


class ComputerEvent(Base):
    """
    ComputerEvent ORM Model.
    Tracks raw monitoring updates sent by the Student Monitoring Agent.
    Stores computer details, metrics, active app/website, and timestamps.
    """
    __tablename__ = "computer_events"

    # Composite index: accelerates `WHERE computer_id=X ORDER BY timestamp DESC LIMIT 1`
    # which is the hottest query pattern (called on every agent packet)
    __table_args__ = (
        Index("ix_computer_events_computer_ts", "computer_id", "timestamp"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    computer_id: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    student_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    active_application: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    active_website: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    cpu_usage: Mapped[float] = mapped_column(Float, default=0.0)
    ram_usage: Mapped[float] = mapped_column(Float, default=0.0)
    screenshot_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    activity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    def __repr__(self) -> str:
        return f"<ComputerEvent(id={self.id}, computer_id='{self.computer_id}', activity_type='{self.activity_type}')>"

