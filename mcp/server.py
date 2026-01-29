from __future__ import annotations

import os
import random
import hashlib
import time
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any

app = FastAPI(title="Workshop MCP Server", version="0.1.0")

CHAOS = os.environ.get("MCP_CHAOS", "0") == "1"

class RoutesRequest(BaseModel):
    origin: str = Field(min_length=3, max_length=3)
    destination: str = Field(min_length=3, max_length=3)
    max_layovers: int = Field(default=2, ge=0, le=6)


class PricingRequest(BaseModel):
    origin: str
    destination: str
    mode: str  # flight | orbital
    provider: str
    date: datetime | None = None
    passenger_count: int = 1


class AvailabilityRequest(BaseModel):
    origin: str
    destination: str
    depart: datetime
    mode: str
    provider: str


class RiskRequest(BaseModel):
    provider: str
    mode: str
    route: str
    date: datetime | None = None
    weather_data: dict | None = None


class ValidationRequest(BaseModel):
    object: dict
    schema_name: str

@app.get("/healthz")
def healthz() -> dict:
    return {"ok": True, "chaos": CHAOS}

@app.post("/tools/routes.get")
def routes_get(req: RoutesRequest) -> dict:
    # Deterministic-ish sample itineraries (replace with real provider simulation later)
    base = [
        # direct-ish flight
        {"legs": [{"origin": req.origin, "destination": req.destination, "mode": "flight", "provider": "earth-air", "duration_minutes": 450}]},
        # one stop
        {"legs": [
            {"origin": req.origin, "destination": "KEF", "mode": "flight", "provider": "earth-air", "duration_minutes": 180},
            {"origin": "KEF", "destination": req.destination, "mode": "flight", "provider": "northwind", "duration_minutes": 360},
        ]},
        # silly orbital transfer (fun route)
        {"legs": [
            {"origin": req.origin, "destination": "ISS", "mode": "orbital", "provider": "orbitalx", "duration_minutes": 90},
            {"origin": "ISS", "destination": req.destination, "mode": "flight", "provider": "earth-air", "duration_minutes": 420},
        ]},
        # longer but "green-ish" (pretend)
        {"legs": [
            {"origin": req.origin, "destination": "AMS", "mode": "flight", "provider": "tulip", "duration_minutes": 80},
            {"origin": "AMS", "destination": req.destination, "mode": "flight", "provider": "tulip", "duration_minutes": 420},
        ]},
    ]

    # respect max_layovers
    itins = [i for i in base if (len(i["legs"]) - 1) <= req.max_layovers]

    if CHAOS:
        rnd = random.random()
        if rnd < 0.15:
            raise HTTPException(status_code=500, detail="provider timeout")
        if rnd < 0.30:
            # partial data
            itins = itins[:2]
        if rnd < 0.40:
            random.shuffle(itins)

    return {"itineraries": itins}


@app.post("/tools/pricing.calculate")
def pricing_calculate(req: PricingRequest) -> dict:
    """
    Calculate pricing with dynamic components.

    Intentional chaos modes:
    - 10% chance: timeout
    - 15% chance: return negative price
    - 20% chance: return price with missing fields
    """
    start_time = time.time()

    if CHAOS:
        rnd = random.random()
        if rnd < 0.10:
            time.sleep(5)  # Simulate timeout
            raise HTTPException(status_code=504, detail="Pricing service timeout")
        if rnd < 0.15:
            # Intentional bug: negative price
            return {
                "base_price": -100.0,
                "taxes": 20.0,
                "fees": 10.0,
                "total": -70.0,
                "currency": "GBP",
            }
        if rnd < 0.20:
            # Intentional bug: missing fields
            return {"total": 250.0}

    # Simple pricing model
    base_price = 100.0
    if req.mode == "orbital":
        base_price = 500.0

    # Provider multipliers
    provider_multipliers = {
        "earth-air": 1.0,
        "northwind": 0.9,
        "orbitalx": 2.0,
        "tulip": 0.85,
    }
    base_price *= provider_multipliers.get(req.provider, 1.0)

    # Peak pricing (weekends)
    if req.date and req.date.weekday() >= 5:
        base_price *= 1.3

    # Route hash for variation
    route_hash = hashlib.md5(f"{req.origin}{req.destination}".encode()).hexdigest()
    variation = int(route_hash[:4], 16) % 100
    base_price += variation

    taxes = base_price * 0.20
    fees = 25.0 if req.mode == "orbital" else 15.0
    total = (base_price + taxes + fees) * req.passenger_count

    duration_ms = int((time.time() - start_time) * 1000)

    return {
        "base_price": round(base_price, 2),
        "taxes": round(taxes, 2),
        "fees": round(fees, 2),
        "total": round(total, 2),
        "currency": "GBP",
        "duration_ms": duration_ms,
    }


