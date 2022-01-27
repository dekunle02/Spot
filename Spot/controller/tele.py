import os
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
    Message,
    Bot,
    Update,
    File,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove)

from database import fire, models
from . import parser
from .replies import Replies 

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

"""
General handlers
"""
def help(update: Update, context: CallbackContext):
    update.message.reply_text(text= Replies.HELP_MESSAGE)

def error(update: Update, context: CallbackContext) -> int:
    sender = update.message.from_user
    context.bot.send_message(
        chat_id=MY_TELEGRAM_ID, 
        text=f"{update.message.text} sent by @{sender.first_name} id-{sender.id}\nUpdate {update} caused error {context.error}")
    update.message.reply_text(text=Replies.ERROR_MESSAGE)

def general(update: Update, context: CallbackContext) -> int:
    user = fire.get_user_with_id(update.message.from_user.id)
    if user:
        update.message.reply_text(
            Replies.IDLE_MESSAGE
        )
    else:
       update.message.reply_text(
            Replies.WELCOME_MESSAGE
        ) 

def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        Replies.CANCEL_MESSAGE
    )
    return ConversationHandler.END


"""
SetUp New User Flow
"""
def setup(update: Update, context: CallbackContext) -> int:
    user = fire.get_user_with_id(update.message.from_user.id)
    if user:
        update.message.reply_text(
        Replies.ALREADY_SETUP_MESSAGE, quote=False
        )
        return ConversationHandler.END
    update.message.reply_text(
        Replies.FIRST_NAME_ASK, quote=False
    )
    return FIRST_NAME

def first_name(update: Update, context: CallbackContext) -> int:
    first_name = update.message.text.strip().capitalize()
    context.user_data['first_name'] = first_name
    update.message.reply_text(
        Replies.LAST_NAME_ASK
    )
    return LAST_NAME

def last_name(update: Update, context: CallbackContext) -> int:
    last_name = update.message.text.strip().capitalize()
    context.user_data["last_name"] = last_name
    update.message.reply_text(
        Replies.HOSPITAL_NAME_ASK
    )
    return HOSPITAL_NAME

def hospital_name(update: Update, context: CallbackContext) -> int:
    hospital_name = parser.cap_each_word(update.message.text)
    context.user_data["hospital_name"] = hospital_name
    update.message.reply_text(
        Replies.SIGNATURE_ASK
    )
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
        update.message.reply_text(Replies.FIRST_NAME_ASK, reply_markup=ReplyKeyboardRemove())
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
View Information Flow
"""
def info(update:Update, context: CallbackContext):
    user = fire.get_user_with_id(update.message.from_user.id)
    if user:
        reply = f"Here you go\n\nFirst name: {user.first_name}\nLast name: {user.last_name}\nHospital:{user.hospital_name}"
        update.message.reply_text(reply)
    else:
        update.message.reply_text(
            Replies.UNKNOWN_USER_INFO_ASK
        )


def run_bot():
    print("Bot running")
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler(Commands.HELP, help))
    dispatcher.add_handler(CommandHandler(Commands.INFO, info))

    setup_conversation_handler = ConversationHandler(
        entry_points=[CommandHandler(Commands.SETUP, setup)],
        states={
            FIRST_NAME: [MessageHandler(Filters.text, first_name)],
            LAST_NAME: [MessageHandler(Filters.text, last_name)],
            HOSPITAL_NAME: [MessageHandler(Filters.text, hospital_name)],
            SIGNATURE: [MessageHandler(Filters.photo, signature)],
        },
        fallbacks=[CommandHandler(Commands.CANCEL, cancel), CommandHandler(Commands.HELP, help)]
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
        fallbacks=[CommandHandler(Commands.CANCEL, cancel), CommandHandler(Commands.HELP, help)]
        )
    
    delete_conversation_handler = ConversationHandler(
        entry_points=[CommandHandler(Commands.DELETE, delete)],
        states={
            DELETE_USER: [MessageHandler(Filters.regex('^(Yes|No)$'), delete_user)],
        },
        fallbacks=[CommandHandler(Commands.CANCEL, cancel), CommandHandler(Commands.HELP, help)]
        )

    dispatcher.add_handler(setup_conversation_handler)
    dispatcher.add_handler(edit_conversation_handler)
    dispatcher.add_handler(delete_conversation_handler)
    dispatcher.add_handler(MessageHandler(Filters.text, general))

    dispatcher.add_error_handler(error)

    updater.start_polling()
    updater.idle()
