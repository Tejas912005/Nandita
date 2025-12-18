# TeleMed - PythonAnywhere Deployment Guide

## Step 1: Create PythonAnywhere Account
1. Go to [pythonanywhere.com](https://www.pythonanywhere.com)
2. Click **"Start running Python online"** → **"Create a Beginner account"** (FREE)
3. Sign up with your email

---

## Step 2: Upload Your Project

### Option A: Upload as ZIP (Easier)
1. Zip your entire `Nandita` folder
2. In PythonAnywhere dashboard → **Files** tab
3. Click **Upload a file** → select your ZIP
4. Open a **Bash console** and unzip:
   ```bash
   cd ~
   unzip Nandita.zip
   ```

### Option B: Use Git (Better for updates)
1. Push your project to GitHub
2. In PythonAnywhere Bash console:
   ```bash
   git clone https://github.com/YOUR_USERNAME/Nandita.git
   ```

---

## Step 3: Set Up Virtual Environment
In PythonAnywhere **Bash console**:
```bash
cd ~/Nandita
mkvirtualenv --python=/usr/bin/python3.10 telemed-env
pip install django pillow qrcode
```

---

## Step 4: Configure Web App
1. Go to **Web** tab → **Add a new web app**
2. Choose **Manual configuration** → **Python 3.10**
3. Set these values:

| Setting | Value |
|---------|-------|
| **Source code** | `/home/YOUR_USERNAME/Nandita` |
| **Working directory** | `/home/YOUR_USERNAME/Nandita` |
| **Virtualenv** | `/home/YOUR_USERNAME/.virtualenvs/telemed-env` |

---

## Step 5: Configure WSGI File
Click on the **WSGI configuration file** link and replace ALL content with:

```python
import os
import sys

path = '/home/YOUR_USERNAME/Nandita'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'telemedicine.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

**Replace `YOUR_USERNAME` with your actual PythonAnywhere username!**

---

## Step 6: Configure Static Files
In **Web** tab, scroll to **Static files** section and add:

| URL | Directory |
|-----|-----------|
| `/static/` | `/home/YOUR_USERNAME/Nandita/staticfiles` |
| `/media/` | `/home/YOUR_USERNAME/Nandita/media` |

---

## Step 7: Initialize Database
In **Bash console**:
```bash
cd ~/Nandita
workon telemed-env
python manage.py migrate
python init_data.py
```

---

## Step 8: Reload and Test!
1. Click the green **Reload** button in Web tab
2. Visit: `https://YOUR_USERNAME.pythonanywhere.com`

---

## Your Site Will Be Live At:
**https://YOUR_USERNAME.pythonanywhere.com**

---

## Troubleshooting

**Error: "Something went wrong"**
- Check **Error log** in Web tab
- Make sure virtualenv path is correct

**Static files not loading**
- Verify static files mapping in Web tab
- Run `python manage.py collectstatic`

**Database errors**
- Run migrations: `python manage.py migrate`
