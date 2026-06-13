# blueprints/dashboard.py — Dashboard route
from flask import Blueprint, render_template, session, redirect, url_for
from models import get_dashboard_stats, get_user_by_id

dashboard_bp = Blueprint("dashboard", __name__)


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


@dashboard_bp.route("/")
@dashboard_bp.route("/dashboard")
@login_required
def index():
    stats = get_dashboard_stats(session["user_id"])
    user  = get_user_by_id(session["user_id"])
    return render_template("dashboard.html", stats=stats, user=user)
