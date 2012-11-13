"""Pusher events."""
import logging

from portfoliyo.pusher import get_pusher


logger = logging.getLogger(__name__)



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
    from portfoliyo.api.resources import SlimProfileResource
    profile_resource = SlimProfileResource()
    # allows resource_uri to be generated
    profile_resource._meta.api_name = 'v1'
    b = profile_resource.build_bundle(obj=student)
    b = profile_resource.full_dehydrate(b)
    data = profile_resource._meta.serializer.to_simple(b, None)
    for elder in elders:
        trigger('students_of_%s' % elder.id, event, {'objects': [data]})



def group_added(group):
    group_event('group_added', group)



def group_removed(group):
    group_event('group_removed', group)



def group_edited(group):
    group_event('group_edited', group)



def group_event(event, group):
    """Send Pusher ``event`` regarding ``group`` to its owner."""
    from portfoliyo.api.resources import SlimGroupResource
    group_resource = SlimGroupResource()
    # allows resource_uri to be generated
    group_resource._meta.api_name = 'v1'
    b = group_resource.build_bundle(obj=group)
    b = group_resource.full_dehydrate(b)
    data = group_resource._meta.serializer.to_simple(b, None)
    trigger('groups_of_%s' % group.owner.id, event, {'objects': [data]})



def student_added_to_group(owner, students, groups):
    """Added event needs full student data."""
    from portfoliyo.api.resources import SlimProfileResource
    profile_resource = SlimProfileResource()
    # allows resource_uri to be generated
    profile_resource._meta.api_name = 'v1'
    group_ids = [g.id for g in groups]
    objects = []
    for student in students:
        b = profile_resource.build_bundle(obj=student)
        b = profile_resource.full_dehydrate(b)
        data = profile_resource._meta.serializer.to_simple(b, None)
        data['groups'] = group_ids
        objects.append(data)
    trigger(
        'groups_of_%s' % owner.id,
        'student_added_to_group',
        {
            'objects': objects
            },
        )



def student_removed_from_group(owner, students, groups):
    """Removed event only needs student ID."""
    group_ids = [g.id for g in groups]
    trigger(
        'groups_of_%s' % owner.id,
        'student_removed_from_group',
        {
            'objects': [
                {'id': s.id, 'groups': group_ids} for s in students]
            },
        )



def trigger(channel, event, data):
    """
    Fire ``event`` on ``channel`` with ``data`` if Pusher is configured.

    Log failures, but never blow up.

    """
    pusher = get_pusher()
    if pusher is None:
        return
    try:
        pusher['private-%s' % channel].trigger(event, data)
    except Exception as e:
        logger.error("Pusher exception: %s" % str(e))
