# Workshop Setup Guide

Quick setup guide for workshop participants. Follow these steps before the workshop starts.

## Prerequisites

1. **Python 3.11+** installed
   ```bash
   python --version  # Should be 3.11 or higher
   ```

2. **Claude Code** installed and configured
   - Follow: https://github.com/anthropics/claude-code

3. **Git** installed
   ```bash
   git --version
   ```

4. **Text editor or IDE** (VS Code, PyCharm, etc.)

---

## Setup Steps

### 1. Clone Repository

```bash
git clone <repository-url>
cd orbital-travel-planner
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -U pip
pip install -e ".[dev]"
```

This installs:
- FastAPI & Uvicorn (API server)
- SQLAlchemy & Alembic (database)
- httpx (HTTP client)
- Pydantic (validation)
- pytest (testing)
- And more...

### 4. Verify Installation

Run the tests to confirm everything is installed:

```bash
pytest -q
```

You should see tests pass (some may be marked `xfail` - that's expected).

### 5. Start the MCP Server

In one terminal:

```bash
source .venv/bin/activate
python -m mcp.server
```

You should see:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8765
```

Leave this running.

### 6. Start the API Server

In a **second terminal**:

```bash
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

You should see:
```
INFO:     Started server process
INFO:     Application startup complete
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### 7. Test the Application

Open your browser to: **http://localhost:8000**

You should see the Orbital Travel Planner interface.

Try a search:
- Origin: **LON**
- Destination: **NYC**
- Set dates (any future dates)
- Click **Search**

You should see 3-4 itineraries returned.

### 8. Test Booking Flow

1. Click **Book This Plan** on any itinerary
2. Fill in passenger details:
   - Name: Your name
   - Email: test@example.com
   - Passport: (optional)
3. Click **Confirm & Pay**
4. You should see a success message with a payment reference

---

## Troubleshooting

### Port Already in Use

If port 8000 or 8765 is already in use:

```bash
# Check what's using the port
lsof -i :8000   # On macOS/Linux
netstat -ano | findstr :8000  # On Windows

# Kill the process or use a different port
uvicorn app.main:app --reload --port 8001
```

### Import Errors

If you see import errors:

```bash
# Reinstall dependencies
pip install -e ".[dev]"

# Verify you're in the virtual environment
which python  # Should show .venv/bin/python
```

### Database Errors

If you see database errors:

```bash
# Delete and recreate the database
rm -f orbital_travel.db
# Restart the API server
```

### MCP Server Not Found

If the API can't connect to the MCP server:

```bash
# Verify MCP server is running
curl http://localhost:8765/healthz

# Should return: {"ok": true, "chaos": false}
```

---

## Workshop Checklist

Before the workshop, make sure you can:

- [ ] Clone the repository
- [ ] Install dependencies without errors
- [ ] Run tests successfully
- [ ] Start both MCP server and API server
- [ ] Access the web interface at http://localhost:8000
- [ ] Perform a search and see results
- [ ] Create a booking and confirm it
- [ ] View booking details

If any of these fail, ask for help before the workshop starts!

---

## Optional: Enable Chaos Mode

To test error handling (useful for later exercises):

```bash
# Stop the MCP server (Ctrl+C)
# Restart with chaos mode
MCP_CHAOS=1 python -m mcp.server
```

Now searches may randomly fail or return invalid data. This is intentional!

---

## Claude Code Configuration

Make sure Claude Code can access this repository:

1. Open Claude Code CLI
2. Navigate to the repository directory:
   ```bash
   cd /path/to/orbital-travel-planner
   ```
3. Test Claude Code:
   ```
   Ask Claude: "Explore the codebase and tell me what this application does"
   ```

Claude should be able to read files and understand the structure.

---

## What's Next?

Once setup is complete, read [WORKSHOP.md](WORKSHOP.md) for the full workshop agenda.

The workshop starts with **Stage 1: Foundations & Setup** where you'll:
- Create your first custom skill
- Spawn and coordinate agents
- Add an MCP server to Claude Code's config

See you at the workshop!
