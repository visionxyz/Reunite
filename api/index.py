"""Vercel serverless entry point — exports the FastAPI ASGI app."""

from dotenv import load_dotenv
load_dotenv()

from app.main import app  # noqa: E402, F401
