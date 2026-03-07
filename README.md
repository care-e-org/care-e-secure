CARE-E Secure

CARE-E Secure is a lightweight prototype web application designed to simulate a secure healthcare logistics registration system.
The project focuses on implementing security-first web development practices using a minimal stack suitable for low-resource environments.

The application is built using Python Flask with a simple HTML/CSS frontend and demonstrates practical DevSecOps principles including secure session handling, CSRF protection, Content Security Policy enforcement, and input sanitization.


---

Project Goals

This project was created as a hands-on learning lab to explore secure web application design while transitioning into Cloud Engineering, DevSecOps, and Cybersecurity.

Primary goals:

Build a secure web prototype using lightweight technologies

Implement defense-in-depth security controls

Demonstrate OWASP-aligned security practices

Maintain compatibility with low-resource hardware (4GB RAM)



---

System Architecture

The application follows a simple client-server architecture.

User Browser
     │
     ▼
Registration Form (HTML)
     │
     ▼
Flask Backend API
     │
     ▼
SQLite Database
     │
     ▼
Admin Dashboard

Components:

Frontend: HTML/CSS forms for hospital and supplier registration

Backend: Flask application handling routing, validation, and authentication

Database: SQLite for lightweight data persistence

Admin Panel: Authenticated interface to review submitted registrations



---

Security Architecture

CARE-E Secure is designed using a defense-in-depth approach aligned with OWASP web security principles.

Transport Security

HTTPS enforced via Flask-Talisman

HSTS (HTTP Strict Transport Security) enabled

Secure cookie configuration in production


Browser Security Controls

Content Security Policy (CSP) with nonce-based script execution

X-Frame-Options to prevent clickjacking

X-Content-Type-Options to prevent MIME sniffing

Strict resource whitelisting


Input Security

All form inputs validated using Flask-WTF

HTML sanitization using the nh3 library

Jinja2 automatic template escaping


Authentication & Session Management

Password hashing using Werkzeug

Session cookies configured with:

HttpOnly

SameSite=Lax

Secure (production)


Session lifetime limited to 30 minutes

Admin routes protected using Flask-Login


Abuse Protection

Rate limiting applied to authentication and registration endpoints

Request payload size limited to 1MB


Database Security

SQLAlchemy ORM prevents SQL injection

Database constraints enforce integrity

Indexed columns for efficient queries


Security Logging

Authentication attempts are logged

Failed login attempts recorded with source IP



---

Threat Model

The application is designed to mitigate common web application threats.

Potential threats considered:

Cross-Site Scripting (XSS)

Cross-Site Request Forgery (CSRF)

SQL Injection

Brute-force login attacks

Session hijacking

Automated form abuse


Mitigations implemented:

CSP enforcement

CSRF tokens on all forms

HTML sanitization

ORM-based database queries

Rate limiting

Secure session configuration



---

Tech Stack

Backend

Python

Flask

SQLAlchemy

Flask-Login

Flask-Limiter

Flask-Talisman


Security Libraries

Flask-WTF

nh3 (HTML sanitization)


Frontend

HTML

CSS

minimal JavaScript



---

Running the Project Locally

Clone the repository:

git clone https://github.com/yourusername/care-e-secure.git
cd care-e-secure

Create virtual environment:

python3 -m venv venv
source venv/bin/activate

Install dependencies:

pip install -r requirements.txt

Configure environment variables:

cp .env.example .env

Run the application:

python app.py

The server will start locally.

---

Future Improvements

Planned enhancements include:

containerization using Docker

CI security scanning (Bandit / pip-audit)

cloud deployment

monitoring and observability

role-based access control



---

License
This project is intended for educational and experimentation purposes.
