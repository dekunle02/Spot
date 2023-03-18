import os
import asyncio
import traceback
import html
import json
from datetime import datetime, timedelta

from telegram import Update, ParseMode, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)
from database import fire, models
import utils
import constants
from dotenv import load_dotenv

load_dotenv

DEVELOPMENT_MODE = os.getenv("DEVELOPMENT_MODE", "False") == "True"
if DEVELOPMENT_MODE:
    TELEGRAM_TOKEN = os.getenv("TEST_TELEGRAM_TOKEN")
else:
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
MY_TELEGRAM_ID = os.getenv("MY_TELEGRAM_ID")

CONVERSATION_TIMEOUT = 180


# main handlers
def help_handler(update: Update, context: CallbackContext):
    update.message.reply_text(text=constants.HELP_MESSAGE, parse_mode=ParseMode.HTML)


def general_handler(update: Update, context: CallbackContext) -> int:
    user = fire.get_user_with_id(update.message.from_user.id)
    if user != None:
        update.message.reply_text(f"Hello {user.first_name} " + constants.IDLE_MESSAGE)
    else:
        update.message.reply_text(constants.WELCOME_MESSAGE)


def info_handler(update: Update, context: CallbackContext):
    user = fire.get_user_with_id(update.message.from_user.id)
    if user:
        reply = f"Here you go\n\nFirst name: <b>{user.first_name}</b>\nLast name: <b>{user.last_name}</b>\nHospital: <b>{user.hospital_name}</b>\n"
        update.message.reply_text(reply, parse_mode=ParseMode.HTML)
    else:
        update.message.reply_text(constants.UNKNOWN_USER_INFO_ASK)


def cancel_handler(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(constants.CANCEL_MESSAGE)
    return ConversationHandler.END


def error_handler(update: Update, context: CallbackContext) -> int:
    sender = update.message.from_user
    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__
    )
    tb_string = "".join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        f"An exception was raised while handling an update\n"
        f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
        "</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
        f"<pre>{html.escape(tb_string)}</pre>"
    )
    # Finally, send the message
    context.bot.send_message(
        chat_id=MY_TELEGRAM_ID,
        text=f"@{sender.first_name}-{sender.id}\n" + message,
        parse_mode=ParseMode.HTML,
    )
    update.message.reply_text(text=constants.ERROR_MESSAGE, parse_mode=ParseMode.HTML)
    return ConversationHandler.END


# admin handlers
def dm_handler(update: Update, context: CallbackContext):
    sender = update.message.from_user
    if str(sender.id) != str(MY_TELEGRAM_ID):
        return
    received_message = update.message.text
    if "*" not in received_message:
        context.bot.send_message(chat_id=MY_TELEGRAM_ID, text="/dm * account * message")
        return
    [command, user_id, msg] = received_message.split("*")
    context.bot.send_message(
        chat_id=(user_id.strip()), text=f"Here is a message from Samad 👇🏾\n{msg}"
    )
    context.bot.send_message(chat_id=MY_TELEGRAM_ID, text="Message delivered")


def bc_handler(update: Update, context: CallbackContext):
    sender = update.message.from_user
    if str(sender.id) != str(MY_TELEGRAM_ID):
        return
    received_message = update.message.text
    all_users = fire.get_all_users()
    if "*" not in received_message:
        context.bot.send_message(chat_id=MY_TELEGRAM_ID, text=str(len(all_users)))
        return
    [command, msg] = received_message.split("*")
    for user in all_users:
        context.bot.send_message(chat_id=user.id, text=f"Message from Samad 👇🏾\n{msg}")
    context.bot.send_message(chat_id=MY_TELEGRAM_ID, text="Messages delivered")


