import urllib

import pytest

from portfoliyo.model.users import bulk
from portfoliyo.model.users.models import Profile
from portfoliyo.tests import factories as f


@pytest.fixture
def csvfile(request, tmpdir):
    """Returns the filename of a temporary CSV file with some user info."""
    fn = str(tmpdir.join('users.csv'))
    with open(fn, 'w') as fh:
        fh.write('First Person, +13216540987,groupA\n')
        fh.write('Second Person,+13336660000,groupB::groupA\n')
    return fn



@pytest.fixture
def teacher(db):
    return f.ProfileFactory.create(
        school_staff=True, user__email='teacher@example.com')



def test_import_from_csv_file(csvfile, teacher):
    created, found = bulk.import_from_csv(teacher, csvfile)
    assert [p.name for p in created] == ['First Person', 'Second Person']
    assert [
        {g.name for g in p.students[0].student_in_groups.all()}
        for p in created
        ] == [{'groupA'}, {'groupB', 'groupA'}]
    assert found == []
    assert Profile.objects.count() == 5


def test_import_from_csv_url(csvfile, monkeypatch, teacher):
    monkeypatch.setattr(urllib, 'urlopen', lambda url: open(csvfile))
    created, found = bulk.import_from_csv(
        teacher, 'http://example.com/fake.csv')
    assert [p.name for p in created] == ['First Person', 'Second Person']
    assert found == []
    assert Profile.objects.count() == 5


def test_skip_found(csvfile, teacher):
    p = f.ProfileFactory.create(name='Second Person', phone='+13336660000')
    s = f.ProfileFactory.create(name='Second Person')
    f.RelationshipFactory.create(to_profile=s, from_profile=teacher)
    f.RelationshipFactory.create(to_profile=s, from_profile=p)
    created, found = bulk.import_from_csv(teacher, csvfile)
    assert [p.name for p in created] == ['First Person']
    assert [p.name for p in found] == ['Second Person']
    assert Profile.objects.count() == 5


def test_set_source_phone(csvfile, teacher):
    created, found = bulk.import_from_csv(teacher, csvfile, '+13216540987')
    assert [p.source_phone for p in created] == ['+13216540987', '+13216540987']
