import datetime

from django.utils import timezone
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
        kwargs.setdefault('tzinfo', timezone.utc)
        self.now = datetime.datetime(*args, **kwargs)


    def __call__(self):
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



@pytest.fixture(autouse=True)
def _current_timezone(request):
    """Use current timezone as given in a mark."""
    if 'timezone' in request.keywords:
        cm = timezone.override(request.keywords['timezone'].args[0])
        cm.__enter__()
        request.addfinalizer(lambda: cm.__exit__(None, None, None))



@pytest.mark.timezone(timezone.utc)
def test_post2dict(db):
    """post2dict returns dictionary of post data."""
    rel = factories.RelationshipFactory.create(
        from_profile__name='The Teacher', description='desc')
    post = factories.PostFactory.create(
        author=rel.elder,
        student=rel.student,
        relationship=rel,
        timestamp=datetime.datetime(2012, 9, 17, 5, 30, tzinfo=timezone.utc),
        html_text='Foo',
        )

    assert serializers.post2dict(post, extra="extra") == {
        'post_id': post.id,
        'type': 'message',
        'author_id': rel.elder.id,
        'student_id': rel.student.id,
        'author': 'The Teacher',
        'role': u'desc',
        'school_staff': False,
        'timestamp': '2012-09-17T05:30:00+00:00',
        'timestamp_display': u'Sep 17 2012, 5:30am',
        'text': 'Foo',
        'extra': 'extra',
        'sms': False,
        'to_sms': False,
        'from_sms': False,
        'sms_recipients': '',
        'plural_sms': '',
        'num_sms_recipients': 0,
        'attachment_url': '',
        }


@pytest.mark.timezone(timezone.utc)
@pytest.mark.mock_now(2013, 2, 11, tzinfo=timezone.utc)
def test_post2dict_timestamp_display(mock_now):
    """Natural date for a nearby date."""
    post = factories.PostFactory.build(
        timestamp=datetime.datetime(2013, 2, 11, 8, 32, tzinfo=timezone.utc))
    assert serializers.post2dict(post)['timestamp_display'] == u"8:32am"



def test_post2dict_no_author():
    """Special handling for author-less (automated) posts."""
    student = factories.ProfileFactory.build()
    post = factories.PostFactory.build(author=None, student=student)

    d = serializers.post2dict(post)

    assert d['author_id'] == 0
    assert d['author'] == "Portfoliyo"
    assert d['role'] == ""



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


@pytest.mark.timezone(timezone.utc)
class TestNaturalDateTime(object):
    @pytest.mark.mock_now(2012, 1, 3, tzinfo=timezone.utc)
    def test_today(self, mock_now):
        """A date today is rendered as just the time."""
        d = datetime.datetime(2012, 1, 3, 8, 23, tzinfo=timezone.utc)
        assert serializers.naturaldatetime(d) == u"8:23am"


    @pytest.mark.mock_now(2013, 2, 11, tzinfo=timezone.utc)
    def test_day_of_week(self, mock_now):
        """A date within the past week is rendered as weekday and time."""
        d = datetime.datetime(2013, 2, 5, 15, 45, tzinfo=timezone.utc)
        assert serializers.naturaldatetime(d) == u"Tue 3:45pm"


    @pytest.mark.mock_now(2013, 2, 11, tzinfo=timezone.utc)
    def test_same_year(self, mock_now):
        """A date within the current year is date and time without year."""
        d = datetime.datetime(2013, 1, 15, 8, 12, tzinfo=timezone.utc)
        assert serializers.naturaldatetime(d) == u"Jan 15, 8:12am"


    @pytest.mark.mock_now(2013, 2, 11, tzinfo=timezone.utc)
    def test_different_year(self, mock_now):
        """A date in a different year is date and time with year."""
        d = datetime.datetime(2012, 1, 15, 10, 34, tzinfo=timezone.utc)
        assert serializers.naturaldatetime(d) == u"Jan 15 2012, 10:34am"


    @pytest.mark.mock_now(2012, 1, 3, 1, tzinfo=timezone.utc)
    def test_today_timezone(self, mock_now):
        """Values are normalized to local time correctly."""
        d = datetime.datetime(2012, 1, 2, 23, 10, tzinfo=denver)
        with timezone.override(denver):
            assert serializers.naturaldatetime(d) == u"11:10pm"
        with timezone.override(timezone.utc):
            assert serializers.naturaldatetime(d) == u"6:10am"


    @pytest.mark.mock_now(2013, 2, 11, tzinfo=timezone.utc)
    def test_timezone_naive(self, mock_now):
        """A naive datetime is assumed to be local time."""
        d = datetime.datetime(2012, 1, 15, 10, 34)
        with timezone.override(denver):
            assert serializers.naturaldatetime(d) == u"Jan 15 2012, 10:34am"
