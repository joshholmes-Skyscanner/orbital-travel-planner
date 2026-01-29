from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from contextlib import asynccontextmanager

from app.api.search import router as search_router
from app.api.bookings import router as bookings_router
from app.middleware import AuditMiddleware, configure_logging, limiter
from app.database import init_db
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    configure_logging()
    await init_db()
    yield


app = FastAPI(
    title="Orbital Travel Planner",
    version="0.1.0",
    lifespan=lifespan,
)

# Attach limiter to app state (required by SlowAPI)
app.state.limiter = limiter

# Add middleware
app.add_middleware(AuditMiddleware)
app.add_middleware(SlowAPIMiddleware)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Note: AuthMiddleware intentionally NOT enabled by default
# Participants can enable it as a workshop exercise
# from app.middleware import AuthMiddleware
# app.add_middleware(AuthMiddleware)

app.include_router(search_router, prefix="/api")
app.include_router(bookings_router, prefix="/api")

# Serve static files (frontend)
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    @app.get("/")
    def root() -> FileResponse:
        return FileResponse(static_dir / "index.html")

@app.get("/healthz")
def healthz() -> dict:
    return {"ok": True}
