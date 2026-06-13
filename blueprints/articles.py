# blueprints/articles.py — Article generation & management routes
import json, requests
from flask import (Blueprint, render_template, request, session,
                   redirect, url_for, flash, jsonify, current_app)
from models import (save_article, get_articles_by_user, get_article_by_id,
                    update_article, delete_article)

articles_bp = Blueprint("articles", __name__)

CATEGORIES = [
    "Technology", "Health & Wellness", "Business", "Finance",
    "Education", "Travel", "Food & Cooking", "Lifestyle",
    "Science", "Sports", "Entertainment", "Politics",
    "Environment", "Fashion", "Real Estate", "Marketing",
]

LENGTH_WORDS = {"short": "~300 words", "medium": "~600 words", "long": "~1200 words"}


# ── Guard decorator ───────────────────────────────────────────
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


# ── Generate page ─────────────────────────────────────────────
@articles_bp.route("/generate", methods=["GET"])
@login_required
def generate():
    return render_template("generate.html", categories=CATEGORIES)


@articles_bp.route("/generate", methods=["POST"])
@login_required
def generate_post():
    """AJAX endpoint — streams the AI call and returns JSON."""
    data     = request.get_json(silent=True) or {}
    title    = data.get("title", "").strip()
    keywords = data.get("keywords", "").strip()
    category = data.get("category", "Technology").strip()
    length   = data.get("length", "medium").lower()
    language = data.get("language", "english").lower()

    if not title:
        return jsonify({"error": "Title is required."}), 400

    # ── Build AI prompt ───────────────────────────────────────
    word_target = LENGTH_WORDS.get(length, "~600 words")
    lang_label  = language.capitalize()

    system_prompt = (
        "You are an expert SEO content writer. "
        "Always respond with valid JSON only — no markdown fences, no extra text."
    )

    user_prompt = f"""Write a complete, SEO-friendly article in {lang_label}.

Article details:
- Title: {title}
- Keywords: {keywords}
- Category: {category}
- Target length: {word_target}

Return ONLY this JSON structure:
{{
  "title": "...",
  "meta_description": "150-160 char meta description",
  "seo_keywords": "comma-separated SEO keywords",
  "content": "Full article in HTML with <h2>, <h3>, <p> tags. Must include: introduction, 3-5 sections with headings, and a conclusion."
}}"""

    try:
        
        resp = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen2.5:3b",
                "prompt": system_prompt + "\n\n" + user_prompt,
                "stream": False
            },
            timeout=120
        )

        resp.raise_for_status()

        raw = resp.json()["response"].strip()
        print("OLLAMA RESPONSE REPR:")
        print(repr(raw))
        raw = raw.replace("\r", "\\r").replace("\n","\\n")

        article = {
            "title": title,
            "meta_description": "",
            "seo_keywords": keywords,
            "content": raw.replace("\\n", "<br>")
        }

    except requests.RequestException as e:
        return jsonify({"error": f"Ollama error: {str(e)}"}), 502

    except (json.JSONDecodeError, KeyError) as e:
        return jsonify({"error": f"Could not parse AI response: {str(e)}"}), 500
        
        
    

    # ── Persist to DB ─────────────────────────────────────────
    art_id = save_article(
        user_id         = session["user_id"],
        title           = article.get("title", title),
        keywords        = keywords,
        category        = category,
        length          = length,
        language        = language,
        content         = article.get("content", ""),
        meta_description= article.get("meta_description", ""),
        seo_keywords    = article.get("seo_keywords", ""),
    )
    article["id"] = art_id
    return jsonify({"article": article})


# ── History page ──────────────────────────────────────────────
@articles_bp.route("/history")
@login_required
def history():
    search   = request.args.get("q", "").strip()
    arts     = get_articles_by_user(session["user_id"], search)
    return render_template("history.html", articles=arts, search=search)


# ── View single article ───────────────────────────────────────
@articles_bp.route("/article/<int:art_id>")
@login_required
def view_article(art_id):
    art = get_article_by_id(art_id, session["user_id"])
    if not art:
        flash("Article not found.", "error")
        return redirect(url_for("articles.history"))
    return render_template("view_article.html", article=art)


# ── Edit ──────────────────────────────────────────────────────
@articles_bp.route("/article/<int:art_id>/edit", methods=["GET", "POST"])
@login_required
def edit_article(art_id):
    art = get_article_by_id(art_id, session["user_id"])
    if not art:
        flash("Article not found.", "error")
        return redirect(url_for("articles.history"))

    if request.method == "POST":
        title    = request.form.get("title", "").strip()
        content  = request.form.get("content", "").strip()
        meta     = request.form.get("meta_description", "").strip()
        seo_kw   = request.form.get("seo_keywords", "").strip()
        update_article(art_id, session["user_id"], title, content, meta, seo_kw)
        flash("Article updated successfully.", "success")
        return redirect(url_for("articles.view_article", art_id=art_id))

    return render_template("edit_article.html", article=art)


# ── Delete ────────────────────────────────────────────────────
@articles_bp.route("/article/<int:art_id>/delete", methods=["POST"])
@login_required
def delete_article_route(art_id):
    delete_article(art_id, session["user_id"])
    flash("Article deleted.", "info")
    return redirect(url_for("articles.history"))
