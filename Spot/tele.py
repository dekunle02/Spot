import os, traceback, html, json
from datetime import datetime, timedelta
from socket import timeout
from dotenv import load_dotenv

from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext
)

from telegram import (
    Update,
    ParseMode,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove
    )

from database import fire, models
from controller import parser, composer
from controller.replies import Replies 

load_dotenv()
TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
MY_TELEGRAM_ID = os.environ['MY_TELEGRAM_ID']

class Options:
    YES = 'Yes'
    NO = 'No'
    MAYBE = 'Maybe'
    UNSURE = 'Unsure'


class Commands:
    SETUP = 'setup'
    EDIT = 'edit'
    INFO ='info'
    HELP = 'help'
    SPOT = 'spot'
    CANCEL = 'cancel'
    DELETE = 'delete'
    SAM = 'sam'


"""
Conversation STATES
"""
FIRST_NAME, LAST_NAME, HOSPITAL_NAME, SIGNATURE = range(0, 4)
FIRST_NAME_EDIT, FIRST_NAME_EDIT_PROMPT, LAST_NAME_EDIT, LAST_NAME_EDIT_PROMPT, HOSPITAL_NAME_EDIT, HOSPITAL_NAME_EDIT_PROMPT, SIGNATURE_EDIT, SIGNATURE_EDIT_PROMPT = range(4, 12)
START_DATE, START_TIME, NUMBER_OF_DAYS, END_TIME, NIGHT_ADD = range(12, 17)
NIGHT_DAY, NIGHT_TIME, NIGHT_DURATION, NIGHT_REASON = range(17, 21)
DELETE_USER = 21
TIMESHEET_START_DATE, TIMESHEET_START_TIME, TIMESHEET_DAYS, TIMESHEET_END_TIME = range(22,26)
NIGHT_PROMPT, NIGHT_DAY, NIGHT_TIME, NIGHT_DURATION, NIGHT_REASON = range(26,31)
SAM, SAM_MESSAGE = (31, 32)

"""
General handlers
"""
def help(update: Update, context: CallbackContext):
    update.message.reply_text(text= Replies.HELP_MESSAGE, parse_mode=ParseMode.HTML)

def error(update: Update, context: CallbackContext) -> int:
    sender = update.message.from_user
    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = ''.join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        f'An exception was raised while handling an update\n'
        f'<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}'
        '</pre>\n\n'
        f'<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n'
        f'<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n'
        f'<pre>{html.escape(tb_string)}</pre>'
    )
    # Finally, send the message
    context.bot.send_message(chat_id=MY_TELEGRAM_ID, text=f"@{sender.first_name}-{sender.id}\n"+message, parse_mode=ParseMode.HTML)
    update.message.reply_text(text=Replies.ERROR_MESSAGE, parse_mode=ParseMode.HTML)
    return ConversationHandler.END

def general(update: Update, context: CallbackContext) -> int:
    user = fire.get_user_with_id(update.message.from_user.id)
    if user != None:
        update.message.reply_text(
            f"Hello {user.first_name} " + Replies.IDLE_MESSAGE
        )
    else:
       update.message.reply_text(
            Replies.WELCOME_MESSAGE
        ) 

def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(Replies.CANCEL_MESSAGE)
    return ConversationHandler.END

def info(update:Update, context: CallbackContext):
    user = fire.get_user_with_id(update.message.from_user.id)
    if user:
        reply = f"Here you go\n\nFirst name: <b>{user.first_name}</b>\nLast name: <b>{user.last_name}</b>\nHospital: <b>{user.hospital_name}</b>\n"
        update.message.reply_text(reply, parse_mode=ParseMode.HTML)
    else:
        update.message.reply_text(
            Replies.UNKNOWN_USER_INFO_ASK
        )


def sam(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        Replies.SAMAD_ASK
    )
    return SAM_MESSAGE

def sam_message(update: Update, context: CallbackContext) -> int:
    samad_message = update.message.text
    sender = update.message.from_user
    context.bot.send_message(
        chat_id=MY_TELEGRAM_ID, 
        text=f"{samad_message} sent by @{sender.first_name} & {sender.full_name} id-{sender.id}\n")
    update.message.reply_text(text=Replies.SAMAD_THANKS)
    return ConversationHandler.END


