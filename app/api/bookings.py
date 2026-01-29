"""Booking endpoints with stateful operations and intentional vulnerabilities."""
from __future__ import annotations

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import uuid

from app.database import get_db
from app.db_models import Booking, BookingLeg, AuditLog, BookingStatus
from app.models import Plan
from pydantic import BaseModel, Field

router = APIRouter()


# Request/Response models
class CreateBookingRequest(BaseModel):
    plan: Plan
    user_id: str | None = None


class PassengerData(BaseModel):
    full_name: str = Field(min_length=1)
    email: str = Field(pattern=r"^[^@]+@[^@]+\.[^@]+$")
    passport_number: str | None = None


class ConfirmBookingRequest(BaseModel):
    passenger_data: PassengerData


class BookingResponse(BaseModel):
    id: str
    status: BookingStatus
    plan: Plan
    total_price_gbp: float
    passenger_data: PassengerData | None = None
    payment_reference: str | None = None
    hold_expires_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class BookingListResponse(BaseModel):
    bookings: List[BookingResponse]


class AuditLogEntry(BaseModel):
    action: str
    timestamp: datetime
    before_state: dict | None = None
    after_state: dict | None = None
    extra_data: dict | None = None


class BookingDetailResponse(BookingResponse):
    audit_trail: List[AuditLogEntry]


async def log_audit(
    db: AsyncSession,
    booking_id: str | None,
    entity_type: str,
    action: str,
    before: dict | None = None,
    after: dict | None = None,
    extra_data: dict | None = None,
) -> None:
    """Helper to create audit log entries."""
    log = AuditLog(
        booking_id=booking_id,
        entity_type=entity_type,
        entity_id=booking_id,
        action=action,
        before_state=before,
        after_state=after,
        extra_data=extra_data,
        timestamp=datetime.utcnow(),
    )
    db.add(log)


@router.post("/bookings", response_model=BookingResponse, status_code=201)
async def create_booking(
    req: CreateBookingRequest,
    db: AsyncSession = Depends(get_db),
) -> BookingResponse:
    """
    Create a new booking in PROPOSED state with 5-minute hold.

    Intentional issues for workshop:
    - No duplicate detection (can book same plan multiple times)
    - No seat availability check
    - No concurrent booking handling
    """
    booking_id = str(uuid.uuid4())
    hold_expires_at = datetime.utcnow() + timedelta(minutes=5)

    booking = Booking(
        id=booking_id,
        user_id=req.user_id,
        status=BookingStatus.PROPOSED,
        plan_json=req.plan.model_dump(),
        total_price_gbp=req.plan.metrics.total_price_gbp,
        hold_expires_at=hold_expires_at,
    )

    # Create legs
    for leg_data in req.plan.legs:
        leg = BookingLeg(
            booking_id=booking_id,
            provider=leg_data.provider,
            mode=leg_data.mode,
            origin=leg_data.origin,
            destination=leg_data.destination,
            depart_at=leg_data.depart_at,
            arrive_at=leg_data.arrive_at,
            duration_minutes=leg_data.duration_minutes,
        )
        db.add(leg)

    db.add(booking)
    await log_audit(
        db,
        booking_id,
        "booking",
        "CREATED",
        after={"status": BookingStatus.PROPOSED.value, "price": req.plan.metrics.total_price_gbp},
    )
    await db.commit()
    await db.refresh(booking)

    return BookingResponse(
        id=booking.id,
        status=booking.status,
        plan=Plan(**booking.plan_json),
        total_price_gbp=booking.total_price_gbp,
        hold_expires_at=booking.hold_expires_at,
        created_at=booking.created_at,
        updated_at=booking.updated_at,
    )


@router.get("/bookings/{booking_id}", response_model=BookingDetailResponse)
async def get_booking(
    booking_id: str,
    db: AsyncSession = Depends(get_db),
) -> BookingDetailResponse:
    """
    Fetch booking with full audit trail.

    Intentional issue for workshop:
    - No authorization check (anyone can view any booking)
    - Verbose error messages expose internal state
    """
    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalar_one_or_none()

    if not booking:
        # Intentional: verbose error message
        raise HTTPException(
            status_code=404,
            detail=f"Booking {booking_id} not found in database table 'bookings'",
        )

    # Fetch audit trail
    audit_result = await db.execute(
        select(AuditLog)
        .where(AuditLog.booking_id == booking_id)
        .order_by(AuditLog.timestamp.asc())
    )
    audit_logs = audit_result.scalars().all()

    passenger_data = None
    if booking.passenger_data:
        passenger_data = PassengerData(**booking.passenger_data)

    return BookingDetailResponse(
        id=booking.id,
        status=booking.status,
        plan=Plan(**booking.plan_json),
        total_price_gbp=booking.total_price_gbp,
        passenger_data=passenger_data,
        payment_reference=booking.payment_reference,
        hold_expires_at=booking.hold_expires_at,
        created_at=booking.created_at,
        updated_at=booking.updated_at,
        audit_trail=[
            AuditLogEntry(
                action=log.action,
                timestamp=log.timestamp,
                before_state=log.before_state,
                after_state=log.after_state,
                extra_data=log.extra_data,
            )
            for log in audit_logs
        ],
    )


