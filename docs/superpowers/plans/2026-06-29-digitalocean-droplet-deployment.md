# DigitalOcean Droplet Deployment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Serve the Flask portfolio site in production on the existing DigitalOcean Droplet, reachable over HTTP at `http://selisah.duckdns.org`.

**Architecture:** Gunicorn runs the Flask app (`app:app`) bound to a unix socket; systemd supervises Gunicorn (auto-restart + start on boot); nginx listens on port 80, serves `/static/` directly, and reverse-proxies everything else to the Gunicorn socket.

**Tech Stack:** Ubuntu, Python 3 venv, Flask 2.0.1, Gunicorn, systemd, nginx.

---

## Conventions Used In This Plan

Two values depend on your specific Droplet. **Set them once per SSH session** and every later command reuses them. Run these right after you SSH in:

```bash
# The Linux user that owns the cloned repo and will run gunicorn.
# On a default DigitalOcean droplet this is often `root`. Use `whoami` to check.
export APP_USER="$(whoami)"

# Absolute path to the already-cloned repo. Adjust if yours differs.
# Find it with: find / -name "selisah-portfolio-site" -type d 2>/dev/null
export PROJECT_DIR="/home/$APP_USER/selisah-portfolio-site"
# If you are root and cloned into /root, instead use:
# export PROJECT_DIR="/root/selisah-portfolio-site"
```

Verify before continuing:

```bash
echo "$APP_USER"; echo "$PROJECT_DIR"; ls "$PROJECT_DIR/app/__init__.py"
```

Expected: prints your user, the project path, and the path to `__init__.py` with no "No such file" error.

---

## Task 1: Add gunicorn to requirements (local repo change)

This is the only repository change. Do it **on your local Windows machine** (where this repo is checked out), then push.

**Files:**
- Modify: `requirements.txt`

- [ ] **Step 1: Add gunicorn to `requirements.txt`**

Append this line to `requirements.txt`:

```
gunicorn==20.1.0
```

The full file should read:

```
cffi==1.15.0
click==8.0.1
cryptography==37.0.2
Flask==2.0.1
itsdangerous==2.0.1
Jinja2==3.0.1
MarkupSafe==2.0.1
peewee==3.14.10
pycparser==2.21
PyMySQL==1.0.2
python-dotenv==0.17.1
Werkzeug==2.0.1
gunicorn==20.1.0
```

- [ ] **Step 2: Commit and push**

```bash
git add requirements.txt
git commit -m "build: add gunicorn for production WSGI serving"
git push origin main
```

Expected: push succeeds to `github.com/Selisah/selisah-portfolio-site`.

---

## Task 2: Connect to the Droplet and sync code

**Files:** none (server operations)

- [ ] **Step 1: SSH into the Droplet**

From your local machine:

```bash
ssh root@159.89.156.117
```

(Use your actual login user if not `root`. You will be prompted for your SSH key passphrase — this is expected; type it and press Enter.)

Expected: a shell prompt on the Droplet.

- [ ] **Step 2: Set the session variables**

Run the two `export` commands and the verification from the "Conventions Used In This Plan" section above.

Expected: `ls "$PROJECT_DIR/app/__init__.py"` prints the path with no error.

- [ ] **Step 3: Pull the latest code (now includes gunicorn)**

```bash
cd "$PROJECT_DIR"
git pull origin main
```

Expected: output includes the `requirements.txt` change you just pushed.

---

## Task 3: Install system packages

**Files:** none (server operations)

- [ ] **Step 1: Update apt and install Python venv + nginx**

```bash
sudo apt update
sudo apt install -y python3-venv python3-pip nginx
```

Expected: packages install without error.

- [ ] **Step 2: Confirm nginx is running**

```bash
systemctl status nginx --no-pager
```

Expected: shows `active (running)`. (Visiting `http://159.89.156.117` now shows the default nginx welcome page — that gets replaced in Task 6.)

---

## Task 4: Create the Python environment

**Files:**
- Create: `$PROJECT_DIR/.venv/` (virtualenv)

- [ ] **Step 1: Create and populate the virtualenv**

```bash
cd "$PROJECT_DIR"
python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Expected: all packages install, including `gunicorn`.

- [ ] **Step 2: Confirm gunicorn is installed**

```bash
.venv/bin/gunicorn --version
```

Expected: prints `gunicorn (version 20.1.0)`.

---

## Task 5: Create the environment file and smoke-test gunicorn

**Files:**
- Create: `$PROJECT_DIR/.env`

- [ ] **Step 1: Create `.env`**

```bash
cd "$PROJECT_DIR"
echo "URL=selisah.duckdns.org" > .env
cat .env
```

Expected: prints `URL=selisah.duckdns.org`.

- [ ] **Step 2: Temporarily open port 8000 for the smoke test (only if ufw is active)**

```bash
sudo ufw status | grep -q "Status: active" && sudo ufw allow 8000/tcp || echo "ufw inactive, skip"
```

- [ ] **Step 3: Run gunicorn manually on a TCP port**

```bash
cd "$PROJECT_DIR"
.venv/bin/gunicorn --workers 3 --bind 0.0.0.0:8000 app:app
```

Expected: logs show `Listening at: http://0.0.0.0:8000` and worker boot lines.

- [ ] **Step 4: Verify it responds**

In a browser visit `http://159.89.156.117:8000` (or from another terminal: `curl -I http://159.89.156.117:8000`).

Expected: HTTP 200 and the portfolio home page HTML.

- [ ] **Step 5: Stop the manual gunicorn and close the temp port**

Press `Ctrl+C` to stop gunicorn, then:

