# Visa Scheduler with Telegram Alerts

This project automates the process of checking and rescheduling US visa appointments using Selenium. It includes smart retry handling, cooldowns, and Telegram bot notifications.

---

## ✅ Features

* Logs in to your [ais.usvisa-info.com](https://ais.usvisa-info.com) account
* Checks for available appointment dates
* Automatically reschedules if a better date is found
* Sends notifications via **Telegram** (and optionally SendGrid, Pushover, or custom email API)
* Retries on failure with cooldown periods

---

## 🔧 Setup Instructions

### 1. Prerequisites

* Chrome browser installed
* Python 3.8 or higher
* A Telegram bot with your chat ID
* Valid US visa appointment login credentials

### 2. Clone and Install Dependencies

```bash
pip install selenium requests webdriver-manager
```

### 3. Create `config.ini`

Fill in your credentials, target date range, embassy info, and notification settings:

```ini
[PERSONAL_INFO]
USERNAME = your_email
PASSWORD = your_password
SCHEDULE_ID = your_appointment_id
PRIOD_START = 2025-06-01
PRIOD_END = 2025-08-01
YOUR_EMBASSY = en-ug-yer

[NOTIFICATION]
TELEGRAM_BOT_TOKEN = 123456:ABC-YourBotToken
TELEGRAM_CHAT_ID = 987654321
SENDGRID_API_KEY =
PUSHOVER_TOKEN =
PUSHOVER_USER =
PERSONAL_SITE_USER =
PERSONAL_SITE_PASS =
PUSH_TARGET_EMAIL = you@example.com
PERSONAL_PUSHER_URL =

[CHROMEDRIVER]
LOCAL_USE = True
HUB_ADDRESS = http://localhost:9515/wd/hub

[TIME]
RETRY_TIME_L_BOUND = 10
RETRY_TIME_U_BOUND = 60
WORK_LIMIT_TIME = 1.5
WORK_COOLDOWN_TIME = 2
BAN_COOLDOWN_TIME = 5
```

### 4. Run the Script

```bash
python visa.py
```

Keep the terminal open. The browser will open and simulate your interactions.

---

## 📬 Telegram Alerts

You will receive alerts for:

* 🔄 Each request start
* ✅ Successful reschedule
* ❌ Reschedule failure
* ❌ Login failure or timeout
* ⚠️ Site errors or bans

To get your `TELEGRAM_CHAT_ID`, send a message to your bot and check the JSON response from:

```
https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates
```

---

## 🤖 Extendability

* Add daily summaries
* Capture screenshots on success
* Add other embassies to `embassy.py`
* Replace browser login with API (if possible)

---

## 👨‍💻 Author

Built and customized by @kutesir with real-time Telegram integration.

---

## 🛡️ Disclaimer

This tool is for educational and personal automation purposes only. Use responsibly and respect the website’s terms of service.

---
