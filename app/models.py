from datetime import datetime
from flask_login import UserMixin
from app import db, login_mgr

ROLES   = ["admin", "manager", "associate", "viewer"]
MODULES = ["cases", "invoices", "clients", "team"]
ACTIONS = ["view","add","edit","delete","edit_status","edit_progress",
           "edit_invoice_status","edit_compliance_date","edit_completion_date","edit_assignee"]

ROLE_DEFAULTS = {
    "admin":   {m: {a: True for a in ACTIONS} for m in MODULES},
    "manager": {m: {a: a != "delete" for a in ACTIONS} for m in MODULES},
    "associate": {
        "cases":    {a: a in ["view","edit","edit_status","edit_progress",
                              "edit_compliance_date","edit_completion_date"] for a in ACTIONS},
        "invoices": {a: a in ["view"] for a in ACTIONS},
        "clients":  {a: a in ["view"] for a in ACTIONS},
        "team":     {a: a in ["view"] for a in ACTIONS},
    },
    "viewer":  {m: {a: a == "view" for a in ACTIONS} for m in MODULES},
}

@login_mgr.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(64),  unique=True, nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name     = db.Column(db.String(120))
    role          = db.Column(db.String(20), default="viewer")
    is_active     = db.Column(db.Boolean,    default=True)
    created_at    = db.Column(db.DateTime,   default=datetime.utcnow)
    last_login    = db.Column(db.DateTime)
    permissions   = db.relationship("Permission",    back_populates="user", cascade="all, delete-orphan")
    notifications = db.relationship("Notification",  back_populates="user", cascade="all, delete-orphan")

    def get_id(self): return str(self.id)

    def can(self, module, action):
        if self.role == "admin": return True
        perm = Permission.query.filter_by(user_id=self.id, module=module, action=action).first()
        if perm: return perm.allowed
        return ROLE_DEFAULTS.get(self.role, {}).get(module, {}).get(action, False)

    def unread_count(self):
        return Notification.query.filter_by(user_id=self.id, is_read=False).count()

class Permission(db.Model):
    __tablename__ = "permissions"
    id      = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    module  = db.Column(db.String(32), nullable=False)
    action  = db.Column(db.String(32), nullable=False)
    allowed = db.Column(db.Boolean,    default=False)
    user    = db.relationship("User", back_populates="permissions")
    __table_args__ = (db.UniqueConstraint("user_id","module","action"),)

class Client(db.Model):
    __tablename__ = "clients"
    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(200), nullable=False)
    ntn        = db.Column(db.String(30))
    contact    = db.Column(db.String(120))
    email      = db.Column(db.String(120))
    address    = db.Column(db.Text)
    notes      = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    cases      = db.relationship("Case",    back_populates="client")
    invoices   = db.relationship("Invoice", back_populates="client")

class TeamMember(db.Model):
    __tablename__ = "team_members"
    id        = db.Column(db.Integer, primary_key=True)
    name      = db.Column(db.String(120), nullable=False)
    role      = db.Column(db.String(80))
    email     = db.Column(db.String(120))
    phone     = db.Column(db.String(40))
    is_active = db.Column(db.Boolean, default=True)
    user_id   = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    cases     = db.relationship("Case", back_populates="assignee")

class Case(db.Model):
    __tablename__ = "cases"
    id              = db.Column(db.Integer, primary_key=True)
    file_no         = db.Column(db.String(50))
    client_id       = db.Column(db.Integer, db.ForeignKey("clients.id"))
    case_details    = db.Column(db.Text, nullable=False)
    tax_period      = db.Column(db.String(50))
    assignee_id     = db.Column(db.Integer, db.ForeignKey("team_members.id"))
    status          = db.Column(db.String(40), default="Under Preparation")
    priority        = db.Column(db.String(20), default="Normal")
    compliance_date = db.Column(db.Date)
    completion_date = db.Column(db.Date)
    progress        = db.Column(db.Text)
    notes           = db.Column(db.Text)
    notified_7      = db.Column(db.Boolean, default=False)
    notified_3      = db.Column(db.Boolean, default=False)
    notified_0      = db.Column(db.Boolean, default=False)
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at      = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    client          = db.relationship("Client",     back_populates="cases")
    assignee        = db.relationship("TeamMember", back_populates="cases")
    invoices        = db.relationship("Invoice",    back_populates="case")
    history         = db.relationship("CaseHistory", back_populates="case", cascade="all, delete-orphan")

class CaseHistory(db.Model):
    __tablename__ = "case_history"
    id         = db.Column(db.Integer, primary_key=True)
    case_id    = db.Column(db.Integer, db.ForeignKey("cases.id"), nullable=False)
    field      = db.Column(db.String(60))
    old_value  = db.Column(db.Text)
    new_value  = db.Column(db.Text)
    changed_by = db.Column(db.String(80))
    changed_at = db.Column(db.DateTime, default=datetime.utcnow)
    case       = db.relationship("Case", back_populates="history")

class Invoice(db.Model):
    __tablename__ = "invoices"
    id          = db.Column(db.Integer, primary_key=True)
    invoice_no  = db.Column(db.String(50), unique=True)
    case_id     = db.Column(db.Integer, db.ForeignKey("cases.id"))
    client_id   = db.Column(db.Integer, db.ForeignKey("clients.id"))
    description = db.Column(db.Text)
    amount      = db.Column(db.Float, default=0)
    status      = db.Column(db.String(20), default="Pending")
    issue_date  = db.Column(db.Date)
    due_date    = db.Column(db.Date)
    paid_date   = db.Column(db.Date)
    notes       = db.Column(db.Text)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    case        = db.relationship("Case",   back_populates="invoices")
    client      = db.relationship("Client", back_populates="invoices")

class Notification(db.Model):
    __tablename__ = "notifications"
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title      = db.Column(db.String(200))
    message    = db.Column(db.Text)
    type       = db.Column(db.String(20), default="info")
    link       = db.Column(db.String(200))
    is_read    = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user       = db.relationship("User", back_populates="notifications")
