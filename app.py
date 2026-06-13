# app.py — Application factory / entry point
from flask import Flask
from config import Config
from models import close_db
from blueprints.auth      import auth_bp
from blueprints.dashboard import dashboard_bp
from blueprints.articles  import articles_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # ── Tear-down: close DB connection after each request ─────
    app.teardown_appcontext(close_db)

    # ── Register blueprints ───────────────────────────────────
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(articles_bp)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
