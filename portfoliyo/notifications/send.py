"""
Rendering and sending of notifications.

Summary of template context needed:

``students`` is a list of students affected by any notification.

``added_to_villages`` is a list of villages, with ``student`` and ``added_by``
attributes, sorted by ``added_by``.




"""
import logging

from django.template.loader import render_to_string

from portfoliyo import email
from portfoliyo import model

from . import store, types



logger = logging.getLogger(__name__)



def send(profile_id):
    """
    Send activity notification(s) to user with given profile ID.

    Return ``True`` if email was sent, ``False`` otherwise.

    """
    profile = model.Profile.objects.select_related('user').get(pk=profile_id)
    user = profile.user
    if user.email and user.is_active:
        notifications = store.get_and_clear_all(profile_id)

        if notifications:
            return _send_email(profile, notifications)

    return False



SUBJECT_TEMPLATE = 'notifications/activity.subject.txt'



def _send_email(profile, notifications):
    """Construct and send activity notification email."""
    by_type = {}
    for data in notifications:
        name = data.pop('name', None)
        try:
            type_class = TYPE_CLASSES[name]
        except KeyError:
            logger.warning("Unknown notification type '%s'", name)
            continue
        # @@@ transform bulk posts that I only see in one village to single post
        # (notification-type classmethod to fetch objects for IDs in data)
        type_instance = by_type.setdefault(name, type_class())
        type_instance.add(data)

    # - clear out any empty notification types (e.g. if data was invalid)
    # - populate template-rendering context and set of affected students
    context = {}
    students = set()
    for type_name, type_instance in by_type.items():
        if not type_instance:
            del by_type[type_name]
        context.update(type_instance.get_context())
        students.update(type_instance.get_students())

    # need to convert to list so it can be indexed into in template
    context['students'] = list(students)

    # bail out early if there are no valid notifications left
    if not by_type:
        return False

    # select template to use for email subject
    if len(by_type) > 1:
        subject_template = SUBJECT_TEMPLATE
    else:
        type_instance = by_type.values()[0]
        subject_template = type_instance.subject_template

    subject = render_to_string(subject_template, context)

    # @@@ strip consecutive newlines from textual templates
    text = ''
    html = ''

    email.send_multipart(subject, text, html, [profile.user.email])

    return True



class NotificationAggregator(object):
    """Base class for aggregations of notifications of the same type."""
    # these should be overridden by subclasses
    #  notification type this class aggregates (constant from types module)
    type_name = None
    #  name of template for email subject if this is only notification type
    subject_template = None
    #  mapping of source data ID keys to lookup model and hydrated data key
    db_lookup = {}


    """Base class for notification types."""
    def __init__(self):
        self.notifications = []


    def __nonzero__(self):
        return bool(self.notifications)


    def add(self, data):
        """
        Rehydrate given notification data and add to internal list.

        Rehydrating means to take any database object IDs in the given
        notification data, and query for the actual database objects needed.

        If any needed objects aren't found, return ``False`` and don't add this
        notification.

        """
        hydrated = {}
        for src_key, (model_class, dest_key) in self.db_lookup.items():
            try:
                hydrated[dest_key] = model_class.objects.get(pk=data[src_key])
            except (KeyError, model_class.DoesNotExist):
                return False
        self.notifications.append(hydrated)
        return True


    def get_context(self):
        """Get template context for this notification type."""
        return {}


    def get_students(self):
        return [n['student'] for n in self.notifications]



class AddedToVillage(object):
    def __init__(self, added_by, student):
        self.added_by = added_by
        self.student = student



class AddedToVillageNotifications(NotificationAggregator):
    type_name = types.ADDED_TO_VILLAGE
    subject_template = 'notifications/activity/_added_to_villages.subject.txt'
    db_lookup = {
        'added-by-id': (model.Profile, 'added_by'),
        'student-id': (model.Profile, 'student'),
        }


    def get_context(self):
        return {
            'added_to_villages': [
                AddedToVillage(n['added_by'], n['student'])
                for n in sorted(
                    self.notifications, key=lambda x: x['added_by'])
                ],
            }



class NewTeacherNotifications(NotificationAggregator):
    type_name = types.NEW_TEACHER
    subject_template = 'notifications/activity/_new_teachers.subject.txt'
    db_lookup = {
        'teacher-id': (model.Profile, 'teacher'),
        'student-id': (model.Profile, 'student'),
        }


    def get_context(self):
        return {}



TYPE_CLASSES = {
    types.ADDED_TO_VILLAGE: AddedToVillageNotifications,
    types.NEW_TEACHER: NewTeacherNotifications,
    }
