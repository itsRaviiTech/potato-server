from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import psutil
import datetime

app = FastAPI(title="Potato Server")

# This tells FastAPI to serve the "fonts" folder at the "/fonts" URL path
app.mount("/fonts", StaticFiles(directory="fonts"), name="fonts")

# Point Jinja2 to the "templates" folder
templates = Jinja2Templates(directory="templates")


# -------------------------------------------------------------
# 1. SERVER-SIDE RENDERED HOMEPAGE
# -------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    # Read live machine stats (works on PC & Android Termux)
    ram = psutil.virtual_memory()
    cpu_percent = psutil.cpu_percent(interval=None)
    uptime_seconds = int(datetime.datetime.now().timestamp() - psutil.boot_time())
    uptime_hours = round(uptime_seconds / 3600, 1)

    context = {
        "request": request,
        "server_name": "Potato Node 01 (Samsung S22 Ultra)",
        "ram_used_gb": round(ram.used / (1024**3), 2),
        "ram_total_gb": round(ram.total / (1024**3), 2),
        "ram_percent": ram.percent,
        "cpu_percent": cpu_percent,
        "uptime_hours": uptime_hours,
    }
    return templates.TemplateResponse(request=request, name="index.html", context=context)


# -------------------------------------------------------------
# 2. REST API ENDPOINTS (For your external tools / RAG)
# -------------------------------------------------------------
@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "node": "s22-ultra-junkbox",
        "timestamp": datetime.datetime.utcnow().isoformat()
    }

@app.get("/api/projects")
async def list_projects():
    # Mock data representing your active projects
    return [
        {
            "id": "rag-system",
            "name": "RAG From Scratch",
            "url": "https://rag.runsonpotato.dev",
            "description": "Custom retrieval-augmented generation engine."
        },
        {
            "id": "nothingness",
            "name": "Nothingness",
            "url": "https://nothingness.runsonpotato.dev",
            "description": "Literally nothing. A peaceful waste of time."
        }
    ]