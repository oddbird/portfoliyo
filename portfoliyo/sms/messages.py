# -*- coding: utf-8 -*-
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
            u"No problem! Sorry to have bothered you. "
            u"Text this number anytime to re-start."
            ),
        'es': (
            u"No hay problema! Siento haberte molestado. "
            u"Envía un texto a este número en cualquier momento "
            u"para volver a empezar."
            )
        },

    'ACTIVATED': {
        'en': u"You can text this number to talk with %s.",
        'es': u"Usted puede enviar un texto a este número para hablar con %s.",
        },

    'NO_STUDENTS': {
        'en': (
            u"Sorry, we can't find any students connected to your number, "
            u"so we can't deliver your message. "
            u"Please text a teacher code to connect with that teacher."
            ),
        'es': (
            u"No encontramos ningún estudiante conectados a su número, "
            u"por lo que no se puede entregar su mensaje. "
            u"Texto maestro código para conectarse con ese maestro."
            ),
        },

    'NO_TEACHERS': {
        'en': (
            u"Sorry, we can't find any teachers connected to your number, "
            u"so we can't deliver your message. "
            u"Please text a teacher code to connect with that teacher."
            ),
        'es': (
            u"No encontramos ningún maestro conectados a su número, "
            u"por lo que no se puede entregar su mensaje. "
            u"Texto maestro código para conectarse con ese maestro."
            ),
        },

    'STUDENT_NAME': {
        'en': u"Thanks! What is the name of your child in %s's class?",
        'es': (
            u"¡Gracias! "
            u"¿Cuál es el nombre de su hijo en la clase del %s?"
            ),
        },

    'RELATIONSHIP': {
        'en': (
            u"And what is your relationship to that child "
            u"(mother, father, ...)?"
            ),
        'es': u"¿Y cuál es su relación con el niño (madre, padre, ...)?",
        },

    'NAME': {
        'en': (
            u"Last question: "
            u"what is your name? (So %s knows who is texting.)"
            ),
        'es': (
            u"Última pregunta: ¿Cuál es su nombre? "
            u"(Para que el %s sepa quién está enviando mensajes de texto)."
            ),
        },

    'ALL_DONE': {
        'en': u"All done, thank you! You can text this number to talk with %s.",
        'es': (
            u"Listo, gracias! "
            u"Ahora puede textear a este número para hablar con %s.",
            )
        },

    'SUBSEQUENT_CODE_DONE': {
        'en': u"Ok, thanks! You can text %s at this number too.",
        'es': u"¡Ok, gracias! Usted puede texto del %s en este número también.",
        },

    'STUDENT_NAME_FOLLOWUP': {
        'en': u"And what's the student's name?",
        'es': u"¿Y cuál es el nombre de su hijo?",
        },

    'RELATIONSHIP_FOLLOWUP': {
        'en': u"And what's your relationship to the student?",
        'es': u"¿Y cuál es su relación con el niño?",
        },

    'NAME_FOLLOWUP': {
        'en': u"And what's your name?",
        'es': u"¿Y cuál es su nombre?",
        },

    'UNKNOWN': {
        # This is here to keep all the messages together, but there's no point
        # in having it translated; we don't know who we're replying to, so we
        # don't know what language to use anyway.
        'en': (
            u"We don't recognize your phone number, "
            u"so we don't know who to send your text to! "
            u"If you are just signing up, "
            u"make sure your invite code is typed correctly."
            ),
        },
    }
