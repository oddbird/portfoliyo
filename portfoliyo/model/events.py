"""Pusher events."""
from portfoliyo.pusher import get_pusher



def student_added(student, *elders):
    """Send Pusher notification that ``student`` was added to ``elders``."""
    student_event('student_added', student, *elders)



def student_removed(student, *elders):
    """Send Pusher notification that ``student`` was removed from ``elders``."""
    student_event('student_removed', student, *elders)



def student_edited(student, *elders):
    """Send Pusher notification that ``student`` was edited to ``elders``."""
    student_event('student_edited', student, *elders)



def student_event(event, student, *elders):
    """Send Pusher ``event`` regarding ``student`` to ``elders``."""
    pusher = get_pusher()
    if pusher is None:
        return
    from portfoliyo.api.resources import SlimProfileResource
    profile_resource = SlimProfileResource()
    b = profile_resource.build_bundle(obj=student)
    data = profile_resource.full_dehydrate(b).data
    data['groups'] = list(
        student.student_in_groups.values_list('pk', flat=True))
    for elder in elders:
        channel = pusher['students_of_%s' % elder.id]
        channel.trigger(event, {'objects': [data]})
