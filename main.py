from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os
import time
import datetime
import psutil

app = FastAPI(title="Potato Server")

app.mount("/fonts", StaticFiles(directory="fonts"), name="fonts")
templates = Jinja2Templates(directory="templates")


# -------------------------------------------------------------
# STATS HELPERS (Android/Termux blocks /proc/stat)
# -------------------------------------------------------------
NCPU = os.cpu_count() or 8
_system_cpu_ok = True


def cpu_percent_safe():
    global _system_cpu_ok
    if _system_cpu_ok:
        try:
            return psutil.cpu_percent(interval=None)
        except (PermissionError, OSError):
            _system_cpu_ok = False  # Android blocks /proc/stat

    # Fallback: add up CPU use of every process Termux lets us see
    total = 0.0
    for p in psutil.process_iter():
        try:
            total += p.cpu_percent(interval=None)
        except (psutil.Error, OSError):
            continue
    return round(min(100.0, total / NCPU), 1)


def uptime_hours():
    try:
        return round(time.clock_gettime(time.CLOCK_BOOTTIME) / 3600, 1)
    except Exception:
        try:
            return round((time.time() - psutil.boot_time()) / 3600, 1)
        except Exception:
            return 0.0


def read_stats():
    try:
        ram = psutil.virtual_memory()
        total_b, used_b = ram.total, ram.total - ram.available
    except (PermissionError, OSError):
        total_b, used_b = 12 * 1024**3, 0  # placeholder if /proc/meminfo is blocked too

    return {
        "cpu_percent": cpu_percent_safe(),
        "ram_used_gb": round(used_b / (1024**3), 2),
        "ram_total_gb": round(total_b / (1024**3), 2),
        "ram_percent": round(used_b / total_b * 100, 1),
        "uptime_hours": uptime_hours(),
    }


# -------------------------------------------------------------
# 1. SERVER-SIDE RENDERED HOMEPAGE
# -------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    context = {
        "request": request,
        "server_name": "Potato Node 01 (Samsung S22 Ultra)",
        **read_stats(),
    }
    return templates.TemplateResponse(request=request, name="index.html", context=context)


# -------------------------------------------------------------
# 2. REST API ENDPOINTS
# -------------------------------------------------------------
@app.get("/api/stats")
async def stats():
    return read_stats()


@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "node": "s22-ultra-junkbox",
        "timestamp": datetime.datetime.utcnow().isoformat(),
    }


@app.get("/api/projects")
async def list_projects():
    return [
        {
            "id": "rag-system",
            "name": "RAG From Scratch",
            "url": "https://rag.runsonpotato.dev",
            "description": "Custom retrieval-augmented generation engine.",
        },
        {
            "id": "nothingness",
            "name": "Nothingness",
            "url": "https://nothingness.runsonpotato.dev",
            "description": "Literally nothing. A peaceful waste of time.",
        },
    ]