def sam_handler(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(constants.SAMAD_ASK)
    return constants.SAM_MESSAGE_STATE


def sam_message_handler(update: Update, context: CallbackContext) -> int:
    user = fire.get_user_with_id(update.message.from_user.id)
    message_body = update.message.text
    context.bot.send_message(
        chat_id=MY_TELEGRAM_ID,
        text=f"""**Direct Message to Samad**
{message_body}
From: {user.first_name} {user.last_name} ({user.id})
{user.hospital_name}
""",
    )
    update.message.reply_text(text=constants.SAMAD_THANKS)
    return ConversationHandler.END


# setup new user handlers
def setup_handler(update: Update, context: CallbackContext) -> int:
    user = fire.get_user_with_id(update.message.from_user.id)
    if user:
        update.message.reply_text(
            f"Hello {user.first_name} 👋🏾\n" + constants.ALREADY_SETUP_MESSAGE,
            quote=False,
        )
        return ConversationHandler.END
    update.message.reply_text(
        constants.FIRST_NAME_ASK, quote=False, parse_mode=ParseMode.HTML
    )
    return constants.FIRST_NAME_STATE


def first_name_handler(update: Update, context: CallbackContext) -> int:
    first_name = update.message.text.strip().capitalize()
    context.user_data["first_name"] = first_name
    update.message.reply_text(text=constants.LAST_NAME_ASK)
    return constants.LAST_NAME_STATE


def last_name_handler(update: Update, context: CallbackContext) -> int:
    last_name = update.message.text.strip().capitalize()
    context.user_data["last_name"] = last_name
    update.message.reply_text(
        text=constants.HOSPITAL_NAME_ASK, parse_mode=ParseMode.HTML
    )
    return constants.HOSPITAL_NAME_STATE


def hospital_name_handler(update: Update, context: CallbackContext) -> int:
    hospital_name = update.message.text.title()
    context.user_data["hospital_name"] = hospital_name
    update.message.reply_text(text=constants.SIGNATURE_ASK)
    return constants.SIGNATURE_STATE


def signature_handler(update: Update, context: CallbackContext) -> int:
    photo_file_id = update.message.photo[-1].get_file().file_id
    sender_id = update.message.from_user.id
    user = models.User(
        id=sender_id,
        first_name=context.user_data["first_name"],
        last_name=context.user_data["last_name"],
        hospital_name=context.user_data["hospital_name"],
        signature_file_id=photo_file_id,
    )
    fire.add_user(user)
    update.message.reply_text(constants.SETUP_COMPLETE_MESSAGE)
    return ConversationHandler.END


# edit user handlers
def edit_handler(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [[constants.OPTION_NO, constants.OPTION_YES]]
    update.message.reply_text(
        text=constants.EDIT_FIRST_NAME_PROMPT,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            one_time_keyboard=True,
            input_field_placeholder=f"Type {constants.OPTION_YES} or {constants.OPTION_NO}",
        ),
    )
    return constants.FIRST_NAME_EDIT_PROMPT_STATE


def edit_first_name_prompt(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [[constants.OPTION_NO, constants.OPTION_YES]]
    prompt_answer = update.message.text
    if prompt_answer == constants.OPTION_YES:
        update.message.reply_text(
            constants.EDIT_FIRST_NAME, reply_markup=ReplyKeyboardRemove()
        )
        return constants.FIRST_NAME_EDIT_STATE
    else:
        update.message.reply_text(
            text=constants.EDIT_LAST_NAME_PROMPT,
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard,
                one_time_keyboard=True,
                input_field_placeholder=f"Type {constants.OPTION_YES} or {constants.OPTION_NO}",
            ),
        )
        return constants.LAST_NAME_EDIT_PROMPT_STATE


def edit_first_name(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [[constants.OPTION_NO, constants.OPTION_YES]]
    new_first_name = update.message.text.strip().capitalize()
    context.user_data["first_name"] = new_first_name
    update.message.reply_text(
        text=constants.EDIT_LAST_NAME_PROMPT,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            one_time_keyboard=True,
            input_field_placeholder=f"Type {constants.OPTION_YES} or {constants.OPTION_NO}",
        ),
    )
    return constants.LAST_NAME_EDIT_PROMPT_STATE


def edit_last_name_prompt(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [[constants.OPTION_NO, constants.OPTION_YES]]
    prompt_answer = update.message.text
    if prompt_answer == constants.OPTION_YES:
        update.message.reply_text(
            constants.LAST_NAME_ASK, reply_markup=ReplyKeyboardRemove()
        )
        return constants.LAST_NAME_EDIT_STATE
    else:
        update.message.reply_text(
            text=constants.EDIT_HOSPITAL_NAME_PROMPT,
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard,
                one_time_keyboard=True,
                input_field_placeholder=f"Type {constants.OPTION_YES} or {constants.OPTION_NO}",
            ),
        )
        return constants.HOSPITAL_NAME_EDIT_PROMPT_STATE


def edit_last_name(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [[constants.OPTION_NO, constants.OPTION_YES]]
    new_last_name = update.message.text.strip().capitalize()
    context.user_data["last_name"] = new_last_name
    update.message.reply_text(
        text=constants.EDIT_HOSPITAL_NAME_PROMPT,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            one_time_keyboard=True,
            input_field_placeholder=f"Type {constants.OPTION_YES} or {constants.OPTION_NO}",
        ),
    )
    return constants.HOSPITAL_NAME_EDIT_PROMPT_STATE


def edit_hospital_name_prompt(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [[constants.OPTION_NO, constants.OPTION_YES]]
    prompt_answer = update.message.text
    if prompt_answer == constants.OPTION_YES:
        update.message.reply_text(
            constants.EDIT_HOSPITAL_NAME, reply_markup=ReplyKeyboardRemove()
        )
        return constants.HOSPITAL_NAME_EDIT_STATE
    else:
        update.message.reply_text(
            text=constants.EDIT_SIGNATURE_PROMPT,
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard,
                one_time_keyboard=True,
                input_field_placeholder=f"Type {constants.OPTION_YES} or {constants.OPTION_NO}",
            ),
        )
        return constants.SIGNATURE_EDIT_PROMPT_STATE


def edit_hospital_name(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [[constants.OPTION_NO, constants.OPTION_YES]]
    new_hospital_name = update.message.text.strip().title()
    context.user_data["hospital_name"] = new_hospital_name
    update.message.reply_text(
        text=constants.EDIT_SIGNATURE_PROMPT,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            one_time_keyboard=True,
            input_field_placeholder=f"Type {constants.OPTION_YES} or {constants.OPTION_NO}",
        ),
    )
    return constants.SIGNATURE_EDIT_PROMPT_STATE


def edit_signature_prompt(update: Update, context: CallbackContext) -> int:
    prompt_answer = update.message.text
    if prompt_answer == constants.OPTION_YES:
        update.message.reply_text(
            constants.EDIT_SIGNATURE, reply_markup=ReplyKeyboardRemove()
        )
        return constants.SIGNATURE_EDIT_STATE
    else:
        user = fire.get_user_with_id(update.message.from_user.id)
        cd = context.user_data
        first_name = cd.get("first_name") if cd.get("first_name") else user.first_name
        last_name = cd.get("last_name") if cd.get("last_name") else user.last_name
        hospital_name = (
            cd.get("hospital_name") if cd.get("hospital_name") else user.hospital_name
        )
        fire.update_user(
            id=update.message.from_user.id,
            first_name=first_name,
            last_name=last_name,
            hospital_name=hospital_name,
        )
        update.message.reply_text(constants.EDIT_COMPLETE)
        return ConversationHandler.END


def edit_signature(update: Update, context: CallbackContext) -> int:
    photo_file_id = update.message.photo[-1].get_file().file_id
    user = fire.get_user_with_id(update.message.from_user.id)
    cd = context.user_data
    first_name = cd.get("first_name") if cd.get("first_name") else user.first_name
    last_name = cd.get("last_name") if cd.get("last_name") else user.last_name
    hospital_name = (
        cd.get("hospital_name") if cd.get("hospital_name") else user.hospital_name
    )
    fire.update_user(
        id=update.message.from_user.id,
        first_name=first_name,
        last_name=last_name,
        hospital_name=hospital_name,
        signature_file_id=photo_file_id,
    )
    update.message.reply_text(constants.EDIT_COMPLETE)
    return ConversationHandler.END


# delete user handlers
def delete_handler(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [[constants.OPTION_NO, constants.OPTION_YES]]
    update.message.reply_text(
        text=constants.DELETE_USER_PROMPT,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            one_time_keyboard=True,
            input_field_placeholder=f"Type {constants.OPTION_YES} or {constants.OPTION_NO}",
        ),
    )
    return constants.DELETE_USER_STATE


def delete_user(update: Update, context: CallbackContext) -> int:
    prompt_answer = update.message.text
    if prompt_answer == constants.OPTION_YES:
        fire.delete_user(id=update.message.from_user.id)
        update.message.reply_text(
            constants.DELETE_USER_FINAL, reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    else:
        update.message.reply_text(
            text=constants.DELETE_USER_SKIP, reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END


# timesheet handlers
def timesheet_handler(update: Update, context: CallbackContext) -> int:
    user = fire.get_user_with_id(update.message.from_user.id)
    if not user:
        update.message.reply_text(text=constants.UNKNOWN_USER_INFO_ASK)
        return ConversationHandler.END
    update.message.reply_text(
        constants.START_DATE_ASK,
        quote=False,
        parse_mode=ParseMode.HTML,
    )
    return constants.TIMESHEET_START_DATE_STATE


def timesheet_start_date(update: Update, context: CallbackContext) -> int:
    entered_date = update.message.text
    if not utils.string_is_valid_date(entered_date):
        update.message.reply_text(text=constants.DATE_ERROR, parse_mode=ParseMode.HTML)
        return
    context.user_data["start_date"] = entered_date
    update.message.reply_text(
        constants.TIME_ASK, quote=False, parse_mode=ParseMode.HTML
    )
    return constants.TIMESHEET_START_TIME_STATE


def timesheet_start_time(update: Update, context: CallbackContext) -> int:
    entered_time = update.message.text
    if not utils.string_is_valid_time(entered_time):
        update.message.reply_text(text=constants.TIME_ERROR, parse_mode=ParseMode.HTML)
        return
    context.user_data["start_time"] = entered_time
    update.message.reply_text(constants.DURATION_ASK, parse_mode=ParseMode.HTML)
    return constants.TIMESHEET_DAYS_STATE


def timesheet_days(update: Update, context: CallbackContext) -> int:
    try:
        context.user_data["day_count"] = int(update.message.text)
    except:
        update.message.reply_text(
            constants.NUMBER_INPUT_ERROR, parse_mode=ParseMode.HTML
        )
        return
    update.message.reply_text(constants.END_TIME_ASK, parse_mode=ParseMode.HTML)
    return constants.TIMESHEET_END_TIME_STATE


def timesheet_end_time(update: Update, context: CallbackContext) -> int:
    entered_end_time = update.message.text
    if not utils.string_is_valid_time(entered_end_time):
        update.message.reply_text(text=constants.TIME_ERROR)
        return
    end_hour, end_minute = entered_end_time.split(":")
    entered_start_date = context.user_data["start_date"]
    entered_start_time = context.user_data["start_time"]
    day_count = context.user_data["day_count"]

    user: models.User = fire.get_user_with_id(update.message.from_user.id)
    start_time: datetime = utils.convert_string_into_date(
        date_string=entered_start_date, time_string=entered_start_time
    )
    end_time: datetime = start_time.replace(
        hour=int(end_hour), minute=int(end_minute)
    ) + timedelta(days=int(day_count))
    timesheet = models.TimeSheet(user=user, shift_start=start_time, shift_end=end_time)

    context.user_data["timesheet"] = timesheet

    reply_keyboard = [[constants.OPTION_NO, constants.OPTION_YES]]
    update.message.reply_text(
        text=constants.DISTURBANCE_ASK,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            one_time_keyboard=True,
            input_field_placeholder=f"Type {constants.OPTION_YES} or {constants.OPTION_NO}",
        ),
    )
    return constants.NIGHT_PROMPT_STATE


def night_prompt(update: Update, context: CallbackContext) -> int:
    prompt_answer = update.message.text

    if prompt_answer == constants.OPTION_NO:
        sender = update.message.from_user
        update.message.reply_text(text=constants.TIMESHEET_AWAITING_MESSAGE)
        timesheet: models.TimeSheet = context.user_data["timesheet"]
        photo_string = utils.make_timesheet_photo(timesheet)
        context.bot.send_photo(chat_id=update.message.from_user.id, photo=photo_string)
        update.message.reply_text(
            text=constants.TIMESHEET_MESSAGE, reply_markup=ReplyKeyboardRemove()
        )
        user = fire.get_user_with_id(update.message.from_user.id)
        context.bot.send_message(
            chat_id=MY_TELEGRAM_ID,
            text=f"{user.first_name}({sender.id}) made a timesheet!",
        )
        return ConversationHandler.END

    update.message.reply_text(
        constants.DISTURBANCE_DAY_ASK,
        reply_markup=ReplyKeyboardRemove(),
        parse_mode=ParseMode.HTML,
    )
    return constants.NIGHT_DAY_STATE


def night_day(update: Update, context: CallbackContext) -> int:
    try:
        context.user_data["disturbance_day"] = int(update.message.text)
    except:
        update.message.reply_text(constants.NUMBER_INPUT_ERROR)
        return
    update.message.reply_text(
        constants.DISTURBANCE_TIME_ASK,
        reply_markup=ReplyKeyboardRemove(),
        parse_mode=ParseMode.HTML,
    )
    return constants.NIGHT_TIME_STATE


def night_time(update: Update, context: CallbackContext) -> int:
    entered_time = update.message.text
    if not utils.string_is_valid_time(entered_time):
        update.message.reply_text(text=constants.TIME_ERROR)
        return
    context.user_data["disturbance_time"] = update.message.text
    update.message.reply_text(
        constants.DISTURBANCE_DURATION_ASK, parse_mode=ParseMode.HTML
    )
    return constants.NIGHT_DURATION_STATE


def night_duration(update: Update, context: CallbackContext) -> int:
    context.user_data["disturbance_duration"] = update.message.text.strip()
    update.message.reply_text(
        constants.DISTURBANCE_REASON_ASK, parse_mode=ParseMode.HTML
    )
    return constants.NIGHT_REASON_STATE


def night_reason(update: Update, context: CallbackContext) -> int:
    reason = update.message.text.strip()
    timesheet: models.TimeSheet = context.user_data["timesheet"]
    duration = context.user_data["disturbance_duration"]
    hour, min = context.user_data["disturbance_time"].split(":")
    time = timesheet.shift_start.replace(hour=int(hour), minute=int(min)) + timedelta(
        days=int(context.user_data["disturbance_day"])
    )
    night_disturbance = models.NightDisturbance(
        time=time, duration=duration, reason=reason
    )
    timesheet.append_nightDisturbance(night_disturbance)
    context.user_data["timesheet"] = timesheet

    reply_keyboard = [[constants.OPTION_NO, constants.OPTION_YES]]
    update.message.reply_text(
        text=constants.DISTURBANCE_ASK_ANOTHER,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            one_time_keyboard=True,
            input_field_placeholder=f"Type {constants.OPTION_YES} or {constants.OPTION_NO}",
        ),
    )
    return constants.NIGHT_PROMPT_STATE


def run_bot():
    print("Bot running...")
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # main handlers
    dispatcher.add_handler(CommandHandler(constants.HELP_COMMAND, help_handler))
    dispatcher.add_handler(CommandHandler(constants.INFO_COMMAND, info_handler))
    dispatcher.add_handler(CommandHandler(constants.CANCEL_COMMAND, cancel_handler))

    # admin handlers
    dispatcher.add_handler(CommandHandler(constants.DM_COMMAND, dm_handler))
    dispatcher.add_handler(CommandHandler(constants.BC_COMMAND, bc_handler))

    sam_conversation_handler = ConversationHandler(
        entry_points=[CommandHandler(constants.SAM_COMMAND, sam_handler)],
        states={
            constants.SAM_MESSAGE_STATE: [
                MessageHandler(Filters.text, sam_message_handler)
            ]
        },
        fallbacks=[CommandHandler(constants.CANCEL_COMMAND, cancel_handler)],
    )
    dispatcher.add_handler(sam_conversation_handler)

    # setup new user handlers
    setup_conversation_handler = ConversationHandler(
        entry_points=[CommandHandler(constants.SETUP_COMMAND, setup_handler)],
        states={
            constants.FIRST_NAME_STATE: [
                MessageHandler(Filters.text, first_name_handler)
            ],
            constants.LAST_NAME_STATE: [
                MessageHandler(Filters.text, last_name_handler)
            ],
            constants.HOSPITAL_NAME_STATE: [
                MessageHandler(Filters.text, hospital_name_handler)
            ],
            constants.SIGNATURE_STATE: [
                MessageHandler(Filters.photo, signature_handler)
            ],
        },
        fallbacks=[
            CommandHandler(constants.CANCEL_COMMAND, cancel_handler),
        ],
        conversation_timeout=timedelta(seconds=CONVERSATION_TIMEOUT),
    )
    dispatcher.add_handler(setup_conversation_handler)

    # edit old user handlers
    edit_conversation_handler = ConversationHandler(
        entry_points=[CommandHandler(constants.EDIT_COMMAND, edit_handler)],
        states={
            constants.FIRST_NAME_EDIT_STATE: [
                MessageHandler(Filters.text, edit_first_name)
            ],
            constants.LAST_NAME_EDIT_STATE: [
                MessageHandler(Filters.text, edit_last_name)
            ],
            constants.HOSPITAL_NAME_EDIT_STATE: [
                MessageHandler(Filters.text, edit_hospital_name)
            ],
            constants.SIGNATURE_EDIT_STATE: [
                MessageHandler(Filters.photo, edit_signature)
            ],
            constants.FIRST_NAME_EDIT_PROMPT_STATE: [
                MessageHandler(
                    Filters.regex(f"^({constants.OPTION_YES}|{constants.OPTION_NO})$"),
                    edit_first_name_prompt,
                )
            ],
            constants.LAST_NAME_EDIT_PROMPT_STATE: [
                MessageHandler(
                    Filters.regex(f"^({constants.OPTION_YES}|{constants.OPTION_NO})$"),
                    edit_last_name_prompt,
                )
            ],
            constants.HOSPITAL_NAME_EDIT_PROMPT_STATE: [
                MessageHandler(
                    Filters.regex(f"^({constants.OPTION_YES}|{constants.OPTION_NO})$"),
                    edit_hospital_name_prompt,
                )
            ],
            constants.SIGNATURE_EDIT_PROMPT_STATE: [
                MessageHandler(
                    Filters.regex(f"^({constants.OPTION_YES}|{constants.OPTION_NO})$"),
                    edit_signature_prompt,
                )
            ],
        },
        fallbacks=[
            CommandHandler(constants.CANCEL_COMMAND, cancel_handler),
        ],
        conversation_timeout=timedelta(seconds=CONVERSATION_TIMEOUT),
    )
    dispatcher.add_handler(edit_conversation_handler)

    # delete user handler
    delete_conversation_handler = ConversationHandler(
        entry_points=[CommandHandler(constants.DELETE_COMMAND, delete_handler)],
        states={
            constants.DELETE_USER_STATE: [
                MessageHandler(
                    Filters.regex(f"^({constants.OPTION_YES}|{constants.OPTION_NO})$"),
                    delete_user,
                )
            ],
        },
        fallbacks=[
            CommandHandler(constants.CANCEL_COMMAND, cancel_handler),
        ],
    )
    dispatcher.add_handler(delete_conversation_handler)

    # timesheet handlers
    timesheet_conversation_handler = ConversationHandler(
        entry_points=[CommandHandler(constants.SPOT_COMMAND, timesheet_handler)],
        states={
            constants.TIMESHEET_START_DATE_STATE: [
                MessageHandler(Filters.text, timesheet_start_date)
            ],
            constants.TIMESHEET_START_TIME_STATE: [
                MessageHandler(Filters.text, timesheet_start_time)
            ],
            constants.TIMESHEET_DAYS_STATE: [
                MessageHandler(Filters.text, timesheet_days)
            ],
            constants.TIMESHEET_END_TIME_STATE: [
                MessageHandler(Filters.text, timesheet_end_time)
            ],
            constants.NIGHT_PROMPT_STATE: [
                MessageHandler(
                    Filters.regex(f"^({constants.OPTION_YES}|{constants.OPTION_NO})$"),
                    night_prompt,
                )
            ],
            constants.NIGHT_DAY_STATE: [MessageHandler(Filters.text, night_day)],
            constants.NIGHT_TIME_STATE: [MessageHandler(Filters.text, night_time)],
            constants.NIGHT_DURATION_STATE: [
                MessageHandler(Filters.text, night_duration)
            ],
            constants.NIGHT_REASON_STATE: [MessageHandler(Filters.text, night_reason)],
        },
        fallbacks=[
            CommandHandler(constants.CANCEL_COMMAND, cancel_handler),
        ],
        conversation_timeout=timedelta(seconds=CONVERSATION_TIMEOUT),
    )
    dispatcher.add_handler(timesheet_conversation_handler)

    # general handlers
    dispatcher.add_handler(
        MessageHandler(Filters.text, general_handler, run_async=True)
    )
    dispatcher.add_error_handler(error_handler)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    run_bot()
