# AuthSystem — Complete Authentication Platform

A professional, Google-themed authentication system built with Python Flask.

---

## 📁 Project Structure

```
auth_system/
├── app.py                    ← Main Flask backend (all routes, email, CSV logic)
├── requirements.txt          ← Python dependencies
├── data/                     ← Auto-created CSV data files
│   ├── users.csv             ← User accounts
│   ├── logs.csv              ← Activity logs
│   ├── otps.csv              ← OTP records
│   └── tokens.csv            ← Reset tokens
├── templates/
│   ├── base.html             ← Base HTML layout
│   ├── login.html            ← Sign In page
│   ├── signup.html           ← Sign Up page (with CAPTCHA)
│   ├── otp.html              ← OTP verification (6-box UI)
│   ├── forgot_password.html  ← Forgot Password
│   ├── reset_password.html   ← Reset Password
│   ├── dashboard.html        ← Main Dashboard
│   └── email/
│       ├── otp_email.html    ← Professional OTP email
│       └── reset_email.html  ← Professional reset email
└── static/
    ├── css/
    │   ├── style.css         ← Global styles
    │   ├── auth.css          ← Auth page styles
    │   └── dashboard.css     ← Dashboard styles
    └── js/
        ├── auth.js           ← Password toggle, alerts
        ├── otp.js            ← OTP boxes, countdown timer
        ├── signup.js         ← CAPTCHA refresh, pw strength
        └── dashboard.js      ← Tabs, auto-logout, chat AI
```

---

## 🚀 Setup & Run

### 1. Install Python (3.9+)
Make sure Python is installed: `python --version`

### 2. Install dependencies
```bash
pip install flask
```

### 3. Run the app
```bash
cd auth_system
python app.py
```

### 4. Open in browser
```
http://localhost:5000
```

---

## ✨ Features

| Feature | Details |
|---|---|
| Sign Up | First/Last name, Email, Password, DOB, CAPTCHA, Terms |
| Email OTP | 6-digit code sent via Gmail to verify account |
| Sign In | Email + Password + optional 2FA OTP |
| Two-Factor Auth | Toggle on/off in Settings |
| Forgot Password | Email + DOB verification → reset link + temp password |
| Auto Logout | Configurable inactivity timer (1–60 min or Off) |
| Dashboard | Home stats, Ask AI, Activity Logs, Settings |
| CSV Logging | All actions logged to data/logs.csv |
| Professional Emails | Google-style HTML emails for OTP and reset |

---

## ⚙️ Configuration

Email credentials are in `app.py`:
```python
EMAIL_ADDRESS = 'lanser2676@gmail.com'
EMAIL_PASSWORD = 'qfwl duhk zwyw lgxe'
```

To change the secret key (recommended for production):
```python
app.secret_key = 'your-new-secret-key'
```

---

## 📊 CSV Data Files

All data is stored in `data/` as CSV:

- **users.csv** — id, first_name, last_name, email, password_hash, dob, created_at, is_verified, two_fa_enabled, auto_logout_minutes
- **logs.csv** — timestamp, email, action, ip, status, details
- **otps.csv** — email, otp, created_at, expires_at, used
- **tokens.csv** — token, email, type, created_at, expires_at, used
