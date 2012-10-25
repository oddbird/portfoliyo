"""Pusher events."""
from portfoliyo.pusher import get_pusher



def student_added(student, elder):
    """Send Pusher notification that ``student`` was added to ``elder``."""
    pusher = get_pusher()
    if pusher is None:
        return
    from portfoliyo.api.resources import ProfileResource
    profile_resource = ProfileResource()
    b = profile_resource.build_bundle(obj=student)
    data = profile_resource.full_dehydrate(b).data
    data['groups'] = list(
        student.student_in_groups.values_list('pk', flat=True))
    channel = pusher['students_of_%s' % elder.id]
    channel.trigger('student_added', {'objects': [data]})
