"""
Case Management Web App — Application Factory
"""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from apscheduler.schedulers.background import BackgroundScheduler

db        = SQLAlchemy()
login_mgr = LoginManager()
mail      = Mail()
scheduler = BackgroundScheduler(daemon=True)


def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"]          = os.environ.get("SECRET_KEY", "dev-secret-change-in-prod")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", "sqlite:///case_manager.db"
    ).replace("postgres://", "postgresql://")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config["MAIL_SERVER"]         = os.environ.get("MAIL_SERVER",  "smtp.gmail.com")
    app.config["MAIL_PORT"]           = int(os.environ.get("MAIL_PORT", 587))
    app.config["MAIL_USE_TLS"]        = True
    app.config["MAIL_USERNAME"]       = os.environ.get("MAIL_USERNAME", "")
    app.config["MAIL_PASSWORD"]       = os.environ.get("MAIL_PASSWORD", "")
    app.config["MAIL_DEFAULT_SENDER"] = os.environ.get("MAIL_USERNAME", "noreply@casemanager.com")
    app.config["APP_NAME"]            = "Case Manager"
    app.config["ADMIN_EMAIL"]         = os.environ.get("ADMIN_EMAIL", "admin@firm.com")

    db.init_app(app)
    mail.init_app(app)
    login_mgr.init_app(app)
    login_mgr.login_view             = "auth.login"
    login_mgr.login_message          = "Please log in to access this page."
    login_mgr.login_message_category = "warning"

    from app.blueprints.auth          import auth_bp
    from app.blueprints.dashboard     import dashboard_bp
    from app.blueprints.cases         import cases_bp
    from app.blueprints.invoices      import invoices_bp
    from app.blueprints.clients       import clients_bp
    from app.blueprints.team          import team_bp
    from app.blueprints.admin         import admin_bp
    from app.blueprints.notifications import notif_bp
    from app.blueprints.import_data   import import_bp

    for bp in [auth_bp, dashboard_bp, cases_bp, invoices_bp,
               clients_bp, team_bp, admin_bp, notif_bp, import_bp]:
        app.register_blueprint(bp)

    with app.app_context():
        db.create_all()
        _seed_defaults()

    if not scheduler.running:
        from app.services.notification_service import run_due_date_check
        scheduler.add_job(run_due_date_check, "interval", hours=12,
                          args=[app], id="due_check", replace_existing=True)
        scheduler.start()

    return app


def _seed_defaults():
    from app.models import User
    if User.query.count() == 0:
        from werkzeug.security import generate_password_hash
        admin = User(
            username="admin",
            email=os.environ.get("ADMIN_EMAIL", "admin@firm.com"),
            password_hash=generate_password_hash("Admin@1234"),
            full_name="System Administrator",
            role="admin",
            is_active=True,
        )
        db.session.add(admin)
        db.session.commit()
        print("Default admin: username=admin  password=Admin@1234")

