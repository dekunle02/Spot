#
# COMMANDS
#
SETUP_COMMAND = "setup"
EDIT_COMMAND = "edit"
INFO_COMMAND = "info"
HELP_COMMAND = "help"
SPOT_COMMAND = "spot"
CANCEL_COMMAND = "cancel"
DELETE_COMMAND = "delete"
SAM_COMMAND = "sam"
DM_COMMAND = "dm"
BC_COMMAND = "bc"


#
# OPTIONS
#
OPTION_NO = "no"
OPTION_YES = "yes"

# REPLIES
#
WELCOME_MESSAGE = f"""Hello, it’s good to have you here 🙂. My name is Spot🚀. I was created by Samad.
I’m here to help you create your NES timesheet in a few minutes.

To get started, type /{SETUP_COMMAND}
You can cancel anytime by typing /cancel
"""
IDLE_MESSAGE = "👋🏾\nType /help to see how to operate me\nType /spot to make a timesheet"
ERROR_MESSAGE = "Something went wrong with my code while trying to process that 🥴🤒...\n I am going to get Samad to fix this 🏃🏾‍♂️"
CANCEL_MESSAGE = f"""Maybe we can pick this up some other time 🥲 
You can type always type /{HELP_COMMAND} to see how we do things here 😎"""
HELP_MESSAGE = f"""🚨🚨🚨HELP MESSAGE🚨🚨🚨

Just type /help and you will always get this help message👇

📄 Type /{SPOT_COMMAND} to make a timesheet

🧑‍⚕️ Type /{INFO_COMMAND} to view your info

✍️ Type /{EDIT_COMMAND} to change your info, e.g hospital name or signature

🧹 Type /{DELETE_COMMAND} to delete all your info

💬 Type /{SAM_COMMAND} to send Samad a message.

That easy!😎
"""
UNKNOWN_USER_INFO_ASK = f"""💭 I don’t think I have any information about you yet
Not to worry, type /{SETUP_COMMAND} to get started"""

SAMAD_ASK = "What would you like to tell Samad? 👀"
SAMAD_THANKS = "I'll make sure he gets this 🏃🏾‍♂️🏃🏾‍♂️"

ALREADY_SETUP_MESSAGE = f"""I already have your information.
Type /{INFO_COMMAND} to check your info
Type /{HELP_COMMAND} to see how I work
"""

SETUP_COMPLETE_MESSAGE = """You are all set!🥳
To create a timesheet, just type /spot
Type /help to see how we do things here 😎"""
FIRST_NAME_ASK = """We should have a formal introduction here or what do you think 😎
Can you tell me your first name? e.g <b>Spot</b> 🙈"""
LAST_NAME_ASK = "That's a lovely name 😊\nand your last name?"
HOSPITAL_NAME_ASK = "Where do you work?\n e.g. <b>Nuffield Taunton</b>"
SIGNATURE_ASK = "Send a picture of your signature. I will use this to sign your timesheets on your behalf./n/nThis is saved on your device and can be deleted from your Telegram at any point."
START_DATE_ASK = """To begin, when did your shift start 📆? 

For example, type <b>20-5-2021</b> if it started on the 20th of May in 2021
Do not add any other letters or numbers, I may get confused 🥴"
    """
END_DATE_ASK = """Great! When did it end?

Don't forget to type in this format > <b>20-10-2021</b> """
DATE_ERROR = """Now I’m confused 😕
Type <b>20-10-2021</b> if you mean 20th October 2021
Do not add any other letters or numbers
"""
TIME_ASK = """What time did you start the shift ? ⏰

Type in 24hrs time format, e.g <b>17:30</b> if you started at 5:30 pm."""
END_TIME_ASK = """What time did the shift end? ⏰"""
TIME_ERROR = (
    "Sorry 😞 I only understand 24hrs time, so if you meant 12am, that would be 00:00"
)
DURATION_ASK = """How many days did you work for? 
    
Do not count the last day but count the first.
e.g if you worked from Monday to Monday that’ll count as 7, so just type the digit."""
NUMBER_INPUT_ERROR = "Send a number e.g <b>4</b>"

