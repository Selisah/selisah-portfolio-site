# DigitalOcean Droplet Deployment Design

## Overview

Deploy the Flask portfolio site (`selisah-portfolio-site`) to an existing
DigitalOcean Ubuntu Droplet so it is reachable over HTTP at
`http://selisah.duckdns.org`. The deployment replaces the development-only
`flask run` with a production stack and makes the app resilient to crashes and
server reboots.

## Current State

- **Droplet:** already provisioned and running. Public IP `159.89.156.117`.
- **DNS:** `selisah.duckdns.org` (DuckDNS) already points an A record at
  `159.89.156.117`.
- **Code:** the GitHub repo
  (`https://github.com/Selisah/selisah-portfolio-site.git`) is already cloned
  onto the Droplet.
- **App:** a Flask package `app` whose `app/__init__.py` creates
  `app = Flask(__name__)` and defines the `/` route. WSGI entry point is
  therefore `app:app`.
- **Dependencies:** `requirements.txt` lists Flask and friends but **no
  production WSGI server** (no gunicorn) and there is no `Procfile`/`Dockerfile`.
- **Config:** the app reads a `URL` variable via `python-dotenv` from a `.env`
  file. `.env` is git-ignored (correct — it is created on the server).

## Goals

- Serve the site in production via a real WSGI server instead of `flask run`.
- Keep the app running across crashes and reboots (process supervision).
- Put a reverse proxy in front so the site is reachable on port 80 and static
  files are served efficiently.
- Make future updates a simple `git pull` + service restart.
- Leave a clean path to add HTTPS later.

## Non-Goals (for now)

- HTTPS / TLS certificates (explicitly deferred; see "Future Work").
- Database setup (the live app uses no DB despite `peewee`/`PyMySQL` being
  listed).
- CI/CD automation, zero-downtime deploys, autoscaling.
- Multi-environment (staging) setup.

## Architecture

```
Browser
  │  HTTP :80
  ▼
nginx (reverse proxy)
  │  - serves /static/* directly
  │  - proxies everything else via unix socket
  ▼
Gunicorn (WSGI server, app:app)  ← supervised by systemd
  ▼
Flask application (the `app` package)
```

### Components

1. **Gunicorn** — runs the Flask app (`app:app`) with a small worker pool,
   bound to a unix domain socket rather than a TCP port (socket stays local to
   the box and is the standard nginx↔gunicorn pattern).
2. **systemd service** — supervises Gunicorn: starts it on boot, restarts it on
   failure, runs it as a non-root user inside the project virtualenv.
3. **nginx** — listens on port 80 for `server_name selisah.duckdns.org
   159.89.156.117`, proxies dynamic requests to the Gunicorn socket, and serves
   `app/static/` directly.

## Repository Changes

The only change committed to the repo:

1. **Add `gunicorn` to `requirements.txt`.** Pin a recent stable version
   compatible with the existing Werkzeug/Flask 2.0.1 pins. This is required —
   without it there is no production server to run.

Server-only artifacts (NOT committed):

- `.env` file on the Droplet containing `URL=selisah.duckdns.org`.
- systemd unit file at `/etc/systemd/system/selisah.service`.
- nginx site config at `/etc/nginx/sites-available/selisah`.

> Note: systemd/nginx config could optionally be stored in the repo under a
> `deploy/` folder for reference, but the design keeps them server-side to avoid
> implying they are auto-applied. This can be revisited if desired.

## Deployment Procedure (server-side)

Assumes SSH access to the Droplet and that the repo is cloned at a known path
(e.g. `/home/<user>/selisah-portfolio-site`).

1. **Sync the repo & add gunicorn**
   - `git pull` the latest (which now includes gunicorn in `requirements.txt`).
2. **System packages**
   - `sudo apt update`
   - `sudo apt install -y python3-venv python3-pip nginx`
3. **Python environment**
   - Create venv in the project dir: `python3 -m venv .venv`
   - `. .venv/bin/activate && pip install -r requirements.txt`
4. **Environment file**
   - Create `.env` with `URL=selisah.duckdns.org`.
5. **Smoke test gunicorn manually**
   - `.venv/bin/gunicorn --workers 3 --bind 0.0.0.0:8000 app:app`
   - Confirm `http://159.89.156.117:8000` responds, then stop it.
6. **systemd service** (`/etc/systemd/system/selisah.service`)
   - Runs `gunicorn --workers 3 --bind unix:<project>/selisah.sock app:app`
     as the project user, `WorkingDirectory` = project dir, with `Restart=always`
     and `WantedBy=multi-user.target`.
   - `sudo systemctl daemon-reload && sudo systemctl enable --now selisah`
7. **nginx site** (`/etc/nginx/sites-available/selisah`, symlinked into
   `sites-enabled`)
   - `server_name selisah.duckdns.org 159.89.156.117;`
   - `location /static/ { alias <project>/app/static/; }`
   - `location / { proxy_pass http://unix:<project>/selisah.sock; ... }`
   - Remove the default site, `sudo nginx -t`, `sudo systemctl restart nginx`.
8. **Firewall**
   - `sudo ufw allow 'Nginx HTTP'` and `sudo ufw allow OpenSSH` (if ufw active).
9. **Verify**
   - Visit `http://selisah.duckdns.org` and confirm the portfolio loads and
     static assets render.

## Update Workflow (after initial deploy)

1. `git pull` in the project dir.
2. If deps changed: `. .venv/bin/activate && pip install -r requirements.txt`.
3. `sudo systemctl restart selisah`.

## Error Handling & Resilience

- **Process crash:** systemd `Restart=always` brings Gunicorn back up.
- **Server reboot:** `enable`d service + nginx start automatically.
- **Socket/permission issues:** project user owns the socket; nginx user
  (`www-data`) is granted access via group membership or socket placement.
- **Bad nginx config:** `nginx -t` is run before every restart to avoid taking
  the site down.

## Testing & Validation

- `systemctl status selisah` shows `active (running)`.
- `curl --unix-socket <project>/selisah.sock http://localhost/` returns the page
  (verifies gunicorn independent of nginx).
- `curl -H 'Host: selisah.duckdns.org' http://159.89.156.117/` returns the page
  (verifies nginx proxy).
- Browser load of `http://selisah.duckdns.org` renders HTML + static assets.
- Reboot test (optional): `sudo reboot`, then confirm the site is up without
  manual intervention.

## Future Work

- **HTTPS:** install Certbot (`certbot --nginx`) to obtain a free Let's Encrypt
  certificate for `selisah.duckdns.org` and redirect HTTP→HTTPS.
- Optionally store `deploy/` config templates in the repo.

## Decision Summary

- **Hosting:** existing DigitalOcean Droplet (Ubuntu), not App Platform.
- **Stack:** Gunicorn (unix socket) + systemd + nginx reverse proxy.
- **WSGI entry point:** `app:app`.
- **Access:** HTTP only on port 80 at `selisah.duckdns.org` (IP `159.89.156.117`),
  HTTPS deferred.
- **Repo change:** add `gunicorn` to `requirements.txt`; all server config lives
  on the Droplet.
