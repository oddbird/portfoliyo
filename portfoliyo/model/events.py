"""Pusher events."""
from portfoliyo.pusher import get_pusher



def student_added(student, elder):
    """Send Pusher notification that ``student`` was added to ``elder``."""
    student_event('student_added', student, elder)



def student_removed(student, elder):
    """Send Pusher notification that ``student`` was removed from ``elder``."""
    student_event('student_removed', student, elder)



def student_edited(student, elder):
    """Send Pusher notification that ``student`` was edited to ``elder``."""
    student_event('student_edited', student, elder)



def student_event(event, student, elder):
    """Send Pusher ``event`` regarding ``student`` to ``elder``."""
    pusher = get_pusher()
    if pusher is None:
        return
    from portfoliyo.api.resources import SlimProfileResource
    profile_resource = SlimProfileResource()
    b = profile_resource.build_bundle(obj=student)
    data = profile_resource.full_dehydrate(b).data
    data['groups'] = list(
        student.student_in_groups.values_list('pk', flat=True))
    channel = pusher['students_of_%s' % elder.id]
    channel.trigger(event, {'objects': [data]})