```bash
sudo ufw status | grep -q "Status: active" && sudo ufw delete allow 8000/tcp || echo "ufw inactive, skip"
```

---

## Task 6: Create the systemd service for gunicorn

**Files:**
- Create: `/etc/systemd/system/selisah.service`

- [ ] **Step 1: Generate the service file using your session variables**

This `cat`/heredoc expands `$APP_USER` and `$PROJECT_DIR` into the file so the paths are correct for your machine:

```bash
sudo tee /etc/systemd/system/selisah.service > /dev/null <<EOF
[Unit]
Description=Gunicorn instance to serve selisah portfolio
After=network.target

[Service]
User=$APP_USER
Group=www-data
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/.venv/bin"
ExecStart=$PROJECT_DIR/.venv/bin/gunicorn --workers 3 --bind unix:$PROJECT_DIR/selisah.sock -m 007 app:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF
```

- [ ] **Step 2: Inspect the generated file**

```bash
cat /etc/systemd/system/selisah.service
```

Expected: `User=`, `WorkingDirectory=`, `Environment=`, and `ExecStart=` all show your real absolute paths (no literal `$PROJECT_DIR` text remaining).

- [ ] **Step 3: Enable and start the service**

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now selisah
```

- [ ] **Step 4: Verify the service is running and the socket exists**

```bash
systemctl status selisah --no-pager
ls -l "$PROJECT_DIR/selisah.sock"
```

Expected: status shows `active (running)`; the socket file is listed.

- [ ] **Step 5: Verify gunicorn responds over the socket (independent of nginx)**

```bash
curl --unix-socket "$PROJECT_DIR/selisah.sock" http://localhost/ | head -n 20
```

Expected: HTML of the portfolio home page.

---

## Task 7: Configure nginx as a reverse proxy

**Files:**
- Create: `/etc/nginx/sites-available/selisah`
- Modify: `/etc/nginx/sites-enabled/` (symlink + remove default)

- [ ] **Step 1: Generate the nginx site config**

```bash
sudo tee /etc/nginx/sites-available/selisah > /dev/null <<EOF
server {
    listen 80;
    server_name selisah.duckdns.org 159.89.156.117;

    location /static/ {
        alias $PROJECT_DIR/app/static/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:$PROJECT_DIR/selisah.sock;
    }
}
EOF
```

- [ ] **Step 2: Inspect the generated config**

```bash
cat /etc/nginx/sites-available/selisah
```

Expected: `alias` and `proxy_pass` show your real absolute project path (no literal `$PROJECT_DIR`).

- [ ] **Step 3: Enable the site and disable the default**

```bash
sudo ln -sf /etc/nginx/sites-available/selisah /etc/nginx/sites-enabled/selisah
sudo rm -f /etc/nginx/sites-enabled/default
```

- [ ] **Step 4: Allow nginx user to reach the socket**

The service runs gunicorn as `$APP_USER` with group `www-data` and socket mode `007`, and nginx runs as `www-data`, so it already has access. Confirm nginx's user:

```bash
grep -E "^user" /etc/nginx/nginx.conf
```

Expected: `user www-data;`.

- [ ] **Step 5: Test and reload nginx**

```bash
sudo nginx -t
sudo systemctl restart nginx
```

Expected: `nginx -t` prints `syntax is ok` and `test is successful`.

---

## Task 8: Open the firewall and verify end-to-end

**Files:** none (server operations)

- [ ] **Step 1: Allow HTTP (and ensure SSH stays open) if ufw is active**

```bash
if sudo ufw status | grep -q "Status: active"; then
  sudo ufw allow OpenSSH
  sudo ufw allow 'Nginx HTTP'
  sudo ufw status
else
  echo "ufw inactive — DigitalOcean cloud firewall (if any) must allow port 80"
fi
```

Expected: rules for OpenSSH and Nginx HTTP are listed (or the inactive message).

- [ ] **Step 2: Verify the proxy by Host header (tests nginx → gunicorn)**

```bash
curl -s -H "Host: selisah.duckdns.org" http://127.0.0.1/ | head -n 20
```

Expected: portfolio home page HTML.

- [ ] **Step 3: Verify from the public domain**

In a browser, open `http://selisah.duckdns.org`.

Expected: the portfolio site loads, including CSS/images (static assets served from `/static/`).

- [ ] **Step 4: (Optional) reboot resilience test**

```bash
sudo reboot
```

Reconnect after ~30s and visit `http://selisah.duckdns.org` again.

Expected: site is up with no manual start needed (systemd + nginx auto-started).

---

## Update Workflow (for future changes)

After the initial deploy, to ship new commits:

```bash
cd "$PROJECT_DIR"
git pull origin main
# only if dependencies changed:
. .venv/bin/activate && pip install -r requirements.txt
sudo systemctl restart selisah
```

---

## Troubleshooting Reference

- **502 Bad Gateway in browser:** gunicorn isn't running or socket perms wrong.
  Check `systemctl status selisah` and `sudo journalctl -u selisah -n 50`.
- **403/permission denied on socket:** ensure the systemd `Group=www-data` and
  `-m 007` are present, then `sudo systemctl restart selisah && sudo systemctl restart nginx`.
- **Static files 404:** confirm the `alias` path ends with a trailing slash and
  points to `$PROJECT_DIR/app/static/`.
- **Domain not resolving:** confirm the DuckDNS A record still points to
  `159.89.156.117`.

---

## Future Work (separate effort)

Add HTTPS once HTTP is confirmed working:

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d selisah.duckdns.org
```

Certbot edits the nginx config to add TLS and an HTTP→HTTPS redirect.
