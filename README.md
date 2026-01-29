# Orbital Travel Planner

A full-stack travel planning application with Python FastAPI backend, vanilla JavaScript frontend, and stateful booking system. This project demonstrates:
- Multi-leg itinerary search and optimization
- Stateful booking flow with database persistence
- External systems mocked via **MCP server** (multi-tool + chaos mode)
- API middleware (audit logging, rate limiting, authentication)
- Test-driven development with pytest
- Intentional vulnerabilities for workshop learning

**This is workshop starter code.** See [WORKSHOP.md](WORKSHOP.md) for the full-day advanced Claude Code workshop guide.

---

## Quick Start

### Prerequisites
- Python 3.11+
- pip

### 1) Installation

Clone the repository and set up the Python environment:

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies (includes SQLAlchemy, Alembic, rate limiting, etc.)
pip install -U pip
pip install -e ".[dev]"
```

### 2) Initialize Database

The database will be automatically initialized when you start the API server. The SQLite database file will be created at `./orbital_travel.db`.

To manually initialize or reset the database:
```bash
rm -f orbital_travel.db  # Remove existing database
# Database will be recreated on next API server start
```

### 3) Start the MCP Server (Required)

The MCP server provides mock travel provider data with multiple tools. Start it in a **separate terminal**:

```bash
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
python -m mcp.server
```

**Chaos Mode (Optional):** To enable random failures for testing:
```bash
MCP_CHAOS=1 python -m mcp.server
```

Leave this running - the API depends on it.

### 4) Start the API Server

In another terminal, start the FastAPI server:

```bash
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

### 5) Access the Application

Open your browser and navigate to:

**http://localhost:8000**

You'll see the Orbital Travel Planner web interface where you can:
- Search for travel routes between cities
- Specify time windows for departure and arrival
- Choose optimization preferences (fastest, cheapest, greenest, balanced)
- View detailed itineraries with multiple legs
- **Book selected itineraries** (new!)
- Confirm bookings with passenger data
- View booking status and audit trail

---

## API Endpoints

### Core Endpoints

#### GET /
Serves the frontend web application

#### GET /healthz
Health check endpoint
- **Response**: `{"ok": true}`

### Search Endpoints

#### POST /api/search
Search for travel itineraries
- **Request Body**:
  ```json
  {
    "origin": "LON",
    "destination": "NYC",
    "depart_after": "2026-02-01T08:00:00Z",
    "arrive_before": "2026-02-02T08:00:00Z",
    "max_layovers": 2,
    "optimize_for": "balanced"
  }
  ```
- **optimize_for options**: `fastest`, `cheapest`, `greenest`, `balanced`
- **Response**: List of travel plans with legs, metrics, and scores

### Booking Endpoints (NEW)

#### POST /api/bookings
Create a new booking in PROPOSED state
- **Request Body**:
  ```json
  {
    "plan": { ... },  // Full Plan object from search results
    "user_id": "optional-user-id"
  }
  ```
- **Response**: Booking object with 5-minute hold
- **Status**: 201 Created

#### GET /api/bookings/{booking_id}
Retrieve booking with full audit trail
- **Response**: Booking details with audit log entries

#### POST /api/bookings/{booking_id}/confirm
Confirm booking and process payment
- **Request Body**:
  ```json
  {
    "passenger_data": {
      "full_name": "Jane Doe",
      "email": "jane@example.com",
      "passport_number": "ABC123456"
    }
  }
  ```
- **Response**: Confirmed booking with payment reference

#### DELETE /api/bookings/{booking_id}
Cancel booking with refund
- **Response**: Cancellation confirmation with refund amount

#### GET /api/bookings?status=proposed&user_id=user123
List bookings with optional filters
- **Query params**: `status`, `user_id`
- **Response**: List of bookings

---

## MCP Server Tools

The MCP server provides multiple tools for workshop exercises:

### routes.get
Get available itineraries
- **Input**: `{origin, destination, max_layovers}`
- **Output**: List of itineraries with legs