"""
SetUp New User Flow
"""
def setup(update: Update, context: CallbackContext) -> int:
    user = fire.get_user_with_id(update.message.from_user.id)
    if user:
        update.message.reply_text(
        f"Hello {user.first_name} 👋🏾\n" + Replies.ALREADY_SETUP_MESSAGE, quote=False
        )
        return ConversationHandler.END
    update.message.reply_text(
        Replies.FIRST_NAME_ASK, quote=False, parse_mode=ParseMode.HTML
    )
    return FIRST_NAME

def first_name(update: Update, context: CallbackContext) -> int:
    first_name = update.message.text.strip().capitalize()
    context.user_data['first_name'] = first_name
    update.message.reply_text(
        text=Replies.LAST_NAME_ASK
    )
    return LAST_NAME

def last_name(update: Update, context: CallbackContext) -> int:
    last_name = update.message.text.strip().capitalize()
    context.user_data["last_name"] = last_name
    update.message.reply_text(text=Replies.HOSPITAL_NAME_ASK, parse_mode=ParseMode.HTML)
    return HOSPITAL_NAME

def hospital_name(update: Update, context: CallbackContext) -> int:
    hospital_name = parser.cap_each_word(update.message.text)
    context.user_data["hospital_name"] = hospital_name
    update.message.reply_text(text=Replies.SIGNATURE_ASK)
    return SIGNATURE

def signature(update: Update, context: CallbackContext) -> int:
    photo_file_id = update.message.photo[-1].get_file().file_id
    sender_id = update.message.from_user.id
    user = models.User(
        id=sender_id,
        first_name=context.user_data['first_name'],
        last_name=context.user_data['last_name'],
        hospital_name=context.user_data['hospital_name'],
        signature_file_id=photo_file_id
    )
    fire.add_user(user)
    update.message.reply_text(
        Replies.SETUP_COMPLETE_MESSAGE
    )
    return ConversationHandler.END



"""
Edit User Flow
"""
def edit(update:Update, context:CallbackContext) -> int:
    reply_keyboard = [[Options.NO, Options.YES]]
    update.message.reply_text(
        text=Replies.EDIT_FIRST_NAME_PROMPT,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, input_field_placeholder= f"Type {Options.YES} or {Options.NO}")
    )
    return FIRST_NAME_EDIT_PROMPT

def edit_first_name_prompt(update:Update, context:CallbackContext) -> int:
    reply_keyboard = [[Options.NO, Options.YES]]
    prompt_answer = update.message.text
    if prompt_answer == Options.YES:
        update.message.reply_text(Replies.EDIT_FIRST_NAME, reply_markup=ReplyKeyboardRemove())
        return FIRST_NAME_EDIT
    else:
        update.message.reply_text(
            text=Replies.EDIT_LAST_NAME_PROMPT,
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, input_field_placeholder= f"Type {Options.YES} or {Options.NO}")
            )
        return LAST_NAME_EDIT_PROMPT
    
def edit_first_name(update:Update, context:CallbackContext) -> int:
    reply_keyboard = [[Options.NO, Options.YES]]
    new_first_name = update.message.text.strip().capitalize()
    context.user_data['first_name'] = new_first_name
    update.message.reply_text(text=Replies.EDIT_LAST_NAME_PROMPT,
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, input_field_placeholder= f"Type {Options.YES} or {Options.NO}")
    )
    return LAST_NAME_EDIT_PROMPT

""""""
def edit_last_name_prompt(update:Update, context:CallbackContext) -> int:
    reply_keyboard = [[Options.NO, Options.YES]]
    prompt_answer = update.message.text
    if prompt_answer == Options.YES:
        update.message.reply_text(Replies.LAST_NAME_ASK, reply_markup=ReplyKeyboardRemove())
        return LAST_NAME_EDIT
    else:
        update.message.reply_text(
            text=Replies.EDIT_HOSPITAL_NAME_PROMPT,
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, input_field_placeholder= f"Type {Options.YES} or {Options.NO}")
            )
        return HOSPITAL_NAME_EDIT_PROMPT

def edit_last_name(update:Update, context:CallbackContext) -> int:
    reply_keyboard = [[Options.NO, Options.YES]]
    new_last_name = update.message.text.strip().capitalize()
    context.user_data['last_name'] = new_last_name
    update.message.reply_text(
        text=Replies.EDIT_HOSPITAL_NAME_PROMPT,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, input_field_placeholder= f"Type {Options.YES} or {Options.NO}")
        )
    return HOSPITAL_NAME_EDIT_PROMPT

