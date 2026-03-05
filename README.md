# Case Manager — Render Deployment

## Default Login
- Username: `admin`
- Password: `Admin@1234`  ← Change immediately after first login

---

## How to Upload to GitHub (No Git knowledge needed)

1. Go to **github.com** → sign in or sign up free
2. Click the **"+"** button (top right) → **"New repository"**
3. Name it `case-manager` → leave everything else default → click **"Create repository"**
4. On the next page, click **"uploading an existing file"**
5. Extract this zip on your computer
6. **Select ALL files and folders** inside the extracted folder → drag them into GitHub
7. Scroll down → click **"Commit changes"**

> ⚠️ Important: Upload the FILES INSIDE the folder, not the folder itself.
> GitHub should show: `wsgi.py`, `requirements.txt`, `app/`, `render.yaml` at the root level.

---

## Deploy on Render

1. Go to **render.com** → sign up free
2. Click **"New +"** → **"Web Service"**
3. Click **"Connect GitHub"** → authorize → select your `case-manager` repo
4. Fill in:
   - **Name**: case-manager
   - **Region**: pick closest to you
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn wsgi:app --workers 2 --bind 0.0.0.0:$PORT`
   - **Plan**: Free
5. Scroll to **Environment Variables** → add:

| Key | Value |
|-----|-------|
| SECRET_KEY | (click Generate) |
| ADMIN_EMAIL | your email |
| MAIL_USERNAME | your Gmail |
| MAIL_PASSWORD | Gmail App Password |
| MAIL_SERVER | smtp.gmail.com |
| MAIL_PORT | 587 |

6. Click **"Create Web Service"**
7. Wait ~3 minutes for build to finish
8. Click the URL Render gives you — your app is live!

---

## Gmail App Password Setup
1. myaccount.google.com → Security
2. Enable 2-Step Verification
3. Search "App Passwords" → create one for Mail
4. Use that 16-character code as MAIL_PASSWORD

---

## Adding Team Members
Admin → Users → Add User → set username, role, temporary password → share URL + credentials
