from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from .database import init_db
from .routers import machines, users, logs, ping
from .initial_data import create_admin

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
create_admin()

# -------------------- ROUTERS API --------------------
app.include_router(machines.router, prefix="/api/machines")
app.include_router(users.router, prefix="/api/users")
app.include_router(logs.router, prefix="/api/logs")
app.include_router(ping.router, prefix="/api")

# -------------------- FRONTEND --------------------
frontend_dist = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"

if frontend_dist.exists():
    # Serve assets (JS/CSS/images)
    app.mount("/static", StaticFiles(directory=str(frontend_dist / "assets")), name="static")

    # Catch-all pour React Router
    @app.get("/{full_path:path}", include_in_schema=False)
    async def frontend_catchall(full_path: str):
        return FileResponse(frontend_dist / "index.html")
else:
    @app.get("/")
    def index():
        return {"message": "Frontend not built. Build frontend into frontend/dist to serve UI."}

# -------------------- MAIN --------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
