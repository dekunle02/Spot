import os
import asyncio
import base64
from datetime import datetime, timedelta
from pathlib import Path
from pyppeteer import launch
from mako.lookup import TemplateLookup
from telegram import Bot, File
from database.models import TimeSheet
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
DEVELOPMENT_MODE = os.getenv("DEVELOPMENT_MODE", "False") == "True"

from time import sleep
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

# options = webdriver.FirefoxOptions()
options = webdriver.ChromeOptions()
options.headless = True


# this method uses selenium
def _get_base64_string(html_string: str) -> str:
    html_bs64 = base64.b64encode(html_string.encode("utf-8")).decode()
    # driver = webdriver.Firefox(options=options)
    driver = webdriver.Chrome(ChromeDriverManager(), options=options)
    driver.set_window_size(1366, 900)
    driver.get("data:text/html;base64, " + html_bs64)
    sleep(1)
    photo_string = driver.get_screenshot_as_png()
    driver.quit()
    return photo_string


# This methous uses pyppeteer
def __get_base64_string(html: str):
    async def main():
        if DEVELOPMENT_MODE:
            browser = await launch(headless=True)
        else:
            browser = await launch(
                headless=True,
                executablePath="/usr/bin/chromium-browser",  # This will work on the raspberry pi
            )
        page = await browser.newPage()
        await page.setViewport({"width": 1366, "height": 900})
        await page.setContent(html)

        base64 = await page.screenshot({"encoding": "base64"})
        await browser.close()
        return base64

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    return asyncio.get_event_loop().run_until_complete(main())


def make_timesheet_photo(timesheet: TimeSheet, write_to_file: bool = False):
    TEMPLATE_DIR = Path(__file__).parents[0] / "template"
    TEMPLATE_LOOKUP = TemplateLookup(directories=[str(TEMPLATE_DIR)])
    html_template = TEMPLATE_LOOKUP.get_template("template.html")

    try:
        bot: Bot = Bot(token=TELEGRAM_TOKEN)
        signature_file: File = bot.get_file(file_id=timesheet.user.signature_file_id)
        signature_byte_array = signature_file.download_as_bytearray()
        encoded_signature = base64.b64encode(signature_byte_array)
        encoded_signature = (str(encoded_signature))[2:-1]
        encoded_signature = "data:image/png;base64, " + encoded_signature
    except:
        encoded_signature = ""

    html = html_template.render(
        user=timesheet.user,
        work_rows=timesheet.get_work_rows(),
        total_week_hours=timesheet.get_total_hours(),
        night_disturbances=timesheet.get_disturbance_rows(),
        signature_string=encoded_signature,
        signature_date=timesheet.shift_end.strftime("%d-%m-%Y"),
    )

    if write_to_file:
        print("****WRITING TO OUT.PDF IN ROOT DIR")
        with open("out.html", "w") as f:
            f.write(html)
        return
    base_64_str = _get_base64_string(html)
    return base_64_str


def string_is_valid_date(date_string: str) -> bool:
    format = "%d-%m-%Y"
    try:
        datetime.strptime(date_string, format)
        return True
    except:
        return False


def string_is_valid_time(time_string: str) -> bool:
    format = "%H:%M"
    try:
        datetime.strptime(time_string, format)
        return True
    except:
        return False


def convert_string_into_date(date_string: str, time_string: str) -> datetime:
    """Expected string->05-12-2021 04:30"""
    string_format = "%d-%m-%Y %H:%M"
    try:
        return datetime.strptime(f"{date_string} {time_string}", string_format)
    except Exception as e:
        return None


def get_end_datetime_from_with_time(
    start_date: datetime, days: int, time: str
) -> datetime:
    try:
        end_date = start_date + timedelta(days=days)
        hour, minute = time.split(":")
        end_date = end_date.replace(hour=int(hour), minute=int(minute))
        return end_date
    except:
        return None
