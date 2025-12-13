from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from .database import init_db
from .routers import machines, users, logs, ping
from .initial_data import create_admin, admin_exists

app = FastAPI(title="Admin Pharma API")

# -------------------- CORS --------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- INIT DB --------------------
init_db()
if not admin_exists():
    create_admin()

# -------------------- API (AVANT TOUT) --------------------
app.include_router(machines.router, prefix="/api/machines")
app.include_router(users.router, prefix="/api/users")
app.include_router(logs.router, prefix="/api/logs")
app.include_router(ping.router, prefix="/api")

# -------------------- FRONTEND --------------------
BASE_DIR = Path(__file__).resolve().parent.parent.parent
FRONTEND_DIST = BASE_DIR / "frontend" / "dist"

if FRONTEND_DIST.exists():

    # 1️⃣ Servir les assets Vite
    app.mount(
        "/assets",
        StaticFiles(directory=FRONTEND_DIST / "assets"),
        name="assets",
    )

    # 2️⃣ Catch-all React (APRES l'API)
    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa(full_path: str):
        return FileResponse(FRONTEND_DIST / "index.html")

else:
    @app.get("/")
    async def no_front():
        return {"message": "Frontend not built"}

# -------------------- HEALTH --------------------
@app.get("/health")
async def health():
    return {"status": "ok"}