### pricing.calculate
Calculate dynamic pricing
- **Input**: `{origin, destination, mode, provider, date, passenger_count}`
- **Output**: `{base_price, taxes, fees, total, currency}`
- **Chaos**: May return negative prices or missing fields

### availability.check
Check seat availability
- **Input**: `{origin, destination, depart, mode, provider}`
- **Output**: `{available_seats, booked_count, hold_count, status}`
- **Chaos**: May return inconsistent data

### risk.assess
Assess route risk
- **Input**: `{provider, mode, route, date, weather_data}`
- **Output**: `{risk_score, factors, recommendation}`
- **Chaos**: May return out-of-bounds risk scores

### validation.check_schema
Validate objects against schemas
- **Input**: `{object, schema_name}`
- **Output**: `{valid, errors}`
- **Chaos**: May produce false negatives

---

## Project Structure

```
orbital-travel-planner/
├── app/
│   ├── api/              # FastAPI route handlers
│   │   ├── search.py     # Search endpoint
│   │   └── bookings.py   # Booking endpoints (NEW)
│   ├── domain/           # Business logic (pricing, risk, emissions, routes)
│   ├── services/         # External service clients (MCP, planner, validator)
│   ├── static/           # Frontend files (HTML, CSS, JS)
│   ├── database.py       # Database configuration (NEW)
│   ├── db_models.py      # SQLAlchemy models (NEW)
│   ├── middleware.py     # API middleware (audit, auth, rate limit) (NEW)
│   ├── main.py           # FastAPI application entry point
│   └── models.py         # Pydantic models for API
├── mcp/                  # MCP server with multiple tools
│   ├── server.py         # Extended with 5 tools (NEW)
│   └── __main__.py       # Entry point
├── tests/                # Test suite
│   ├── integration/      # Integration tests
│   ├── unit/             # Unit tests
│   └── properties/       # Property-based invariant tests
├── pyproject.toml        # Python dependencies and config
├── README.md             # This file
└── WORKSHOP.md           # Workshop guide (NEW)
```

---

## Development

### Running in Development Mode

The application uses `--reload` flag with uvicorn, which automatically restarts the server when code changes are detected.

### Code Quality

Run linting and type checking:
```bash
ruff check .
mypy app/
```

### Running Tests

Basic test run:
```bash
pytest -q
```

With coverage:
```bash
pytest -v --cov=app
```

Run specific test categories:
```bash
pytest tests/unit/          # Unit tests only
pytest tests/integration/   # Integration tests only
pytest tests/properties/    # Property-based tests
```

### Testing with cURL

Test health endpoint:
```bash
curl http://localhost:8000/healthz
```

Search for routes:
```bash
curl -X POST http://localhost:8000/api/search \
  -H 'Content-Type: application/json' \
  -d '{
    "origin": "LON",
    "destination": "NYC",
    "depart_after": "2026-02-01T08:00:00Z",
    "arrive_before": "2026-02-02T08:00:00Z",
    "max_layovers": 2,
    "optimize_for": "balanced"
  }'
```

Create a booking:
```bash
curl -X POST http://localhost:8000/api/bookings \
  -H 'Content-Type: application/json' \
  -d '{
    "plan": <PLAN_JSON_FROM_SEARCH>,
    "user_id": "test-user"
  }'
```

---

## Database Schema

The application uses SQLite with SQLAlchemy ORM. Key tables:

- **bookings**: Main booking records with status lifecycle
- **booking_legs**: Individual legs of each booking
- **audit_logs**: Complete audit trail for all actions
- **seats**: Seat inventory (demonstrates concurrency issues)
- **mcp_call_logs**: MCP server call observability

The database is automatically created on first run.

---

## Middleware & Security

### Audit Middleware
- Logs all API requests and responses
- Captures request/response bodies
- Adds unique request IDs to headers
- **Intentional issues**: Logs sensitive data, no rotation, synchronous

