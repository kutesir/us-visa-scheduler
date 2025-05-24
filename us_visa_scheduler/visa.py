import time
import json
import random
import requests
import configparser
import logging
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as Wait
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from embassy import *

config = configparser.ConfigParser()
config.read('config.ini')

# Personal Info
USERNAME = config['PERSONAL_INFO']['USERNAME']
PASSWORD = config['PERSONAL_INFO']['PASSWORD']
SCHEDULE_ID = config['PERSONAL_INFO']['SCHEDULE_ID']
PRIOD_START = config['PERSONAL_INFO']['PRIOD_START']
PRIOD_END = config['PERSONAL_INFO']['PRIOD_END']
YOUR_EMBASSY = config['PERSONAL_INFO']['YOUR_EMBASSY']
EMBASSY = Embassies[YOUR_EMBASSY][0]
FACILITY_ID = Embassies[YOUR_EMBASSY][1]
REGEX_CONTINUE = Embassies[YOUR_EMBASSY][2]

# Notification
SENDGRID_API_KEY = config['NOTIFICATION']['SENDGRID_API_KEY']
PUSHOVER_TOKEN = config['NOTIFICATION']['PUSHOVER_TOKEN']
PUSHOVER_USER = config['NOTIFICATION']['PUSHOVER_USER']
PERSONAL_SITE_USER = config['NOTIFICATION']['PERSONAL_SITE_USER']
PERSONAL_SITE_PASS = config['NOTIFICATION']['PERSONAL_SITE_PASS']
PUSH_TARGET_EMAIL = config['NOTIFICATION']['PUSH_TARGET_EMAIL']
PERSONAL_PUSHER_URL = config['NOTIFICATION']['PERSONAL_PUSHER_URL']

# Time Settings
SECONDS_IN_MINUTE = 60
SECONDS_IN_HOUR = 60 * SECONDS_IN_MINUTE
STEP_TIME = 0.5
RETRY_TIME_L_BOUND = config['TIME'].getfloat('RETRY_TIME_L_BOUND')
RETRY_TIME_U_BOUND = config['TIME'].getfloat('RETRY_TIME_U_BOUND')
WORK_LIMIT_TIME = config['TIME'].getfloat('WORK_LIMIT_TIME')
WORK_COOLDOWN_TIME = config['TIME'].getfloat('WORK_COOLDOWN_TIME')
BAN_COOLDOWN_TIME = config['TIME'].getfloat('BAN_COOLDOWN_TIME')

# ChromeDriver Settings
LOCAL_USE = config['CHROMEDRIVER'].getboolean('LOCAL_USE')
HUB_ADDRESS = config['CHROMEDRIVER']['HUB_ADDRESS']

# URLs
SIGN_IN_LINK = f"https://ais.usvisa-info.com/{EMBASSY}/niv/users/sign_in"
APPOINTMENT_URL = f"https://ais.usvisa-info.com/{EMBASSY}/niv/schedule/{SCHEDULE_ID}/appointment"
DATE_URL = f"https://ais.usvisa-info.com/{EMBASSY}/niv/schedule/{SCHEDULE_ID}/appointment/days/{FACILITY_ID}.json?appointments[expedite]=false"
TIME_URL = f"https://ais.usvisa-info.com/{EMBASSY}/niv/schedule/{SCHEDULE_ID}/appointment/times/{FACILITY_ID}.json?date=%s&appointments[expedite]=false"
SIGN_OUT_LINK = f"https://ais.usvisa-info.com/{EMBASSY}/niv/users/sign_out"

JS_SCRIPT = ("var req = new XMLHttpRequest();"
             f"req.open('GET', '%s', false);"
             "req.setRequestHeader('Accept', 'application/json, text/javascript, */*; q=0.01');"
             "req.setRequestHeader('X-Requested-With', 'XMLHttpRequest');"
             f"req.setRequestHeader('Cookie', '_yatri_session=%s');"
             "req.send(null);"
             "return req.responseText;")

def auto_action(label, find_by, el_type, action, value, sleep_time=0):
    match find_by.lower():
        case 'id':
            item = driver.find_element(By.ID, el_type)
        case 'name':
            item = driver.find_element(By.NAME, el_type)
        case 'class':
            item = driver.find_element(By.CLASS_NAME, el_type)
        case 'xpath':
            item = driver.find_element(By.XPATH, el_type)
        case _:
            return 0
    match action.lower():
        case 'send':
            item.send_keys(value)
        case 'click':
            item.click()
        case _:
            return 0
    logging.info(f"\t{label}:\t\tCheck!")
    if sleep_time:
        time.sleep(sleep_time)

def browser_login():
    driver.get(SIGN_IN_LINK)
    time.sleep(STEP_TIME)
    Wait(driver, 60).until(EC.presence_of_element_located((By.NAME, "commit")))
    auto_action("Click bounce", "xpath", '//a[@class="down-arrow bounce"]', "click", "", STEP_TIME)
    auto_action("Email", "id", "user_email", "send", USERNAME, STEP_TIME)
    auto_action("Password", "id", "user_password", "send", PASSWORD, STEP_TIME)
    auto_action("Privacy", "class", "icheckbox", "click", "", STEP_TIME)
    auto_action("Enter Panel", "name", "commit", "click", "", STEP_TIME)
    Wait(driver, 60).until(EC.presence_of_element_located(
        (By.XPATH, "//a[contains(text(), '" + REGEX_CONTINUE + "')]")))
    logging.info("login successful!\n")

