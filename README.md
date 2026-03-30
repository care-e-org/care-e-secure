# CARE-E Secure

A security-first Flask prototype simulating a healthcare logistics registration system. Built as a hands-on DevSecOps lab to implement and audit real security controls — not as an afterthought, but as the primary engineering objective.

🔴 **Live:** [care-e.xyz](https://care-e.xyz)

---

## What This Is

CARE-E allows hospitals and logistics suppliers to register as partners for emergency cold-chain deliveries (blood units, vaccines, organs). The registration flow is the demo. The security architecture is the project.

Built on a 4GB RAM Debian 13 machine. Every design decision was constrained by that environment — no containers, no external services in dev, no unnecessary dependencies.

---

## Security Architecture

Designed using defense-in-depth. Each layer assumes the layer above it has already failed.

### Transport & Headers

- HTTPS enforced via Flask-Talisman with HSTS
- `X-Frame-Options`, `X-Content-Type-Options`, `X-XSS-Protection` set by default
- `force_https` activates in production, disabled in local dev

### Content Security Policy

Strict resource whitelist enforced at the browser level:

| Directive   | Allowed Sources                               |
|-------------|-----------------------------------------------|
| default-src | `'self'` only                                 |
| script-src  | `'self'` + cdn.jsdelivr.net + per-request nonce |
| style-src   | `'self'` + Google Fonts + Bootstrap CDN       |
| font-src    | `'self'` + fonts.gstatic.com + Bootstrap CDN  |
| img-src     | `'self'` + `data:` (inline SVGs only)         |

The nonce on `script-src` means injected `<script>` tags are blocked by the browser even if they reach the template.

### CSRF Protection

Flask-WTF `CSRFProtect` is enabled globally at the application factory level — not per-route. Any new route added in the future inherits protection automatically. All forms include `{{ form.hidden_tag() }}` or explicit `{{ csrf_token() }}`.

### XSS Prevention (Three Layers)

1. **nh3.clean()** — All user text sanitized before database storage using the Rust-based nh3 library (replaces deprecated bleach)
2. **Jinja2 autoescaping** — All template variables HTML-escaped on render
3. **CSP** — Blocks unauthorized script execution at the browser level

### SQL Injection Prevention

SQLAlchemy ORM used exclusively. No raw SQL anywhere in the codebase. All queries use parameterized statements internally. Pagination parameters are explicitly type-cast:

```python
request.args.get('page', 1, type=int)
```

### Authentication & Session Security

| Control          | Implementation                                            |
|------------------|-----------------------------------------------------------|
| Password storage | Werkzeug scrypt hash — never plaintext                    |
| Session cookies  | HttpOnly, SameSite=Lax, Secure (production)               |
| Session timeout  | 30 minutes absolute                                       |
| Remember-me      | Explicitly disabled — session ends on browser close       |
| Logout endpoint  | POST-only — prevents CSRF-based forced logout             |
| Route protection | `@login_required` on all admin routes                     |

### Rate Limiting

| Endpoint            | Limit              |
|---------------------|--------------------|
| /admin/login        | 5 requests/minute  |
| /register/hospital  | 10 requests/minute |
| /register/supplier  | 10 requests/minute |

### Secret Management

`SECRET_KEY` is loaded from `.env` exclusively. The application raises a `RuntimeError` on startup if the variable is missing — no hardcoded fallback, no silent degradation:

```python
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise RuntimeError("FATAL: SECRET_KEY environment variable is not set.")
```

### Additional Controls

- **Payload limit:** 1MB cap on all requests — drops oversized payloads before they reach application logic
- **Security logging:** Failed and successful admin logins recorded with username and source IP
- **DB constraints:** `nullable=False` on critical columns, `unique=True` on admin username, column-level length limits

---

## OWASP Top 10 Coverage

| Risk                      | Control                                               |
|---------------------------|-------------------------------------------------------|
| A01 Broken Access Control | `@login_required`, POST-only logout, session timeout  |
| A02 Cryptographic Failures| scrypt hashing, HTTPS, Secure cookies                 |
| A03 Injection             | SQLAlchemy ORM, nh3 sanitization                      |
| A04 Insecure Design       | Rate limiting, fail-fast SECRET_KEY, 30-min sessions  |
| A05 Security Misconfiguration | CSP, Talisman headers, no debug in production     |
| A06 Vulnerable Components | nh3 replaces deprecated bleach, pinned requirements   |
| A07 Auth Failures         | Hashed passwords, rate-limited login, security logs   |
| A08 Data Integrity        | CSRF on all forms, SameSite cookies                   |
| A09 Logging Failures      | Dedicated security logger for auth events             |
| A10 SSRF                  | No outbound HTTP calls in the application             |

---

## System Architecture

```
User Browser
     │
     ▼
Registration Form (HTML + CSRF token)
     │
     ▼
Flask Backend
     ├── Rate limit check     (Flask-Limiter)
     ├── CSRF verification    (Flask-WTF)
     ├── Field validation     (WTForms)
     ├── Input sanitization   (nh3)
     └── Parameterized write  (SQLAlchemy)
     │
     ▼
SQLite Database (instance/care_e.db, chmod 600)
     │
     ▼
Admin Dashboard (Flask-Login protected)
```

---

## Tech Stack

| Layer    | Technology                                            |
|----------|-------------------------------------------------------|
| Backend  | Python, Flask, SQLAlchemy, Flask-Login, Flask-Migrate |
| Security | Flask-WTF, Flask-Talisman, Flask-Limiter, nh3         |
| Frontend | HTML, CSS, Bootstrap 5, Jinja2                        |
| Database | SQLite (dev), PostgreSQL (production via Railway)     |
| Hosting  | Railway + GoDaddy custom domain                       |

---

## Running Locally

```bash
# Clone and enter directory
git clone https://github.com/yourusername/care-e-secure.git
cd care-e-secure

# One-step setup: creates venv, installs deps, and generates .env with SECRET_KEY
bash setup.sh

# Activate virtual environment and start the application
source venv/bin/activate && python3 run.py
```

---

## Security Audit Log

Two independent security audits were conducted during development.

**Audit 1 (mid-build):** 12 findings — 1 Critical, 2 High, 4 Medium, 5 Low.
All critical and high findings resolved before continuing development.

**Audit 2 (pre-deploy):** 7 findings — 0 Critical, 2 High, 3 Medium, 2 Low.
Remaining items are hardening improvements deferred to next iteration.

Notable fixes applied between audits:

- Replaced hardcoded `SECRET_KEY` fallback with fail-fast `RuntimeError`
- Extended nh3 sanitization from `notes` field only to all free-text inputs
- Migrated logout from GET to POST with CSRF token
- Replaced deprecated `bleach` with `nh3`
- Added explicit session cookie security flags

---

## Next Iteration

- [ ] CI pipeline with Bandit (SAST) and pip-audit (dependency scanning)
- [ ] Remove `unsafe-inline` from `style-src` CSP
- [ ] Account lockout after N failed login attempts
- [ ] Containerization with Docker for reproducible deployment
- [ ] Role-based access control for multi-admin support

---

## Context

Built in a weekend as a hands-on security lab. The goal was to apply defense-in-depth to a realistic use case and then audit the result — not to build features.

Stack chosen for a reason: runs on 4GB RAM, no containers, no external services in development. Constraints force decisions.

---

*For educational and portfolio purposes.*
