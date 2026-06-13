# models.py — Database helper functions using PyMySQL directly
import pymysql
import pymysql.cursors
from flask import current_app, g
from werkzeug.security import generate_password_hash, check_password_hash


# ─────────────────────────────────────────────────────────────
# Connection management
# ─────────────────────────────────────────────────────────────

def get_db():
    """Return (and cache) a per-request database connection."""
    if "db" not in g:
        cfg = current_app.config
        g.db = pymysql.connect(
            host=cfg["MYSQL_HOST"],
            user=cfg["MYSQL_USER"],
            password=cfg["MYSQL_PASSWORD"],
            database=cfg["MYSQL_DB"],
            port=cfg["MYSQL_PORT"],
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True,
        )
    return g.db


def close_db(e=None):
    """Close the DB connection at the end of the request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


# ─────────────────────────────────────────────────────────────
# User helpers
# ─────────────────────────────────────────────────────────────

def create_user(username: str, email: str, password: str) -> int | None:
    """Insert a new user; return new id or None on duplicate."""
    hashed = generate_password_hash(password)
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute(
                "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                (username, email, hashed),
            )
        return db.insert_id()
    except pymysql.IntegrityError:
        return None


def get_user_by_email(email: str) -> dict | None:
    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT * FROM users WHERE email = %s LIMIT 1", (email,))
        return cur.fetchone()


def get_user_by_id(user_id: int) -> dict | None:
    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT * FROM users WHERE id = %s LIMIT 1", (user_id,))
        return cur.fetchone()


def verify_password(stored_hash: str, password: str) -> bool:
    return check_password_hash(stored_hash, password)


def update_last_login(user_id: int):
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            "UPDATE users SET last_login = NOW() WHERE id = %s", (user_id,)
        )


# ─────────────────────────────────────────────────────────────
# Article helpers
# ─────────────────────────────────────────────────────────────

def save_article(user_id, title, keywords, category, length, language,
                 content, meta_description, seo_keywords) -> int:
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            """INSERT INTO articles
               (user_id, title, keywords, category, length, language,
                content, meta_description, seo_keywords)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (user_id, title, keywords, category, length, language,
             content, meta_description, seo_keywords),
        )
    return db.insert_id()


def get_articles_by_user(user_id: int, search: str = "") -> list:
    db = get_db()
    with db.cursor() as cur:
        if search:
            like = f"%{search}%"
            cur.execute(
                """SELECT id, title, category, keywords, length, language,
                          meta_description, created_at, updated_at
                   FROM articles
                   WHERE user_id = %s
                     AND (title LIKE %s OR category LIKE %s OR keywords LIKE %s)
                   ORDER BY created_at DESC""",
                (user_id, like, like, like),
            )
        else:
            cur.execute(
                """SELECT id, title, category, keywords, length, language,
                          meta_description, created_at, updated_at
                   FROM articles
                   WHERE user_id = %s
                   ORDER BY created_at DESC""",
                (user_id,),
            )
        return cur.fetchall()


def get_article_by_id(article_id: int, user_id: int) -> dict | None:
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT * FROM articles WHERE id = %s AND user_id = %s LIMIT 1",
            (article_id, user_id),
        )
        return cur.fetchone()


def update_article(article_id: int, user_id: int, title: str,
                   content: str, meta_description: str, seo_keywords: str):
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            """UPDATE articles
               SET title=%s, content=%s, meta_description=%s,
                   seo_keywords=%s, updated_at=NOW()
               WHERE id=%s AND user_id=%s""",
            (title, content, meta_description, seo_keywords, article_id, user_id),
        )


def delete_article(article_id: int, user_id: int):
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            "DELETE FROM articles WHERE id = %s AND user_id = %s",
            (article_id, user_id),
        )


def get_dashboard_stats(user_id: int) -> dict:
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT COUNT(*) AS total FROM articles WHERE user_id=%s", (user_id,)
        )
        total = cur.fetchone()["total"]

        cur.execute(
            """SELECT COUNT(DISTINCT category) AS cats
               FROM articles WHERE user_id=%s""",
            (user_id,),
        )
        cats = cur.fetchone()["cats"]

        cur.execute(
            """SELECT id, title, category, created_at
               FROM articles WHERE user_id=%s
               ORDER BY created_at DESC LIMIT 5""",
            (user_id,),
        )
        recent = cur.fetchall()

    return {"total_articles": total, "total_categories": cats, "recent": recent}
