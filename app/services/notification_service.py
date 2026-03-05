"""
Notification service — due date checks + email alerts
"""
from datetime import date, timedelta
from flask import render_template_string
from flask_mail import Message


def run_due_date_check(app):
    """Called by APScheduler every 12 hours."""
    with app.app_context():
        from app import db, mail
        from app.models import Case, User, Notification

        today     = date.today()
        d3        = today + timedelta(days=3)
        d7        = today + timedelta(days=7)
        all_users = User.query.filter_by(is_active=True).all()

        cases = Case.query.filter(
            Case.compliance_date.isnot(None),
            Case.status.notin_(["Completed", "Case Closed"])
        ).all()

        for case in cases:
            cd = case.compliance_date
            days_left = (cd - today).days

            triggers = []
            if days_left == 7 and not case.notified_7:
                triggers.append(("7 days", "warning", "notified_7"))
            if days_left == 3 and not case.notified_3:
                triggers.append(("3 days", "danger",  "notified_3"))
            if days_left <= 0 and not case.notified_0:
                triggers.append(("TODAY / OVERDUE", "danger", "notified_0"))

            for label, ntype, flag in triggers:
                client_name  = case.client.name  if case.client  else "Unknown"
                assignee_name = case.assignee.name if case.assignee else "Unassigned"

                title   = f"Due Date Alert — {label}"
                message = (f"Case: {case.case_details[:80]}\n"
                           f"Client: {client_name}\n"
                           f"Compliance Date: {cd}\n"
                           f"Assignee: {assignee_name}")
                link    = f"/cases/{case.id}"

                # In-app notifications for all active users
                for user in all_users:
                    notif = Notification(
                        user_id=user.id,
                        title=title,
                        message=message,
                        type=ntype,
                        link=link,
                    )
                    db.session.add(notif)

                # Email notification
                _send_due_email(app, mail, case, label, cd, client_name, assignee_name)

                # Mark as notified
                setattr(case, flag, True)

        db.session.commit()


def _send_due_email(app, mail, case, label, due_date, client_name, assignee_name):
    try:
        from app.models import User
        recipients = [u.email for u in User.query.filter(
            User.is_active == True,
            User.role.in_(["admin", "manager"])
        ).all() if u.email]

        assignee = case.assignee
        if assignee and assignee.email:
            if assignee.email not in recipients:
                recipients.append(assignee.email)

        if not recipients:
            return

        subject = f"[Case Manager] Due Date Alert — {label} — {case.case_details[:50]}"

        body = f"""
Due Date Alert: {label}

Case Details : {case.case_details}
Client       : {client_name}
File No.     : {case.file_no or '—'}
Compliance   : {due_date}
Assignee     : {assignee_name}
Status       : {case.status}

Progress:
{case.progress or 'No progress notes.'}

---
This is an automated alert from Case Manager.
Login at your app URL to view full details.
"""
        msg = Message(subject=subject, recipients=recipients, body=body)
        mail.send(msg)
    except Exception as e:
        print(f"Email send failed: {e}")


def create_notification(user_id, title, message, ntype="info", link=None):
    """Helper to manually create a notification."""
    from app import db
    from app.models import Notification
    n = Notification(user_id=user_id, title=title,
                     message=message, type=ntype, link=link)
    db.session.add(n)
    db.session.commit()
