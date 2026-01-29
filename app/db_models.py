"""SQLAlchemy database models for persistence."""
from __future__ import annotations

from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, JSON, Text, Enum
from sqlalchemy.orm import relationship
from app.database import Base


class BookingStatus(str, PyEnum):
    """Booking lifecycle states."""
    PROPOSED = "proposed"
    CONFIRMED = "confirmed"
    PAID = "paid"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class Booking(Base):
    """Main booking entity with state transitions."""
    __tablename__ = "bookings"

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=True, index=True)  # Intentional: no auth yet
    status = Column(Enum(BookingStatus), default=BookingStatus.PROPOSED, nullable=False, index=True)
    plan_json = Column(JSON, nullable=False)  # Stores the selected Plan
    total_price_gbp = Column(Float, nullable=False)
    passenger_data = Column(JSON, nullable=True)  # name, email, passport, etc.
    payment_reference = Column(String, nullable=True)
    hold_expires_at = Column(DateTime, nullable=True)  # 5-minute hold for PROPOSED
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    legs = relationship("BookingLeg", back_populates="booking", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="booking", cascade="all, delete-orphan")


class BookingLeg(Base):
    """Individual leg of a booking for detailed tracking."""
    __tablename__ = "booking_legs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    booking_id = Column(String, ForeignKey("bookings.id"), nullable=False)
    provider = Column(String, nullable=False)
    mode = Column(String, nullable=False)  # flight | orbital
    origin = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    depart_at = Column(DateTime, nullable=False)
    arrive_at = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    seat_number = Column(String, nullable=True)

    # Relationships
    booking = relationship("Booking", back_populates="legs")


class AuditLog(Base):
    """Audit trail for all state transitions and actions."""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    booking_id = Column(String, ForeignKey("bookings.id"), nullable=True, index=True)
    entity_type = Column(String, nullable=False)  # booking, payment, mcp_call, etc.
    entity_id = Column(String, nullable=True)
    action = Column(String, nullable=False)  # CREATED, STATE_CHANGE, PAYMENT_ATTEMPTED, etc.
    before_state = Column(JSON, nullable=True)
    after_state = Column(JSON, nullable=True)
    extra_data = Column(JSON, nullable=True)  # Additional context (error messages, MCP response, etc.)
    user_id = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    booking = relationship("Booking", back_populates="audit_logs")


class Seat(Base):
    """Seat inventory for demonstrating concurrency issues."""
    __tablename__ = "seats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    flight_id = Column(String, nullable=False, index=True)  # provider:origin:destination:departure
    seat_number = Column(String, nullable=False)
    status = Column(String, nullable=False, default="available")  # available, held, booked
    booking_id = Column(String, ForeignKey("bookings.id"), nullable=True)
    held_until = Column(DateTime, nullable=True)  # Expiry time for held seats
    booked_at = Column(DateTime, nullable=True)

    # Intentional race condition: no database constraint on status transitions
    # Workshop participants will discover and fix this


class MCPCallLog(Base):
    """Log all MCP server calls for observability and chaos analysis."""
    __tablename__ = "mcp_call_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tool_name = Column(String, nullable=False, index=True)
    input_params = Column(JSON, nullable=False)
    output_result = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    success = Column(Integer, nullable=False, default=1)  # 1 = success, 0 = failure (SQLite doesn't have boolean)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
