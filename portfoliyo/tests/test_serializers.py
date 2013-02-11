import datetime

from django.utils.timezone import utc

from portfoliyo import serializers
from portfoliyo.tests import factories



def test_post2dict(db):
    """post2dict returns dictionary of post data."""
    rel = factories.RelationshipFactory.create(
        from_profile__name='The Teacher', description='desc')
    post = factories.PostFactory.create(
        author=rel.elder,
        student=rel.student,
        relationship=rel,
        timestamp=datetime.datetime(2012, 9, 17, 5, 30, tzinfo=utc),
        html_text='Foo',
        )

    assert serializers.post2dict(post, extra="extra") == {
        'post_id': post.id,
        'author_id': rel.elder.id,
        'student_id': rel.student.id,
        'author': 'The Teacher',
        'role': u'desc',
        'timestamp': '2012-09-17T01:30:00-04:00',
        'date': u'9/17/2012',
        'time': u'1:30 a.m.',
        'text': 'Foo',
        'extra': 'extra',
        'sms': False,
        'to_sms': False,
        'from_sms': False,
        'sms_recipients': '',
        'plural_sms': '',
        'num_sms_recipients': 0,
        }



def test_post2dict_no_author():
    """Special handling for author-less (automated) posts."""
    student = factories.ProfileFactory.build()
    post = factories.PostFactory.build(author=None, student=student)

    d = serializers.post2dict(post)

    assert d['author_id'] == 0
    assert d['author'] == ""
    assert d['role'] == "Portfoliyo"



def test_post2dict_no_relationship(db):
    """If relationship is gone, uses author's role instead."""
    rel = factories.RelationshipFactory.create(
        from_profile__name='The Teacher',
        from_profile__role='role',
        description='desc',
        )
    post = factories.PostFactory.create(
        author=rel.elder,
        student=rel.student,
        )
    rel.delete()

    assert serializers.post2dict(post)['role'] == 'role'
