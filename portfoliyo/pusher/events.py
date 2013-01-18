"""Pusher events."""
import logging

from portfoliyo.api import resources
from portfoliyo import model
from portfoliyo.pusher import get_pusher


logger = logging.getLogger(__name__)



def posted(post_id, **extra_data):
    """Send ``message_posted`` event for ``post_id`` with ``extra_data``."""
    posted_event(model.Post.objects.get(pk=post_id), **extra_data)



def bulk_posted(bulk_post_id, **extra_data):
    """Send ``message_posted`` event for ``post_id`` with ``extra_data``."""
    posted_event(model.BulkPost.objects.get(pk=bulk_post_id), **extra_data)



def posted_event(post, **extra_data):
    data = {'posts': [model.post_dict(post, **extra_data)]}
    teacher_ids = post.elders_in_context.filter(
        school_staff=True).values_list('pk', flat=True)
    for teacher_id in teacher_ids:
        channel = 'user_%s' % teacher_id
        trigger(channel, 'message_posted', data)



def student_added(student_id, elder_ids=None):
    """Tell ``elder_ids`` that ``student_id`` was added."""
    student_event('student_added', student_id, elder_ids)



def student_removed(student_id, elder_ids=None):
    """Tell ``elder_ids`` that ``student`` was removed."""
    student_event('student_removed', student_id, elder_ids, full_data=False)



def student_edited(student_id, elder_ids=None):
    """Tell ``elder_ids`` that ``student_id`` was edited."""
    student_event('student_edited', student_id, elder_ids)



def student_event(event, student_id, elder_ids=None, full_data=True):
    """
    Send Pusher ``event`` to ``elder_ids`` regarding ``student_id``.

    If ``elder_ids`` is None, send to all elders of student.

    """
    if full_data:
        profile_resource = resources.SlimProfileResource()
        student = model.Profile.objects.get(pk=student_id)
        # allows resource_uri to be generated
        profile_resource._meta.api_name = 'v1'
        b = profile_resource.build_bundle(obj=student)
        b = profile_resource.full_dehydrate(b)
        data = profile_resource._meta.serializer.to_simple(b, None)
    else:
        data = {'id': student_id}
    if elder_ids is None:
        elder_ids = model.Relationship.objects.filter(
            to_profile=student_id).values_list('from_profile', flat=True)
    for elder_id in elder_ids:
        trigger('user_%s' % elder_id, event, {'objects': [data]})



def group_added(group_id, owner_id):
    """Tell ``owner_id`` that ``group_id`` was added."""
    group_event('group_added', group_id, owner_id)



def group_removed(group_id, owner_id):
    """Tell ``owner_id`` that ``group_id`` was removed."""
    group_event('group_removed', group_id, owner_id, full_data=False)



def group_edited(group_id, owner_id):
    """Tell ``owner_id`` that ``group_id`` was edited."""
    group_event('group_edited', group_id, owner_id)



def group_event(event, group_id, owner_id, full_data=True):
    """Send Pusher ``event`` to ``owner_id`` regarding ``group_id``."""
    if full_data:
        group_resource = resources.SlimGroupResource()
        group = model.Group.objects.get(pk=group_id)
        # allows resource_uri to be generated
        group_resource._meta.api_name = 'v1'
        b = group_resource.build_bundle(obj=group)
        b = group_resource.full_dehydrate(b)
        data = group_resource._meta.serializer.to_simple(b, None)
    else:
        data = {'id': group_id}
    trigger('user_%s' % owner_id, event, {'objects': [data]})



def student_added_to_group(owner_id, student_ids, group_ids):
    """Tell ``owner_id`` that ``student_ids`` were added to ``group_ids``."""
    profile_resource = resources.SlimProfileResource()
    # allows resource_uri to be generated
    profile_resource._meta.api_name = 'v1'
    objects = []
    for student in model.Profile.objects.filter(pk__in=student_ids):
        b = profile_resource.build_bundle(obj=student)
        b = profile_resource.full_dehydrate(b)
        data = profile_resource._meta.serializer.to_simple(b, None)
        data['groups'] = group_ids
        objects.append(data)
    trigger(
        'user_%s' % owner_id,
        'student_added_to_group',
        {
            'objects': objects
            },
        )



def student_removed_from_group(owner_id, student_ids, group_ids):
    """Tell ``owner_id`` that ``student_ids`` were removed from ``group_ids``"""
    trigger(
        'user_%s' % owner_id,
        'student_removed_from_group',
        {
            'objects': [
                {'id': sid, 'groups': group_ids} for sid in student_ids]
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
        logger.warning(
            "Pusher exception: %s" % str(e),
            exc_info=True,
            extra={'stack': True},
            )
