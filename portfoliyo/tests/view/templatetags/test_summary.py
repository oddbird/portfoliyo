import pytest

from portfoliyo.view.templatetags.summary import summary


class Thing(object):
    def __init__(self, name):
        self.name = name


    def __unicode__(self):
        return self.name



def things(*names):
    """Helper to build list of Things from list of names."""
    return [Thing(n) for n in names]



def s(names, options=''):
    """Helper for calling summary with list of Things with given names."""
    return summary(things(*names), options)


def test_empty():
    assert s([]) == "nobody"


def test_single():
    assert s(["Foo"]) == "Foo"


def test_two():
    assert s(["Foo", "Bar"]) == "two things"


@pytest.mark.parametrize('negation', ['no', 'false', 'No', 'False', '0'])
def test_no_apnumber(negation):
    assert s(["Foo", "Bar"], "apnumber=%s" % negation) == "2 things"


def test_named():
    assert s(["Foo"], "named='s place") == "Foo's place"


def test_unnamed():
    assert s(["Foo", "Bar"], "unnamed=places") == "two places"


def test_max_two():
    assert s(
        ["Foo", "Bar", "Baz", "Bill"],
        "max=2") == "Foo and three other things"


def test_max_three_with_unnamed():
    assert s(
        ["Foo", "Bar", "Baz", "Bill"],
        "max=3:unnamed=places") == "Foo, Bar and two other places"
