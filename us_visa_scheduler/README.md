# visa_rescheduler

The `visa_rescheduler` is a bot for monitoring US VISA (usvisa-info.com) appointment available dates. It can automatically reschedule to the earliest date it finds on your behalf, and optionally notify you when that happens.

This enhanced version adds real-time **Telegram alerts**, improved error handling with screenshots, and support for SendGrid and Pushover.

---

## 🚀 Features
- Logs into the visa appointment system
- Searches for earlier available dates
- Automatically reschedules if a better date is found
- Sends Telegram alerts for:
  - Script start
  - Reschedule success
  - Reschedule failure
  - Exceptions or errors with screenshots
- Optional alerts via SendGrid, Pushover, or your personal push endpoint
- Logs activity to `log.txt`

---

## ✅ Prerequisites
- You must already have a US VISA appointment scheduled
- Python 3.10+ and Google Chrome installed
- Optional: a Telegram bot and chat ID, Pushover API key, or SendGrid token

---

## 🧰 Installation
```bash
# Clone the repo
https://github.com/kutesir/us-visa-scheduler.git
cd us-visa-scheduler

# Set up virtual environment
python3 -m venv env
source env/bin/activate

# Install dependencies
pip install -r requirements.txt
```
Or manually:
```bash
pip install requests==2.27.1
pip install selenium==4.2.0
pip install webdriver-manager==3.7.0
pip install sendgrid==6.9.7
```

---

## ⚙️ Configuration
Edit the `config.ini` file to match your information:
```ini
[PERSONAL_INFO]
USERNAME = your_email
PASSWORD = your_password
SCHEDULE_ID = your_schedule_id
PRIOD_START = 2025-05-27
PRIOD_END = 2025-08-15
YOUR_EMBASSY = en-ug-yer

[NOTIFICATION]
TELEGRAM_BOT_TOKEN = your_telegram_bot_token
TELEGRAM_CHAT_ID = your_telegram_chat_id
PUSHOVER_TOKEN = your_pushover_token
PUSHOVER_USER = your_pushover_user
SENDGRID_API_KEY = your_sendgrid_key
PUSH_TARGET_EMAIL = notify@example.com
PERSONAL_PUSHER_URL = https://yourapi.com/esender.php

[CHROMEDRIVER]
LOCAL_USE = True
HUB_ADDRESS = http://localhost:9515/wd/hub

[TIME]
RETRY_TIME_L_BOUND = 10
RETRY_TIME_U_BOUND = 120
WORK_LIMIT_TIME = 1.5
WORK_COOLDOWN_TIME = 2.25
BAN_COOLDOWN_TIME = 5
```

---

## ▶️ How to Run
```bash
python visa.py
```
If all dependencies are installed correctly, the script will start running. You’ll see Chrome launch and log activity in the terminal. When a new date is found, the script will reschedule and notify you.

---

## 🔔 Configure Notification
### ✅ Telegram
1. Create a bot via [@BotFather](https://t.me/BotFather)
2. Paste your token and chat ID in `config.ini`
3. The script will send you text alerts and screenshots automatically

### ✅ Pushover
1. Create a Pushover account
2. Add an app, get the API Token/User Key
3. Fill them in your `config.ini`

### ✅ Email via SendGrid
1. Create an account at [sendgrid.com](https://sendgrid.com)
2. Generate an API key
3. Fill in the `SENDGRID_API_KEY` and `PUSH_TARGET_EMAIL`

---

## 🖼 Screenshot Alerts
If a reschedule attempt fails or crashes, the script saves a screenshot and sends it to you (via Telegram if enabled):
- `reschedule_error.png`
- `fatal_exception.png`

---

## 🏛 How to Add New Embassy
If your embassy isn’t listed in `embassy.py`, you can add it manually by finding the **Facility ID** from the appointment page using browser dev tools. See the image below:
![Finding Facility id](./doc/add_embassy.png)

---

## 🛠 Troubleshooting
- ❌ **403 from GitHub**: Use a [PAT](https://github.com/settings/tokens) or switch to SSH
- ❌ **Blank screenshots**: The page may not have loaded yet; try increasing `STEP_TIME`
- ❌ **No available dates found**: Widen your `PRIOD_START` / `PRIOD_END` range

---

## 📅 Future Improvements
- Multi-account rotation
- GUI (PyQt)
- Sound alerts
- Better ban detection

---

## 🙏 Acknowledgements
Thanks to all contributors and users who provided feedback. Inspired by several visa-slot monitoring tools and enhanced with multi-channel alerting and usability improvements.

---

## 📄 License
MIT — Free to use, modify, and share. Contributions welcome.
