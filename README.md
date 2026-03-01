# 🔐 AuthSystem — Secure Authentication Platform

> A production-ready, Google-themed authentication system built with Python Flask.  
> Complete user lifecycle management with OTP email verification, two-factor authentication, auto-logout, and a full activity dashboard — all powered by lightweight CSV storage.

---

## 🌟 Overview

**AuthSystem** is a full-featured authentication platform designed for developers who need a clean, professional, and secure login system without the complexity of a heavy framework or database setup. Inspired by Google's design language, it delivers a polished user experience from first sign-up to dashboard — with every action logged and every credential protected.

---

## ✨ Features

| Feature | Description |
|---|---|
| 📝 **Sign Up** | Full registration with first/last name, email, password, date of birth, visual CAPTCHA, and terms agreement |
| 📧 **Email OTP Verification** | 6-digit code sent via Gmail to verify new accounts with a 60-second resend timer |
| 🔐 **Secure Sign In** | Email + password authentication with optional two-factor OTP at every login |
| 🛡️ **Two-Factor Authentication** | Toggle 2FA on/off per account from the Settings panel |
| 🔑 **Forgot Password** | Identity verified via email + date of birth → temporary password + secure reset link sent to inbox |
| ⏱️ **Auto Logout** | Configurable inactivity timer (1–60 min, or off) with a 30-second warning modal |
| 📊 **Activity Dashboard** | Live stats, recent activity feed, full logs table, and account overview |
| 🤖 **AI Assistant** | Built-in chat assistant for account help and navigation guidance |
| 📬 **Professional Emails** | Google-styled HTML emails for OTP and password reset |
| 📁 **CSV Storage** | Zero database setup — all data stored locally in clean CSV files |
| 🔒 **Secure Passwords** | SHA-256 hashed, never stored in plain text |
| 📋 **Full Audit Logs** | Every login, OTP attempt, reset, and settings change logged with timestamp and IP |

---

## 📁 Project Structure
```
auth_system/
├── app.py                        ← Main Flask app (routes, email, CSV logic)
├── requirements.txt              ← Python dependencies
├── .env                          ← 🔒 Your credentials (gitignored)
├── .env.example                  ← Template for credentials
├── .gitignore                    ← Protects secrets and data
│
├── data/                         ← Auto-created on first run (gitignored)
│   ├── users.csv
│   ├── logs.csv
│   ├── otps.csv
│   └── tokens.csv
│
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── signup.html
│   ├── otp.html
│   ├── forgot_password.html
│   ├── reset_password.html
│   ├── dashboard.html
│   └── email/
│       ├── otp_email.html
│       └── reset_email.html
│
└── static/
    ├── css/
    │   ├── style.css
    │   ├── auth.css
    │   └── dashboard.css
    └── js/
        ├── auth.js
        ├── otp.js
        ├── signup.js
        └── dashboard.js
```

---

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/faizandev1/Fask-auth-system.git
cd Fask-auth-system
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure your credentials
```bash
cp .env.example .env
```
Open `.env` and fill in your details:
```env
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=xxxx xxxx xxxx xxxx
SECRET_KEY=your-random-secret-key
```

> **Get a Gmail App Password:**  
> [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) → Generate → paste into `.env`

### 4. Run the app
```bash
python app.py
```

### 5. Open in browser
```
http://localhost:5000
```

No database. No migrations. Just run and go.

---

## ⚙️ Environment Variables

| Variable | Description |
|---|---|
| `EMAIL_ADDRESS` | Gmail address used to send emails |
| `EMAIL_PASSWORD` | Gmail App Password (16-char key) |
| `SECRET_KEY` | Flask session secret — use a long random string |

---

## 🔒 Security Notes

- Passwords are **SHA-256 hashed** — never stored in plain text
- OTP codes **expire in 10 minutes**
- Reset tokens **expire in 1 hour** and are single-use
- `.env` and `data/*.csv` are fully **excluded from Git**
- CAPTCHA on signup prevents bot registrations

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.9+ · Flask 3.x |
| Frontend | HTML5 · CSS3 · Vanilla JavaScript |
| Fonts | DM Sans · DM Serif Display |
| Email | SMTP via Gmail |
| Storage | CSV files |
| Config | python-dotenv |

---

## 📜 License

MIT License — free to use, modify, and distribute.

---

<p align="center">Built with using Python & Flask</p>
