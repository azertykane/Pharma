from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from .database import init_db
from .routers import machines, users, logs, ping
from .initial_data import create_admin, admin_exists

app = FastAPI(title="Admin Pharma API")

# ---------------------------
# CORS
# ---------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tu peux restreindre aux domaines autorisés en prod
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# Initialisation DB et admin
# ---------------------------
init_db()

if not admin_exists():
    create_admin()

# ---------------------------
# Routers API
# ---------------------------
app.include_router(machines.router, prefix="/api/machines")
app.include_router(users.router, prefix="/api/users")
app.include_router(logs.router, prefix="/api/logs")
app.include_router(ping.router, prefix="/api")

# ---------------------------
# Frontend
# ---------------------------
frontend_dist = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"

if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")
else:
    @app.get("/")
    async def index():
        return {"message": "Frontend not built."}

# ---------------------------
# Health check
# ---------------------------
@app.get("/health")
async def health_check():
    return {"status": "ok"}
