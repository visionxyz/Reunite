"""Vercel serverless entry point — exports the FastAPI ASGI app."""

import os
os.environ.setdefault("VERCEL", "1")

from dotenv import load_dotenv  # noqa: E402
load_dotenv()

from app.main import app  # noqa: E402, F401
