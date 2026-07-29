# Truemailer — Email Validation API

**Developer:** Ashish Naik  
**Version:** v1.0.0 (Final Release)  
**Deployment:** Render + Cloudflare Workers

---

## 🌐 Live Demo

👉 **https://ashishnaikbackup.github.io/truemailer-web/**

Validate email addresses instantly using the web interface.

---

## 🚀 API

**Base URL**

```
https://truemailer-api.onrender.com
```

### Verify Email

**Endpoint**

```
POST /verify
```

**Full URL**

```
https://truemailer-api.onrender.com/verify
```

**Headers**

```
Content-Type: application/json
```

**Request Body**

```json
{
  "email": "user@example.com"
}
```

---

## 📥 cURL Example

```bash
curl -X POST https://truemailer-api.onrender.com/verify \
-H "Content-Type: application/json" \
-d "{\"email\":\"user@example.com\"}"
```

---

## 📤 Example Response

```json
{
  "email": "user@example.com",
  "valid": true,
  "mx": true,
  "disposable": false,
  "score": 98
}
```

---

## ✨ Features

- ✅ Email syntax validation
- ✅ MX record verification
- ✅ Disposable email detection
- ✅ Confidence score
- ✅ Fast REST API
- ✅ JSON responses
- ✅ CORS enabled
- ✅ Free web interface

---

## 🛠️ Tech Stack

- Node.js
- Express.js
- Cloudflare Workers
- Render
- HTML
- CSS
- JavaScript

---

## 📁 Project Structure

```
truemailer/
├── api/
├── public/
├── worker/
├── package.json
└── README.md
```

---

## 📄 License

MIT License

---

## 👨‍💻 Developer

**Ashish Naik**

GitHub: https://github.com/ashishnaikbackup

Live Demo: https://ashishnaikbackup.github.io/truemailer-web/