DISTURBANCE_ASK = "Would you like to add a Night disturbance? 👀"
DISTURBANCE_ASK_ANOTHER = "Do you want to add another? 😥"
DISTURBANCE_DAY_ASK = """Sorry 😞
On which day were you disturbed?

e.g if your shift started on Monday and you were disturbed on Friday, that’s day <b>5</b>. Type only the digit.
"""
DISTURBANCE_TIME_ASK = """At what time were you called?

Do not forget to use the 24hrs time format. So 2am is <b>02:00</b> 🕑.
"""
DISTURBANCE_DURATION_ASK = """How long did the disturbance last for?🤕
e.g 30 mins"""
DISTURBANCE_REASON_ASK = "Why were you called?👂 e.g i.v cannulation"

EDIT_FIRST_NAME_PROMPT = "Do you want to change your first name?"
EDIT_FIRST_NAME = "What is your new first name?"
EDIT_LAST_NAME_PROMPT = "Do you want to change your last name?"
EDIT_LAST_NAME = "What is your new last name?"
EDIT_HOSPITAL_NAME_PROMPT = "Do you want to change your hospital name? 🏥"
EDIT_HOSPITAL_NAME = "What is your new hospital name?"
EDIT_SIGNATURE_PROMPT = "Do you want to change your signature?"
EDIT_SIGNATURE = "Please send a photo of your new signature"
EDIT_COMPLETE = "All Done! ✅"

DELETE_USER_PROMPT = "Are you sure you want to delete your information? 🥺🥺🥺"
DELETE_USER_FINAL = "Sorry to see you go..😭"
DELETE_USER_SKIP = "Yayyy🕺🏾🕺🏾🕺🏾"

TIMESHEET_AWAITING_MESSAGE = "....⚙️⚙️pRoCESSinG⚙️⚙️...."
TIMESHEET_MESSAGE = """Here you go! 😎
Hello everyone,

I want to extend my heartfelt thanks to each of you who has used Spot. I hope it has been as helpful for you as it once was for me. Unfortunately, the time has come to say goodbye, and I’ll be shutting Spot down on October 31st. I simply don’t have the time or resources needed to continue supporting and developing it.

Thank you for all the messages and feedback over the years—it has meant so much to me. Wishing you all the best going forward.
"""


#
# CONVERSATION STATES
#
FIRST_NAME_STATE, LAST_NAME_STATE, HOSPITAL_NAME_STATE, SIGNATURE_STATE = range(0, 4)
(
    FIRST_NAME_EDIT_STATE,
    FIRST_NAME_EDIT_PROMPT_STATE,
    LAST_NAME_EDIT_STATE,
    LAST_NAME_EDIT_PROMPT_STATE,
    HOSPITAL_NAME_EDIT_STATE,
    HOSPITAL_NAME_EDIT_PROMPT_STATE,
    SIGNATURE_EDIT_STATE,
    SIGNATURE_EDIT_PROMPT_STATE,
) = range(4, 12)
(
    START_DATE_STATE,
    START_TIME_STATE,
    NUMBER_OF_DAYS_STATE,
    END_TIME_STATE,
    NIGHT_ADD_STATE,
) = range(12, 17)
NIGHT_DAY_STATE, NIGHT_TIME_STATE, NIGHT_DURATION_STATE, NIGHT_REASON_STATE = range(
    17, 21
)
DELETE_USER_STATE = 21
(
    TIMESHEET_START_DATE_STATE,
    TIMESHEET_START_TIME_STATE,
    TIMESHEET_DAYS_STATE,
    TIMESHEET_END_TIME_STATE,
) = range(22, 26)
(
    NIGHT_PROMPT_STATE,
    NIGHT_DAY_STATE,
    NIGHT_TIME_STATE,
    NIGHT_DURATION_STATE,
    NIGHT_REASON_STATE,
) = range(26, 31)
SAM_STATE, SAM_MESSAGE_STATE = (31, 32)
