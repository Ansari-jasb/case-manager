# Case Management System — Web App
### Cloud Deployment Guide (Render.com)

---

## ✅ What's Included

| Feature | Details |
|---|---|
| 🔐 Login system | Secure session-based authentication |
| 👥 4 user roles | Admin · Manager · Associate · Viewer |
| 🔒 Field-level permissions | Lock any field for any user |
| 📁 Cases | Full CRUD with search & filters |
| 🧾 Invoices | Track amounts, status, auto email alerts |
| 🏢 Clients | Client directory |
| 👥 Team | Staff management |
| 📧 Email notifications | New invoice → finance team auto-notified |
| 📋 Audit log | Every action logged with user + timestamp |

---

## 🚀 Deploy to Render.com (Free — 15 minutes)

### Step 1 — Push to GitHub
1. Create a free account at github.com
2. Create a new repository (e.g. `case-manager`)
3. Upload all files from this folder to that repository

### Step 2 — Connect to Render
1. Go to **render.com** → Sign up free
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repo
4. Set these values:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn wsgi:app`
   - **Python version:** 3.11

### Step 3 — Set Environment Variables
In Render dashboard → Environment tab, add:

| Variable | Value |
|---|---|
| `SECRET_KEY` | Any long random string |
| `SMTP_HOST` | `smtp.gmail.com` |
| `SMTP_PORT` | `587` |
| `SMTP_USER` | Your Gmail address |
| `SMTP_PASS` | Gmail App Password (see below) |
| `FINANCE_EMAIL` | Finance team email(s), comma-separated |
| `CRON_SECRET` | Any secret string for overdue alerts |

### Step 4 — Deploy
Click **"Deploy"** — Render will build and launch your app.
You'll get a URL like: `https://case-manager-xxxx.onrender.com`

**Share this URL with your team.** No installation needed.

---

## 📧 Gmail App Password Setup
Gmail requires an "App Password" (not your regular password):
1. Go to myaccount.google.com → Security
2. Enable 2-Step Verification
3. Go to Security → App Passwords
4. Generate a password for "Mail" → use this as `SMTP_PASS`

---

## 🔐 Default Login
After first deployment:
- **Username:** `admin`
- **Password:** `admin123`
- ⚠️ Change this immediately via the Change Password page

---

## 👤 User Roles Explained

| Role | View | Add | Edit | Delete | Scope |
|---|---|---|---|---|---|
| **Admin** | ✅ All | ✅ | ✅ | ✅ | Everything |
| **Manager** | ✅ All | ✅ | ✅ | ❌ | All cases |
| **Associate** | ✅ Own | ✅ | ✅ Own | ❌ | Only assigned cases |
| **Viewer** | ✅ All | ❌ | ❌ | ❌ | Read only |

## 🔒 Field-Level Permissions
As Admin, go to **Users & Permissions → 🔒 Permissions** for any user to:
- Grant/restrict View, Add, Edit, Delete per module
- Lock specific fields (e.g. lock "Amount" so associate can't change invoice amounts)

---

## 📧 Email Notifications
Automatic emails are sent when:
- ✅ A **new invoice** is created → finance team notified instantly
- ✅ An invoice is **marked Paid** → finance team notified
- ✅ **Overdue invoices** → call `/api/check-overdue?secret=YOUR_CRON_SECRET` daily

To set up daily overdue alerts, use a free cron service like **cron-job.org** to call:
```
GET https://your-app.onrender.com/api/check-overdue?secret=YOUR_CRON_SECRET
```

---

## 💾 Data Persistence on Render (Free Tier)
Render's free tier has **ephemeral storage** — the SQLite database resets on redeploy.

**To keep data permanently (recommended):**
- Upgrade to Render's paid tier ($7/mo) with a persistent disk, OR
- Use **Railway.app** free tier which includes persistent storage, OR
- Use **Supabase** (free PostgreSQL database) — I can upgrade the app for this on request

---

## 📁 File Structure
```
CaseManagerWeb/
├── wsgi.py              ← Gunicorn entry point
├── requirements.txt     ← Python dependencies
├── render.yaml          ← Render config
├── casemanager.db       ← SQLite database (auto-created)
├── app/
│   ├── models.py        ← Database + all queries
│   ├── routes.py        ← All Flask routes
│   └── email_service.py ← Email notifications
└── templates/           ← HTML templates
    ├── base.html
    ├── login.html
    ├── dashboard.html
    ├── cases.html / case_form.html / case_detail.html
    ├── invoices.html / invoice_form.html
    ├── clients.html / client_form.html
    ├── team.html / team_form.html
    ├── admin_users.html / admin_user_form.html
    ├── admin_permissions.html
    ├── audit_log.html
    └── change_password.html
```
