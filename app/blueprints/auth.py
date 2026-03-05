from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from app import db
from app.models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET","POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))
    error = None
    if request.method == "POST":
        username = request.form.get("username","").strip()
        password = request.form.get("password","")
        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password_hash, password):
            error = "Invalid username or password."
        elif not user.is_active:
            error = "Your account has been deactivated. Contact admin."
        else:
            login_user(user, remember=request.form.get("remember"))
            user.last_login = datetime.utcnow()
            db.session.commit()
            nxt = request.args.get("next")
            return redirect(nxt or url_for("dashboard.index"))
    return render_template("auth/login.html", error=error)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/change-password", methods=["GET","POST"])
@login_required
def change_password():
    error = success = None
    if request.method == "POST":
        old = request.form.get("old_password","")
        new = request.form.get("new_password","")
        confirm = request.form.get("confirm_password","")
        if not check_password_hash(current_user.password_hash, old):
            error = "Current password is incorrect."
        elif len(new) < 8:
            error = "New password must be at least 8 characters."
        elif new != confirm:
            error = "Passwords do not match."
        else:
            current_user.password_hash = generate_password_hash(new)
            db.session.commit()
            success = "Password changed successfully."
    return render_template("auth/change_password.html", error=error, success=success)