@router.post("/bookings/{booking_id}/confirm", response_model=BookingResponse)
async def confirm_booking(
    booking_id: str,
    req: ConfirmBookingRequest,
    db: AsyncSession = Depends(get_db),
) -> BookingResponse:
    """
    Confirm booking: PROPOSED → CONFIRMED → PAID.

    Intentional issues for workshop:
    - No hold expiry check (can confirm after 5-minute window)
    - Mock payment always succeeds
    - No idempotency (can call multiple times)
    - No seat locking (race condition possible)
    """
    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalar_one_or_none()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking.status != BookingStatus.PROPOSED:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot confirm booking in {booking.status} state",
        )

    # Intentional: no hold expiry check
    # if booking.hold_expires_at and datetime.utcnow() > booking.hold_expires_at:
    #     raise HTTPException(status_code=400, detail="Hold expired")

    old_status = booking.status
    booking.status = BookingStatus.CONFIRMED
    booking.passenger_data = req.passenger_data.model_dump()

    await log_audit(
        db,
        booking_id,
        "booking",
        "STATE_CHANGE",
        before={"status": old_status.value},
        after={"status": BookingStatus.CONFIRMED.value},
    )

    # Mock payment
    payment_ref = f"PAY-{uuid.uuid4()}"
    booking.payment_reference = payment_ref
    booking.status = BookingStatus.PAID

    await log_audit(
        db,
        booking_id,
        "payment",
        "PAYMENT_SUCCESSFUL",
        extra_data={"payment_reference": payment_ref, "amount": booking.total_price_gbp},
    )

    await db.commit()
    await db.refresh(booking)

    return BookingResponse(
        id=booking.id,
        status=booking.status,
        plan=Plan(**booking.plan_json),
        total_price_gbp=booking.total_price_gbp,
        passenger_data=PassengerData(**booking.passenger_data),
        payment_reference=booking.payment_reference,
        hold_expires_at=booking.hold_expires_at,
        created_at=booking.created_at,
        updated_at=booking.updated_at,
    )


@router.delete("/bookings/{booking_id}", status_code=200)
async def cancel_booking(
    booking_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Cancel booking with refund processing.

    Intentional issues:
    - No refund amount calculation
    - No authorization (anyone can cancel any booking)
    - Allows cancellation from any state
    """
    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalar_one_or_none()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking.status == BookingStatus.CANCELLED:
        return {"message": "Booking already cancelled"}

    old_status = booking.status
    booking.status = BookingStatus.CANCELLED

    # Mock refund processing
    refund_amount = booking.total_price_gbp if old_status == BookingStatus.PAID else 0.0

    await log_audit(
        db,
        booking_id,
        "booking",
        "CANCELLED",
        before={"status": old_status.value},
        after={"status": BookingStatus.CANCELLED.value},
        extra_data={"refund_amount": refund_amount},
    )

    await db.commit()

    return {"message": "Booking cancelled", "refund_amount": refund_amount}


@router.get("/bookings", response_model=BookingListResponse)
async def list_bookings(
    status: BookingStatus | None = Query(None),
    user_id: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
) -> BookingListResponse:
    """
    List bookings with optional filters.

    Intentional issues:
    - No pagination (can return thousands of records)
    - No authorization (can see all bookings)
    - SQL injection vulnerability if using raw queries (currently safe with SQLAlchemy)
    """
    query = select(Booking)

    if status:
        query = query.where(Booking.status == status)
    if user_id:
        # Intentional: demonstrates SQL injection risk if someone modifies this to raw SQL
        query = query.where(Booking.user_id == user_id)

    result = await db.execute(query.order_by(Booking.created_at.desc()))
    bookings = result.scalars().all()

    return BookingListResponse(
        bookings=[
            BookingResponse(
                id=b.id,
                status=b.status,
                plan=Plan(**b.plan_json),
                total_price_gbp=b.total_price_gbp,
                passenger_data=PassengerData(**b.passenger_data) if b.passenger_data else None,
                payment_reference=b.payment_reference,
                hold_expires_at=b.hold_expires_at,
                created_at=b.created_at,
                updated_at=b.updated_at,
            )
            for b in bookings
        ]
    )
