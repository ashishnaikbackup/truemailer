# Truemailer — Email Validation API

**Developer:** Ashish  
**Version:** Final Release  
**Deployment:** Render + Cloudflare Workers

---

## 🌍 API Base
`https://truemailer-api.onrender.com/`

---

## 📩 Verify Email
**Endpoint:** `/verify`  
**Method:** POST  
**Headers:** `Content-Type: application/json`  
**Body:**
```json
{ "email": "user@example.com" }


---

##📜 Portfolio
# Truemailer – Email Validation API

Truemailer is a lightweight email validation service built to detect
fake, disposable, and temporary email addresses commonly used to abuse
free trials and sign-up systems.

This project was built as a learning-focused SaaS-style application,
covering frontend, backend APIs, deployment, and infrastructure.

---

## Problem
Many applications face:
- Fake signups
- Disposable email abuse
- Spam users accessing free features

Truemailer addresses this by validating email authenticity before
allowing access.

---

## Solution
The API performs multiple checks:
- Email syntax validation
- Domain existence checks
- Disposable and temporary email detection
- Custom allowlist and blocklist logic
- Unified validation wrapper

---

## Tech Stack
- Frontend: HTML (GitHub Pages)
- Backend: Python
- API Hosting: Render
- Edge Routing: Cloudflare Workers
- Data Source: Open-source disposable email domain lists (GitHub)

---

## Features
- REST API for easy integration
- JSON-based requests and responses
- Free-tier friendly architecture
- Designed for scalability

---

## What I Learned
- Building and deploying a real-world API
- Using GitHub as a product backbone
- Deploying Python services on cloud platforms
- Understanding SaaS product limitations and distribution challenges

---

## Status
This project is complete and maintained as a portfolio artifact.
