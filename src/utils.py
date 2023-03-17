import os
import asyncio
import base64
from pathlib import Path
from pyppeteer import launch
from mako.lookup import TemplateLookup
from telegram import Bot, File
from database.models import TimeSheet
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
DEVELOPMENT_MODE = os.getenv("DEVELOPMENT_MODE", "False") == "True"


def get_base64_string(html: str):
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

    return asyncio.get_event_loop().run_until_complete(main())


def make_html(timesheet: TimeSheet, write_to_file: bool = False):
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
    base_64_str = get_base64_string(html)
    return base_64_str