def browser_get_date():
    session = driver.get_cookie("_yatri_session")["value"]
    script = JS_SCRIPT % (DATE_URL, session)
    content = driver.execute_script(script)
    return json.loads(content)

def browser_get_time(date):
    time_url = TIME_URL % date
    session = driver.get_cookie("_yatri_session")["value"]
    script = JS_SCRIPT % (time_url, session)
    logging.info("browser_get_time")
    logging.info(script)
    content = driver.execute_script(script)
    data = json.loads(content)
    time = data.get("available_times")[-1]
    logging.info(f"Got time successfully! {date} {time}")
    return time

def browser_reschedule(date):
    time = browser_get_time(date)
    driver.get(APPOINTMENT_URL)

    headers = {
        "User-Agent": driver.execute_script("return navigator.userAgent;"),
        "Referer": APPOINTMENT_URL,
        "Cookie": "_yatri_session=" + driver.get_cookie("_yatri_session")["value"]
    }

    data = {
        "authenticity_token": driver.find_element(by=By.NAME, value='authenticity_token').get_attribute('value'),
        "confirmed_limit_message": driver.find_element(by=By.NAME, value='confirmed_limit_message').get_attribute('value'),
        "use_consulate_appointment_capacity": driver.find_element(by=By.NAME, value='use_consulate_appointment_capacity').get_attribute('value'),
        "appointments[consulate_appointment][facility_id]": FACILITY_ID,
        "appointments[consulate_appointment][date]": date,
        "appointments[consulate_appointment][time]": time,
    }

    r = requests.post(APPOINTMENT_URL, headers=headers, data=data)
    if 'Successfully Scheduled' in r.text:
        return "SUCCESS", f"Rescheduled Successfully! {date} {time}"
    else:
        return "FAIL", f"Reschedule Failed!!! {date} {time}"

def get_better_date(dates):
    def is_in_period(date, PSD, PED):
        new_date = datetime.strptime(date, "%Y-%m-%d")
        return PSD < new_date < PED

    PED = datetime.strptime(PRIOD_END, "%Y-%m-%d")
    PSD = datetime.strptime(PRIOD_START, "%Y-%m-%d")

    for d in dates:
        if is_in_period(d.get('date'), PSD, PED):
            return d.get('date')
    return None

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("log.txt"),
        ]
    )

    chrome_options = Options()
    chrome_options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

    if LOCAL_USE:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
    else:
        driver = webdriver.Remote(
            command_executor=HUB_ADDRESS,
            options=chrome_options
        )

    logging.info("========= Program Started =========")

    final_notification_title = "None"
    should_login = True
    count_request = 0
    time_session_started = 0

    while True:
        count_request += 1
        print("-" * 60 + f"\nRequest {count_request}\n")
        logging.info(f"Request {count_request}")

        try:
            if should_login:
                time_session_started = time.time()
                browser_login()
                should_login = False

            dates = browser_get_date()
            logging.info(f"Found earliest available days: {dates[:10]}")
            date = get_better_date(dates)
            logging.info(f"get_better_date(dates) = {date}")

            if not dates:
                msg = f"List is empty, probably banned. Sleeping {BAN_COOLDOWN_TIME} hours."
                print(msg)
                logging.info(msg)

                driver.get(SIGN_OUT_LINK)
                should_login = True
                time.sleep(BAN_COOLDOWN_TIME * SECONDS_IN_HOUR)
                continue

            if date:
                msg = "Found a better date. Attempting to reschedule..."
                print(msg)
                logging.info(msg)
                final_notification_title, msg = browser_reschedule(date)
                break

            msg = "No better date. Retrying..."
            print(msg)
            logging.info(msg)

            session_up_time = time.time() - time_session_started
            logging.info(f"Session uptime: {session_up_time / SECONDS_IN_MINUTE:.2f} minutes")

            if session_up_time > WORK_LIMIT_TIME * SECONDS_IN_HOUR:
                msg = f"Taking a break after {WORK_LIMIT_TIME} hours"
                print(msg)
                logging.info(msg)

                driver.get(SIGN_OUT_LINK)
                should_login = True
                time.sleep(WORK_COOLDOWN_TIME * SECONDS_IN_HOUR)
            else:
                sleep_duration = random.randint(int(RETRY_TIME_L_BOUND), int(RETRY_TIME_U_BOUND))
                msg = f"Wait {sleep_duration / SECONDS_IN_MINUTE:.2f} minutes before next check"
                print(msg)
                logging.info(msg)
                time.sleep(sleep_duration)

        except Exception as e:
            final_notification_title = "ERROR"
            msg = "Exception occurred! Program will exit.\n" + str(e)
            logging.error(e)
            break

    print(final_notification_title, msg)
    logging.info((final_notification_title, msg))

    logging.info("Closing browser...")
    driver.get(SIGN_OUT_LINK)
    driver.quit()
