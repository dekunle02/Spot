from inspect import signature
import os
import re
import codecs
import base64
from dotenv import load_dotenv
from pathlib import Path
from typing import Union

from telegram import Bot, File

from Spot.database.models import TimeSheet, User, NightDisturbance

load_dotenv()
HTML_TEMPLATE_DIRECTORY = Path(__file__).parents[1]/'assets' / 'template.html'
CSS_DIRECTORY = Path(__file__).parents[1]/'assets' / 'styles.css'
TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']


def replace(template: str, **kwargs) -> str:
    """
    @desc replaces a string with key value pairs
    @example "ABCD", B=2,C=3 => A23D
    """
    for key, value in kwargs.items():
        template = template.replace(str(key), str(value))
    return template


def clean(template: str) -> str:
    """
    @desc cleans the template which uses XX(value)XX as a replacement pattern
    @example "XXsomethingXX => ""
    """
    pattern = r"(?:XX)(.*?)(?:XX)"
    while re.findall(pattern, template):
        template = re.sub(pattern, "", template)
    return template


def extract_html_string() -> Union[str, None]:
    try:
        with codecs.open(str(HTML_TEMPLATE_DIRECTORY), 'r') as f:
            return f.read()
    except:
        return


def insert_css(template: str, **kwargs) -> str:
    with codecs.open(str(CSS_DIRECTORY), 'r') as f:
        css_style = f.read()
        css_string = f"<style>\n{css_style}\n</style>"
        return replace(template=template, XXCSSXX=css_string)


def insert_biodata(template: str, user: User, **kwargs) -> str:
    return replace(
        template=template,
        XXXXFIRST_NAMEXX=user.first_name,
        XXLAST_NAMEXX=user.last_name,
        XXHOSPITALXX=user.hospital_name
    )


def insert_work_rows(template: str, timesheet: TimeSheet, **kwargs) -> str:
    work_rows = timesheet.get_work_rows()
    work_rows_string = ""
    for row in work_rows:
        row_string = f"<tr>\n" \
            f"<th scope='row'>{row['day']}</th>\n" \
            f"<td>{row['date']}</td>\n" \
            f"<td>{row['start_time']}</td>\n" \
            f"<td>{row['end_time']}</td>\n" \
            f"<td>{row['total_hours']}</td>\n" \
            f"</tr>\n"
        work_rows_string += row_string
    return replace(
        template=template,
        XXWORK_ROWSXX=work_rows_string
    )


def insert_total_hours(template: str, timesheet: TimeSheet, **kwargs) -> str:
    return replace(
        template=template,
        XXTOTAL_WEEK_HOURSXX=str(timesheet.get_total_hours())
    )


def insert_signing_date(template: str, timesheet: TimeSheet, **kwargs) -> str:
    return replace(
        template=template,
        XXSIGNATURE_DATEXX=timesheet.shift_end.strftime("%d-%m-%Y")
    )


def insert_night_disturbances(template: str, timesheet: TimeSheet, **kwargs) -> str:
    disturbance_list = timesheet.get_disturbance_rows()
    disturbance_rows_str = ""
    for dist in disturbance_list:
        dist_row = f"<tr>\n" \
            f"<td>{dist['date']}</td>\n" \
            f"<td>{dist['time']}</td>\n" \
            f"<td>{dist['duration']}</td>\n" \
            f"<td>{dist['reason']}</td>\n" \
            f"</tr>\n"
        disturbance_rows_str += dist_row

    for i in range(12 - len(disturbance_list)):
        disturbance_rows_str += f"<tr>\n" \
            f"<td></td>\n" \
            f"<td></td>\n" \
            f"<td></td>\n" \
            f"<td></td>\n" \
            f"</tr>\n"

    return replace(
        template=template,
        XXDISTURBANCE_ROWSXX=disturbance_rows_str
    )


def insert_signature(template: str, user: User, **kwargs) -> str:
    bot: Bot = Bot(token=TELEGRAM_TOKEN)
    signature_file: File = bot.get_file(file_id=user.signature_file_id)
    signature_byte_array = signature_file.download_as_bytearray()
    encoded_signature = base64.encode(signature_byte_array)
    encoded_signature = (str(encoded_signature))[2:-1]
    return replace(
        template=template,
        XXSIGNATUREXX="data:image/png;base64, " + signature_byte_array
    )


def compose_html_with_timesheet(timesheet:TimeSheet, html_string=None) -> str:
    template: str = html_string if html_string else extract_html_string()
    insertion_func_list = [insert_css, insert_biodata, insert_work_rows,
                           insert_total_hours, insert_signing_date, insert_night_disturbances, insert_signature]
    for func in insertion_func_list:
        template = func(template=template, timesheet=timesheet, user=timesheet.user)
    return template