@app.post("/tools/availability.check")
def availability_check(req: AvailabilityRequest) -> dict:
    """
    Check seat availability for a specific leg.

    Intentional chaos modes:
    - 15% chance: return 0 seats available
    - 10% chance: inconsistent data (held > booked)
    - 5% chance: service error
    """
    if CHAOS:
        rnd = random.random()
        if rnd < 0.05:
            raise HTTPException(status_code=503, detail="Availability service unavailable")
        if rnd < 0.15:
            return {
                "available_seats": 0,
                "booked_count": 150,
                "hold_count": 0,
                "status": "sold_out",
            }
        if rnd < 0.10:
            # Intentional bug: inconsistent data
            return {
                "available_seats": 10,
                "booked_count": 50,
                "hold_count": 100,  # More held than total capacity
                "status": "available",
            }

    # Deterministic availability based on route hash
    route_key = f"{req.provider}:{req.origin}:{req.destination}"
    route_hash = hashlib.md5(route_key.encode()).hexdigest()

    capacity = 200 if req.mode == "flight" else 50
    booked = int(route_hash[:4], 16) % capacity
    held = int(route_hash[4:8], 16) % (capacity - booked)
    available = capacity - booked - held

    status = "available" if available > 10 else "limited"

    return {
        "available_seats": available,
        "booked_count": booked,
        "hold_count": held,
        "total_capacity": capacity,
        "status": status,
    }


@app.post("/tools/risk.assess")
def risk_assess(req: RiskRequest) -> dict:
    """
    Assess risk score for a route/provider combination.

    Intentional chaos modes:
    - 20% chance: return risk > 1.0 (invalid)
    - 10% chance: return risk < 0.0 (invalid)
    - 5% chance: missing factors
    """
    if CHAOS:
        rnd = random.random()
        if rnd < 0.20:
            # Intentional bug: risk out of bounds
            return {
                "risk_score": 1.5,
                "factors": [{"name": "unknown", "contribution": 0.8}],
                "recommendation": "avoid",
            }
        if rnd < 0.10:
            return {"risk_score": -0.2, "factors": [], "recommendation": "safe"}
        if rnd < 0.05:
            return {"risk_score": 0.3}  # Missing fields

    # Simple risk model
    provider_risks = {
        "earth-air": 0.1,
        "northwind": 0.15,
        "orbitalx": 0.4,
        "tulip": 0.12,
    }
    base_risk = provider_risks.get(req.provider, 0.2)

    # Mode risk
    mode_risk = 0.3 if req.mode == "orbital" else 0.1

    # Weather modifier
    weather_risk = 0.0
    if req.weather_data and req.weather_data.get("severe"):
        weather_risk = 0.2

    total_risk = min(base_risk + mode_risk + weather_risk, 1.0)

    factors = [
        {"name": "provider_reliability", "contribution": base_risk},
        {"name": "transport_mode", "contribution": mode_risk},
    ]
    if weather_risk > 0:
        factors.append({"name": "weather_conditions", "contribution": weather_risk})

    recommendation = "avoid" if total_risk > 0.6 else "acceptable"

    return {
        "risk_score": round(total_risk, 3),
        "factors": factors,
        "recommendation": recommendation,
    }


@app.post("/tools/validation.check_schema")
def validation_check_schema(req: ValidationRequest) -> dict:
    """
    Validate object against named schema.

    Intentional chaos modes:
    - 5% chance: incorrectly report valid as invalid
    - 10% chance: timeout
    """
    if CHAOS:
        rnd = random.random()
        if rnd < 0.10:
            time.sleep(3)
            raise HTTPException(status_code=504, detail="Validation timeout")
        if rnd < 0.05:
            # Intentional bug: false negative
            return {
                "valid": False,
                "errors": [{"path": "unknown", "message": "Spurious validation error"}],
            }

    errors = []

    # Simple validation rules
    if req.schema_name == "Plan":
        if "legs" not in req.object:
            errors.append({"path": "legs", "message": "Required field 'legs' missing"})
        elif not isinstance(req.object["legs"], list):
            errors.append({"path": "legs", "message": "Field 'legs' must be a list"})

        if "metrics" not in req.object:
            errors.append({"path": "metrics", "message": "Required field 'metrics' missing"})
        elif isinstance(req.object.get("metrics"), dict):
            metrics = req.object["metrics"]
            if metrics.get("total_price_gbp", -1) < 0:
                errors.append({
                    "path": "metrics.total_price_gbp",
                    "message": "Price must be non-negative",
                })

    elif req.schema_name == "Booking":
        if "id" not in req.object:
            errors.append({"path": "id", "message": "Required field 'id' missing"})
        if "status" not in req.object:
            errors.append({"path": "status", "message": "Required field 'status' missing"})

    return {
        "valid": len(errors) == 0,
        "errors": errors,
    }


def main() -> None:
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("MCP_PORT", "8765")))

if __name__ == "__main__":
    main()
