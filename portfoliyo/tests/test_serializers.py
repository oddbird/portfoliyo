import datetime

from django.utils.timezone import utc
import mock
import pytest
import pytz

from portfoliyo import serializers
from portfoliyo.tests import factories


class MockNow(object):
    """
    Fake replacement for now() function.

    Instantiate with args/kwargs as taken by datetime.datetime(). If no
    timezone is provided, UTC is assumed. The resulting timezone-aware datetime
    is considered the current real time in that timezone.

    When called, if a timezone is provided, the current time is converted to
    that timezone before being returned.

    """
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('tzinfo', utc)
        self.now = datetime.datetime(*args, **kwargs)


    def __call__(self, tzinfo=None):
        if tzinfo is not None:
            return self.now.astimezone(tzinfo)
        return self.now



@pytest.fixture
def mock_now(request):
    """
    Mock out portfoliyo.serializers.now() for a test.

    If the given test has a ``mock_now`` mark, use its args/kwargs as
    instantiation args/kwargs for a ``MockNow`` fake. Otherwise, use a regular
    ``Mock`` object with no special initialization, the test is responsible to
    set up the return value manually.

    """
    if 'mock_now' in request.keywords:
        data = request.keywords['mock_now']
        mock_now = MockNow(*data.args, **data.kwargs)
    else:
        mock_now = mock.Mock()
    patcher = mock.patch('portfoliyo.serializers.now', mock_now)
    mock_now = patcher.start()
    request.addfinalizer(patcher.stop)

    return mock_now



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
        'date': u'September 17, 2012',
        'naturaldate': u'September 17, 2012',
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


@pytest.mark.mock_now(2013, 2, 11, tzinfo=utc)
def test_post2dict_naturaldate(mock_now):
    """Naturaldate for a nearby date."""
    post = factories.PostFactory.build(
        timestamp=datetime.datetime(2013, 2, 11, tzinfo=utc))
    assert serializers.post2dict(post)['naturaldate'] == u"today"



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


denver = pytz.timezone('America/Denver')


class TestNaturalDate(object):
    @pytest.mark.mock_now(2012, 1, 3)
    def test_today(self, mock_now):
        d = datetime.datetime(2012, 1, 3)
        assert serializers.naturaldate(d) == u"today"


    @pytest.mark.mock_now(2012, 1, 3, 1, tzinfo=utc)
    def test_today_timezone(self, mock_now):
        d = datetime.datetime(2012, 1, 2, 23, tzinfo=denver)
        assert serializers.naturaldate(d) == u"today"


    @pytest.mark.mock_now(2012, 1, 3)
    def test_yesterday(self, mock_now):
        d = datetime.datetime(2012, 1, 2)
        assert serializers.naturaldate(d) == u"yesterday"


    @pytest.mark.mock_now(2013, 2, 11)
    def test_day_of_week(self, mock_now):
        d = datetime.datetime(2013, 2, 5)
        assert serializers.naturaldate(d) == u"Tuesday"


    @pytest.mark.mock_now(2013, 2, 11)
    def test_same_year(self, mock_now):
        d = datetime.datetime(2013, 1, 15)
        assert serializers.naturaldate(d) == u"January 15"


    @pytest.mark.mock_now(2013, 2, 11)
    def test_different_year(self, mock_now):
        d = datetime.datetime(2012, 1, 15)
        assert serializers.naturaldate(d) == u"January 15, 2012"
