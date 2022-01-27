class Replies:
    """Wrapper around strings used in the app"""

    WELCOME_MESSAGE = "Hi there. My name is Spot 🚀. I was created by Samad. I can help you create your NES timesheets.\nTo get started type /setup.\nYou can type /cancel at any time to cancel"
    IDLE_MESSAGE = "Hello 👋🏾\nType /help to see how to operate me\nType /spot to make a timesheet."
    ERROR_MESSAGE = "Something went wrong with my code 🥴...\nSamad will come fix it. I have reported to him."
    CANCEL_MESSAGE = "Maybe we can pick this up some other time 🥲. You can type /help to learn how to talk to me"
    HELP_MESSAGE = f"Typing /help always shows this message\n"\
        f"To generate a timeSheet, type /spot\n"\
        f"To view your information, type /info\n"\
        f"To change your information, e.g hospital name or signature, type /edit\n"\
        f"To delete all your info, type /delete\n"\
        f"To send Samad a message, type /sam"
    UNKNOWN_USER_INFO_ASK = "I don't think I have your information yet. Type /setup to get started"
    
    ALREADY_SETUP_MESSAGE = "I think I have your information already. Type /info to see your information, and /help to see how I work"
    SETUP_COMPLETE_MESSAGE = "You're all set! Type /spot to create a timesheet or /help to see how I work 😄"
    FIRST_NAME_ASK = "Tell me your first name? e.g *Ciroma*"
    LAST_NAME_ASK = "And your last name? e.g *Adekunle*"
    HOSPITAL_NAME_ASK = "Where do you work? e.g *Nuffield Taunton*"
    SIGNATURE_ASK = "Send a picture of your signature. I will use this to sign your timesheets on your behalf."


    START_DATE_ASK = "To begin, when did your shift start? For example, type *20-5-2021* if it started on the 20th of May in 2021. Do not add any other letters or numbers 🙂"
    END_DATE_ASK = "When did your shift end? For example, type *20-5-2021* if it ended on the 20th of May in 2021. Do not add any other letters or numbers 🙂"
    DATE_ERROR = "I don't understand that. Type *20-5-2021* if you mean 20th of May 2021"
    TIME_ASK = "At what time of the day? e.g *17:30* if you mean 5:30pm"
    TIME_ERROR = "Hmm. I only understand 24hrs time. So if you mean 12am in the morning, that would be *00:00*"
    DURATION_ASK = "How many days did you work for? Do not count the last day of your shift, but count the first. For example, if you worked from Monday to Monday, that would count as *7*"

    DISTURBANCE_ASK = "Would you like to add a Night disturbance? 👀"
    DISTURBANCE_DAY_ASK = "On which day were you disturbed? e.g if your shift started on Monday and you were woken up on Thursday morning, you should type *4*"
    DISTURBANCE_TIME_ASK = "What time were you were called? Do not forget to give your time in 24hrs format e.g *03:00*"
    DISTURBANCE_DURATION_ASK = "How long was the disturbance? e.g **30 mins**"
    DISTURBANCE_REASON_ASK = "Why were you called? e.g I.V cannulation"

    EDIT_FIRST_NAME_PROMPT = "Do you want to change your first name? You can type /cancel to stop at any time"
    EDIT_FIRST_NAME = "What is your new first name?"
    EDIT_LAST_NAME_PROMPT = "Do you want to change your last name?"
    EDIT_LAST_NAME = "What is your new last name?"
    EDIT_HOSPITAL_NAME_PROMPT = "Do you want to change your hospital name?"
    EDIT_HOSPITAL_NAME = "What is your new hospital name?"
    EDIT_SIGNATURE_PROMPT ="Do you want to change your Signature?"
    EDIT_SIGNATURE = "Please send a photo of your new signature"
    EDIT_COMPLETE = "All Done! 🙂"

    DELETE_USER_PROMPT = "Are you sure you want to delete your information?🥺🥺🥺"
    DELETE_USER_FINAL = "Sorry to see you go..😭"
    DELETE_USER_SKIP = "Yayyy🕺🏾🕺🏾🕺🏾"

    TIMESHEET_AWAITING_MESSAGE = "....processing...."
    TIMESHEET_MESSAGE = "Here you go! 😎"

    

