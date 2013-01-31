"""New-teacher notification collector."""
from portfoliyo import model
from portfoliyo.notifications import types
from . import base



class Signup(object):
    """Encapsulates a single family-member signing up in a single village."""
    def __init__(self, student, family, role, group=None):
        self.student = student
        self.family = family
        self.role = role
        self.group = group


    @classmethod
    def from_textsignup(cls, text_signup):
        """Instantiate from a ``TextSignup`` model instance."""
        try:
            rel = model.Relationship.objects.get(
                from_profile=text_signup.family,
                to_profile=text_signup.student)
        except model.Relationship.DoesNotExist:
            role = text_signup.family.role
        else:
            role = rel.description_or_role
        return cls(
            text_signup.student, text_signup.family, role, text_signup.group)



class NewParentCollector(base.NotificationTypeCollector):
    """
    Collects new-parent notifications.

    Template context provided:

    ``signups`` is a list of ``Signup`` objects.

    """
    type_name = types.NEW_PARENT
    subject_template = 'notifications/activity/_new_parents.subject.txt'
    db_lookup = {'signup-id': (model.TextSignup, 'signup')}
    notification_pref = 'notify_new_parent'


    def get_context(self):
        return {
            'signups': [
                Signup.from_textsignup(n['signup'])
                for n in self.notifications
                ],
            'any_requested_new_parent': self.any_requested(),
            'any_nonrequested_new_parent': self.any_nonrequested(),
            }


    def hydrate(self, data):
        """Add 'student' key to hydrated data."""
        hydrated = super(NewParentCollector, self).hydrate(data)
        student = hydrated['signup'].student
        # signups without students are not valid for notification
        if not student:
            raise base.RehydrationFailed()
        hydrated['student'] = student
        return hydrated
