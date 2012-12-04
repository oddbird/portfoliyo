from django.core.urlresolvers import reverse

from portfoliyo.tests import factories


def admin():
    return factories.ProfileFactory.create(
        user__is_staff=True, user__is_superuser=True).user



def test_post_changelist(client, db):
    factories.PostFactory.create()

    url = reverse('admin:village_post_changelist')

    client.get(url, user=admin(), status=200)



def test_filter_by_author(client, db):
    factories.PostFactory.create(original_text='foobar')
    p = factories.PostFactory.create(original_text='other')

    url = reverse('admin:village_post_changelist') + '?author=%s' % p.author_id
    response = client.get(url, user=admin(), status=200)

    assert 'foobar' not in response



def test_filter_by_no_author(client, db):
    factories.PostFactory.create(original_text='foobar')
    factories.PostFactory.create(original_text='other', author=None)

    url = reverse('admin:village_post_changelist') + '?author=0'
    response = client.get(url, user=admin(), status=200)

    assert 'foobar' not in response



def test_filter_by_student(client, db):
    factories.PostFactory.create(original_text='foobar')
    p = factories.PostFactory.create(original_text='other')

    url = reverse(
        'admin:village_post_changelist') + '?student=%s' % p.student_id
    response = client.get(url, user=admin(), status=200)

    assert 'foobar' not in response



def test_filter_by_school(client, db):
    factories.PostFactory.create(original_text='foobar')
    p = factories.PostFactory.create(original_text='other')

    url = reverse(
        'admin:village_post_changelist') + '?school=%s' % p.student.school_id
    response = client.get(url, user=admin(), status=200)

    assert 'foobar' not in response
