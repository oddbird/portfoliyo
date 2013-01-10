"""SMS auto-message translations."""
from django.conf import settings



def get(key, lang):
    translations = MESSAGES[key]
    if lang not in translations:
        lang = settings.LANGUAGE_CODE
    return translations[lang]



MESSAGES = {
    'ACK_STOP': {
        'en': (
            "No problem! Sorry to have bothered you. "
            "Text this number anytime to re-start."
            ),
        },
    'ACTIVATED': {
        'en': "You can text this number to talk with %s.",
        },
    'NO_STUDENTS': {
        'en': (
            "Sorry, we can't find any students connected to your number, "
            "so we're not able to deliver your message. "
            "Please contact your student's teacher for help."
            ),
        },
    'STUDENT_NAME': {
        'en': "Thanks! What is the name of your child in %s's class?",
        },
    'RELATIONSHIP': {
        'en': (
            "And what is your relationship to that child "
            "(mother, father, ...)?"
            ),
        },
    'NAME': {
        'en': "Last question: what is your name? (So %s knows who is texting.)",
        },
    'ALL_DONE': {
        'en': "All done, thank you! You can text this number to talk with %s.",
        },
    'SUBSEQUENT_CODE_DONE': {
        'en': "Ok, thanks! You can text %s at this number too.",
        },
    'STUDENT_NAME_FOLLOWUP': {
        'en': "Now, what's the student's name?",
        },
    'RELATIONSHIP_FOLLOWUP': {
        'en': "Now, what's your relationship to the student?",
        },
    'NAME_FOLLOWUP': {
        'en': "Now, what's your name?",
        },
    'UNKNOWN': {
        'en': (
            "We don't recognize your phone number, "
            "so we don't know who to send your text to! "
            "If you are just signing up, "
            "make sure your invite code is typed correctly."
            ),
        },
    }
