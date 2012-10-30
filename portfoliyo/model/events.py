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
    # allows resource_uri to be generated
    profile_resource._meta.api_name = 'v1'
    b = profile_resource.build_bundle(obj=student)
    b = profile_resource.full_dehydrate(b)
    data = profile_resource._meta.serializer.to_simple(b, None)
    data['groups'] = list(
        student.student_in_groups.values_list('pk', flat=True))
    for elder in elders:
        channel = pusher['students_of_%s' % elder.id]
        channel.trigger(event, {'objects': [data]})



def group_added(group):
    group_event('group_added', group)



def group_removed(group):
    group_event('group_removed', group)



def group_edited(group):
    group_event('group_edited', group)



def group_event(event, group):
    """Send Pusher ``event`` regarding ``group`` to its owner."""
    pusher = get_pusher()
    if pusher is None:
        return
    from portfoliyo.api.resources import GroupResource
    group_resource = GroupResource()
    b = group_resource.build_bundle(obj=group)
    b = group_resource.full_dehydrate(b)
    data = group_resource._meta.serializer.to_simple(b, None)
    channel = pusher['groups_of_%s' % group.owner.id]
    channel.trigger(event, {'objects': [data]})