""""""
def edit_hospital_name_prompt(update:Update, context:CallbackContext) -> int:
    reply_keyboard = [[Options.NO, Options.YES]]
    prompt_answer = update.message.text
    if prompt_answer == Options.YES:
        update.message.reply_text(Replies.EDIT_HOSPITAL_NAME, reply_markup=ReplyKeyboardRemove())
        return HOSPITAL_NAME_EDIT
    else:
        update.message.reply_text(
            text=Replies.EDIT_SIGNATURE_PROMPT,
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, input_field_placeholder= f"Type {Options.YES} or {Options.NO}")
            )
        return SIGNATURE_EDIT_PROMPT

def edit_hospital_name(update:Update, context:CallbackContext) -> int:
    reply_keyboard = [[Options.NO, Options.YES]]
    new_hospital_name = update.message.text.strip().capitalize()
    context.user_data['hospital_name'] = new_hospital_name
    update.message.reply_text(
        text=Replies.EDIT_SIGNATURE_PROMPT,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, input_field_placeholder= f"Type {Options.YES} or {Options.NO}")
        )
    return SIGNATURE_EDIT_PROMPT

def edit_signature_prompt(update:Update, context:CallbackContext) -> int:
    prompt_answer = update.message.text
    if prompt_answer == Options.YES:
        update.message.reply_text(Replies.EDIT_SIGNATURE, reply_markup=ReplyKeyboardRemove())
        return SIGNATURE_EDIT
    else:
        user = fire.get_user_with_id(update.message.from_user.id)
        cd = context.user_data
        first_name = cd.get('first_name') if cd.get('first_name') else user.first_name
        last_name = cd.get('last_name') if cd.get('last_name') else user.last_name
        hospital_name = cd.get('hospital_name') if cd.get('hospital_name') else user.hospital_name        
        fire.update_user(
            id=update.message.from_user.id,
            first_name=first_name,
            last_name=last_name,
            hospital_name=hospital_name)

        update.message.reply_text(Replies.EDIT_COMPLETE)
        return ConversationHandler.END

def edit_signature(update:Update, context:CallbackContext) -> int:
    photo_file_id = update.message.photo[-1].get_file().file_id
    user = fire.get_user_with_id(update.message.from_user.id)
    cd = context.user_data
    first_name = cd.get('first_name') if cd.get('first_name') else user.first_name
    last_name = cd.get('last_name') if cd.get('last_name') else user.last_name
    hospital_name = cd.get('hospital_name') if cd.get('hospital_name') else user.hospital_name       
    fire.update_user(
        id=update.message.from_user.id,
        first_name=first_name,
        last_name=last_name,
        hospital_name=hospital_name,
        signature_file_id=photo_file_id)
    update.message.reply_text(Replies.EDIT_COMPLETE)
    return ConversationHandler.END
    

"""
Delete User Flow
"""
def delete(update: Update, context: CallbackContext)->int:
    reply_keyboard = [[Options.NO, Options.YES]]
    update.message.reply_text(
        text=Replies.DELETE_USER_PROMPT,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, input_field_placeholder= f"Type {Options.YES} or {Options.NO}")
    )
    return DELETE_USER
 