### Rate Limiting
- Uses SlowAPI for rate limiting
- Default: 60 requests per minute per IP
- **Not enabled by default** - enable in workshop exercises

### Authentication Middleware
- Simple API key authentication (X-API-Key header)
- **Not enabled by default** - enable in workshop exercises
- **Intentional issues**: Hardcoded keys, verbose error messages, no rotation

Valid API keys (for workshop):
- `workshop-key-123` (workshop user)
- `admin-key-456` (admin user)

---

## Intentional Issues for Workshop

This codebase contains deliberate bugs and anti-patterns for learning:

### Booking Endpoints
- ❌ No duplicate detection (can book same plan multiple times)
- ❌ No seat availability check before booking
- ❌ No hold expiry enforcement
- ❌ No authorization (anyone can view/cancel any booking)
- ❌ Verbose error messages expose internal state
- ❌ No idempotency on confirm endpoint
- ❌ Mock payment always succeeds

### Database
- ❌ Seat model has race condition (no lock on status transitions)
- ❌ No database connection pooling tuning
- ❌ No indexes on frequently queried fields

### MCP Server (Chaos Mode)
- ❌ Returns negative prices (invalid data)
- ❌ Returns risk scores > 1.0 (out of bounds)
- ❌ Missing required fields in responses
- ❌ Random timeouts and errors

### Middleware
- ❌ Logs sensitive passenger data
- ❌ No log rotation (disk fills up)
- ❌ Hardcoded API keys
- ❌ No pagination on list endpoints

### Frontend
- ❌ No input sanitization beyond basic escaping
- ❌ No loading states during async operations
- ❌ No retry logic on failures

**These are all learning opportunities.** Workshop participants will use Claude Code to discover, analyze, and fix these issues.

---

## Workshop Usage

This repository is designed for the **Advanced Claude Code Workshop**. See [WORKSHOP.md](WORKSHOP.md) for:
- Full-day schedule (10:30–16:00)
- Stage-by-stage exercises
- Skills to build (custom `/validate-api`, `/chaos-test`, etc.)
- MCP server development exercises
- Multi-agent orchestration patterns
- Self-validation loops

The workshop teaches:
- Planning-first workflows with Claude Code
- Multi-agent coordination (Explore, Plan, Bash agents)
- Custom skill development
- MCP server integration
- Verification loops and quality gates
- Real-world engineering practices

---

## Troubleshooting

**Q: I get "Internal Server Error" when searching**
- Make sure the MCP server is running in a separate terminal (`python -m mcp.server`)
- Check that MCP server is on default port (usually 8765)
- Check API logs for connection errors

**Q: Database errors on startup**
- Delete `orbital_travel.db` and restart the API server
- Ensure SQLAlchemy and aiosqlite are installed: `pip install -e .`

**Q: The frontend doesn't load**
- Verify the API server is running on port 8000
- Check the browser console for errors
- Ensure `app/static/` directory exists with index.html, app.js, styles.css

**Q: Bookings don't work**
- Check that the database initialized successfully (look for `orbital_travel.db`)
- Check API logs for SQLAlchemy errors
- Try the booking endpoints directly with cURL to isolate frontend vs. backend issues

**Q: Tests are failing**
- Make sure you installed dev dependencies: `pip install -e ".[dev]"`
- Some tests may be marked `xfail` intentionally for workshop exercises
- Run with `-v` flag for detailed output

**Q: Import errors for slowapi or other packages**
- Run `pip install -e .` to install all updated dependencies
- Check that you're using the correct virtual environment

---

## License

MIT License - This is educational workshop code.

---

## Contributing

This is workshop starter code. If you're using this for a workshop:
1. Fork the repository
2. Customize exercises for your audience
3. Add your own intentional bugs/challenges
4. Share your workshop learnings!

For workshop facilitators: See [WORKSHOP.md](WORKSHOP.md) for facilitation notes and exercise solutions.
