# config.py — Application configuration
import os

class Config:
    # ── Security ──────────────────────────────────────────────
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production-abc123xyz")

    # ── MySQL connection ──────────────────────────────────────
    # Adjust host/user/password/db to match your environment
    MYSQL_HOST     = os.environ.get("MYSQL_HOST",     "localhost")
    MYSQL_USER     = os.environ.get("MYSQL_USER",     "root")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "Arjun@2004")
    MYSQL_DB       = os.environ.get("MYSQL_DB",       "ai_article_builder")
    MYSQL_PORT     = int(os.environ.get("MYSQL_PORT", 3306))

    # ── Anthropic API ─────────────────────────────────────────
    # The proxy in this environment handles auth automatically;
    # we still expose the base URL so requests can be routed correctly.
    ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
    GEMINI_API_KEY = ""
    GEMINI_API_URL = ""

    # ── Misc ──────────────────────────────────────────────────
    DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