def delete_user(update:Update, context:CallbackContext) -> int:
    prompt_answer = update.message.text
    if prompt_answer == Options.YES:
        fire.delete_user(id=update.message.from_user.id)
        update.message.reply_text(Replies.DELETE_USER_FINAL, reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    else:
        update.message.reply_text(text=Replies.DELETE_USER_SKIP,reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END


"""
Create Timesheet Flow
"""
def timesheet(update: Update, context: CallbackContext) -> int:
    user = fire.get_user_with_id(update.message.from_user.id)
    if not user:
        update.message.reply_text(text=Replies.UNKNOWN_USER_INFO_ASK)
        return ConversationHandler.END
    update.message.reply_text(
        Replies.START_DATE_ASK, quote=False, parse_mode=ParseMode.HTML
    )
    return TIMESHEET_START_DATE

def timesheet_start_date(update:Update, context:CallbackContext) -> int:
    entered_date = update.message.text
    if not parser.string_is_valid_date(entered_date):
        update.message.reply_text(text=Replies.DATE_ERROR, parse_mode=ParseMode.HTML)
        return
    context.user_data['start_date'] = entered_date
    update.message.reply_text(Replies.TIME_ASK, quote=False, parse_mode=ParseMode.HTML)
    return TIMESHEET_START_TIME

def timesheet_start_time(update:Update, context:CallbackContext) -> int:
    entered_time = update.message.text
    if not parser.string_is_valid_time(entered_time):
        update.message.reply_text(text=Replies.TIME_ERROR, parse_mode=ParseMode.HTML)
        return
    context.user_data['start_time'] = entered_time
    update.message.reply_text(Replies.DURATION_ASK, parse_mode=ParseMode.HTML)
    return TIMESHEET_DAYS

def timesheet_days(update:Update, context:CallbackContext) -> int:
    try:
        context.user_data['day_count'] = int(update.message.text)
    except:
        update.message.reply_text(Replies.NUMBER_INPUT_ERROR, parse_mode=ParseMode.HTML)
        return 
    update.message.reply_text(Replies.END_TIME_ASK, parse_mode=ParseMode.HTML)
    return TIMESHEET_END_TIME
    
def timesheet_end_time(update:Update, context:CallbackContext) -> int:
    entered_end_time = update.message.text
    if not parser.string_is_valid_time(entered_end_time):
        update.message.reply_text(text=Replies.TIME_ERROR)
        return
    end_hour, end_minute = entered_end_time.split(":")
    entered_start_date = context.user_data['start_date']
    entered_start_time = context.user_data['start_time']
    day_count = context.user_data['day_count']
    
    user: models.User = fire.get_user_with_id(update.message.from_user.id)
    start_time: datetime = parser.convert_string_into_date(date_string=entered_start_date, time_string=entered_start_time)
    end_time: datetime = start_time.replace(hour=int(end_hour), minute=int(end_minute)) + timedelta(days=int(day_count))
    timesheet = models.TimeSheet(user=user, shift_start=start_time, shift_end=end_time)

    context.user_data['timesheet'] = timesheet

    reply_keyboard = [[Options.NO, Options.YES]]
    update.message.reply_text(text=Replies.DISTURBANCE_ASK,
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, input_field_placeholder= f"Type {Options.YES} or {Options.NO}")
            )
    return NIGHT_PROMPT

def night_prompt(update:Update, context:CallbackContext) -> int:
    prompt_answer = update.message.text
    if prompt_answer == Options.NO:
        update.message.reply_text(text=Replies.TIMESHEET_AWAITING_MESSAGE)
        timesheet: models.TimeSheet = context.user_data['timesheet']
        photo_string = composer.get_timesheet_photo(timesheet)
        context.bot.send_photo(chat_id=update.message.from_user.id ,photo=photo_string)
        update.message.reply_text(text=Replies.TIMESHEET_MESSAGE,reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    
    update.message.reply_text(Replies.DISTURBANCE_DAY_ASK,reply_markup=ReplyKeyboardRemove(),parse_mode=ParseMode.HTML)
    return NIGHT_DAY

def night_day(update:Update, context:CallbackContext) -> int:
    try:
        context.user_data["disturbance_day"] = int(update.message.text)
    except:
        update.message.reply_text(Replies.NUMBER_INPUT_ERROR)
        return
    update.message.reply_text(Replies.DISTURBANCE_TIME_ASK, reply_markup=ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)
    return NIGHT_TIME

def night_time(update:Update, context:CallbackContext) -> int:
    entered_time = update.message.text
    if not parser.string_is_valid_time(entered_time):
        update.message.reply_text(text=Replies.TIME_ERROR)
        return
    context.user_data["disturbance_time"] = update.message.text
    update.message.reply_text(Replies.DISTURBANCE_DURATION_ASK, parse_mode=ParseMode.HTML)
    return NIGHT_DURATION

def night_duration(update:Update, context:CallbackContext) -> int:
    context.user_data["disturbance_duration"] = update.message.text.strip()
    update.message.reply_text(Replies.DISTURBANCE_REASON_ASK, parse_mode=ParseMode.HTML)

    return NIGHT_REASON

def night_reason(update:Update, context: CallbackContext) -> int:
    reason = update.message.text.strip()
    timesheet: models.TimeSheet = context.user_data['timesheet']
    duration = context.user_data['disturbance_duration']
    hour, min = context.user_data['disturbance_time'].split(":")
    time = timesheet.shift_start.replace(hour=int(hour), minute=int(min)) + timedelta(days=int(context.user_data['disturbance_day']))
    night_disturbance = models.NightDisturbance(
        time=time,
        duration=duration,
        reason=reason
    )
    timesheet.append_nightDisturbance(night_disturbance)
    context.user_data['timesheet'] = timesheet

    reply_keyboard = [[Options.NO, Options.YES]]
    update.message.reply_text(text=Replies.DISTURBANCE_ASK_ANOTHER,
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, input_field_placeholder= f"Type {Options.YES} or {Options.NO}")
            )
    return NIGHT_PROMPT



def run_bot():
    print("Bot running...")
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler(Commands.HELP, help))
    dispatcher.add_handler(CommandHandler(Commands.INFO, info))
    dispatcher.add_handler(CommandHandler(Commands.CANCEL, cancel))


    setup_conversation_handler = ConversationHandler(
        entry_points=[CommandHandler(Commands.SETUP, setup)],
        states={
            FIRST_NAME: [MessageHandler(Filters.text, first_name)],
            LAST_NAME: [MessageHandler(Filters.text, last_name)],
            HOSPITAL_NAME: [MessageHandler(Filters.text, hospital_name)],
            SIGNATURE: [MessageHandler(Filters.photo, signature)],
        },
        fallbacks=[CommandHandler(Commands.CANCEL, cancel), CommandHandler(Commands.HELP, help)],
        conversation_timeout  = timedelta(seconds=600)
        )

    edit_conversation_handler = ConversationHandler(
        entry_points=[CommandHandler(Commands.EDIT, edit)],
        states={
            FIRST_NAME_EDIT: [MessageHandler(Filters.text, edit_first_name)],
            LAST_NAME_EDIT: [MessageHandler(Filters.text, edit_last_name)],
            HOSPITAL_NAME_EDIT: [MessageHandler(Filters.text, edit_hospital_name)],
            SIGNATURE_EDIT: [MessageHandler(Filters.photo, edit_signature)],
            
            FIRST_NAME_EDIT_PROMPT: [MessageHandler(Filters.regex('^(Yes|No)$'), edit_first_name_prompt)],
            LAST_NAME_EDIT_PROMPT: [MessageHandler(Filters.regex('^(Yes|No)$'), edit_last_name_prompt)],
            HOSPITAL_NAME_EDIT_PROMPT: [MessageHandler(Filters.regex('^(Yes|No)$'), edit_hospital_name_prompt)],
            SIGNATURE_EDIT_PROMPT: [MessageHandler(Filters.regex('^(Yes|No)$'), edit_signature_prompt)],
        },
        fallbacks=[CommandHandler(Commands.CANCEL, cancel), CommandHandler(Commands.HELP, help)],
        conversation_timeout = timedelta(seconds=600)
        )
    
    delete_conversation_handler = ConversationHandler(
        entry_points=[CommandHandler(Commands.DELETE, delete)],
        states={
            DELETE_USER: [MessageHandler(Filters.regex('^(Yes|No)$'), delete_user)],
        },
        fallbacks=[CommandHandler(Commands.CANCEL, cancel), CommandHandler(Commands.HELP, help)]
        )

    timesheet_conversation_handler = ConversationHandler(
        entry_points=[CommandHandler(Commands.SPOT, timesheet)],
        states = {
            TIMESHEET_START_DATE: [MessageHandler(Filters.text, timesheet_start_date)],
            TIMESHEET_START_TIME: [MessageHandler(Filters.text, timesheet_start_time)],
            TIMESHEET_DAYS: [MessageHandler(Filters.text, timesheet_days)],
            TIMESHEET_END_TIME: [MessageHandler(Filters.text, timesheet_end_time)],
            NIGHT_PROMPT: [MessageHandler(Filters.regex('^(Yes|No)$'), night_prompt)],
            NIGHT_DAY: [MessageHandler(Filters.text, night_day)],
            NIGHT_TIME: [MessageHandler(Filters.text, night_time)],
            NIGHT_DURATION: [MessageHandler(Filters.text, night_duration)],
            NIGHT_REASON: [MessageHandler(Filters.text, night_reason)],
        },
        fallbacks=[CommandHandler(Commands.CANCEL, cancel), CommandHandler(Commands.HELP, help)],
        conversation_timeout = timedelta(seconds=600)
    )

    samad_conversation_handler = ConversationHandler(
        entry_points=[CommandHandler(Commands.SAM, sam)],
        states = {
            SAM_MESSAGE: [MessageHandler(Filters.text, sam_message)] 
        },
        fallbacks=[CommandHandler(Commands.CANCEL, cancel)]
    )

    dispatcher.add_handler(setup_conversation_handler)
    dispatcher.add_handler(edit_conversation_handler)
    dispatcher.add_handler(delete_conversation_handler)
    dispatcher.add_handler(timesheet_conversation_handler)
    dispatcher.add_handler(samad_conversation_handler)
    dispatcher.add_handler(MessageHandler(Filters.text, general))
    dispatcher.add_error_handler(error)
    updater.start_polling()
    updater.idle()
    

if __name__ == '__main__':
    run_bot()