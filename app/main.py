"""FastAPI application for Reunite - 团圆寻亲平台."""

import os
import traceback
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Form, Body
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.models import Entry
from app import database as db
from app import matching
from app import assistant
from app.mock_data import PARENT_ENTRIES, CHILD_ENTRIES

IS_VERCEL = bool(os.environ.get("VERCEL"))
BASE_DIR = Path(__file__).parent

_db_ready = False


def _ensure_db():
    """Init DB and load mock data if empty."""
    global _db_ready
    if _db_ready:
        return
    db.init_db()
    existing = db.get_all_entries()
    if not existing:
        print("Loading mock data...")
        for entry in PARENT_ENTRIES + CHILD_ENTRIES:
            entry_id = db.insert_entry(entry)
            entry.id = entry_id
            if not IS_VERCEL:
                matching.store_memory(entry)
        print(f"Loaded {len(PARENT_ENTRIES)} parent entries and {len(CHILD_ENTRIES)} child entries.")
    _db_ready = True


@asynccontextmanager
async def lifespan(app):
    try:
        _ensure_db()
    except Exception as e:
        print(f"Startup error: {e}")
        traceback.print_exc()
    yield


app = FastAPI(title="Reunite", lifespan=lifespan)

# Mount static files
static_dir = BASE_DIR / "static"
if static_dir.is_dir():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/entries")
async def list_entries(entry_type: str | None = None):
    _ensure_db()
    entries = db.get_all_entries(entry_type=entry_type)
    return [e.to_dict() for e in entries]


@app.get("/api/entries/{entry_id}")
async def get_entry(entry_id: int):
    entry = db.get_entry(entry_id)
    if not entry:
        return JSONResponse({"error": "Not found"}, status_code=404)
    return entry.to_dict()


@app.post("/api/entries")
async def create_entry(
    entry_type: str = Form(...),
    name: str = Form(""),
    gender: str = Form(""),
    birth_date: str = Form(""),
    missing_date: str = Form(""),
    location: str = Form(""),
    physical_features: str = Form(""),
    description: str = Form(""),
    contact: str = Form(""),
):
    entry = Entry(
        entry_type=entry_type,
        name=name,
        gender=gender,
        birth_date=birth_date,
        missing_date=missing_date,
        location=location,
        physical_features=physical_features,
        description=description,
        contact=contact,
    )
    entry_id = db.insert_entry(entry)
    entry.id = entry_id
    matching.store_memory(entry)
    return {"id": entry_id, "message": "登记成功"}


@app.put("/api/entries/{entry_id}")
async def update_entry(entry_id: int, payload: dict = Body(...)):
    """Update an existing entry and refresh its EverMemOS memories."""
    entry = db.get_entry(entry_id)
    if not entry:
        return JSONResponse({"error": "Not found"}, status_code=404)

    db.update_entry(entry_id, **payload)
    updated = db.get_entry(entry_id)

    # Re-store in EverOS with updated info — clear stale memories first
    matching.delete_memory(updated)
    matching.store_memory(updated)

    return updated.to_dict()


@app.get("/api/match/{entry_id}")
async def match_entry(entry_id: int, top_k: int = 10, min_score: float = matching.DEFAULT_MIN_SCORE):
    entry = db.get_entry(entry_id)
    if not entry:
        return JSONResponse({"error": "Not found"}, status_code=404)
    results = matching.find_matches(entry, top_k=top_k, min_score=min_score)
    return [
        {"entry": r.entry.to_dict(), "score": round(r.score, 4)}
        for r in results
    ]


@app.post("/api/search")
async def search(
    entry_type: str = Form(...),
    description: str = Form(""),
    location: str = Form(""),
    physical_features: str = Form(""),
    gender: str = Form(""),
    birth_date: str = Form(""),
):
    """Quick search without saving - create a temporary entry and match."""
    query_entry = Entry(
        entry_type=entry_type,
        gender=gender,
        birth_date=birth_date,
        location=location,
        physical_features=physical_features,
        description=description,
    )
    results = matching.find_matches(query_entry, top_k=10)
    return [
        {"entry": r.entry.to_dict(), "score": round(r.score, 4)}
        for r in results
    ]


@app.post("/api/chat")
async def chat_with_assistant(payload: dict = Body(...)):
    """AI assistant conversation to guide users in recalling details."""
    entry_id = payload.get("entry_id")
    entry_info = payload.get("entry_info", {})
    messages = payload.get("messages", [])

    # If entry_id provided, load existing entry info as base
    if entry_id:
        existing = db.get_entry(entry_id)
        if existing:
            base = existing.to_dict()
            base.update({k: v for k, v in entry_info.items() if v})
            entry_info = base

    reply = await assistant.chat(entry_id, entry_info, messages)

    # If entry_id provided and user sent a message, append it as new memory
    if entry_id and messages:
        last_user_msg = None
        for m in reversed(messages):
            if m.get("role") == "user":
                last_user_msg = m["content"]
                break
        if last_user_msg:
            entry = db.get_entry(entry_id)
            if entry:
                matching.store_chat_memory(entry, last_user_msg)

    return {"reply": reply}
