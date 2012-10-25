"""Pusher events."""
from portfoliyo.api import resources
from portfoliyo.pusher import get_pusher



def student_added(student):
    pusher = get_pusher()
    if pusher is None:
        return
    profile_resource = resources.ProfileResource()
    for elder in student.elders:
        channel = pusher['students_of_%s' % elder.id]
        b = profile_resource.build_bundle(obj=student)
        data = profile_resource.full_dehydrate(b).data
        data['groups'] = list(
            student.student_in_groups.values_list('pk', flat=True))
        channel.trigger('student_added', {'objects': [data]})
