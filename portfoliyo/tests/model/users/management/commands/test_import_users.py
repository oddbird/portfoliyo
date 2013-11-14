from cStringIO import StringIO

from django.core.management import call_command, CommandError
import mock
import pytest

from portfoliyo.model import Profile
from portfoliyo.model.users.management.commands import import_users
from portfoliyo.tests import factories as f



@pytest.mark.parametrize('verbosity', [True, False])
@pytest.mark.parametrize('sourcephone', [None, '+13216540987'])
def test_calls_import_from_csv(monkeypatch, verbosity, sourcephone):
    mock_import = mock.Mock()
    monkeypatch.setattr(import_users, 'import_from_csv', mock_import)

    mock_get = mock.Mock()
    monkeypatch.setattr(Profile.objects, 'get', mock_get)

    mock_stdout = StringIO()

    created_user = f.ProfileFactory.build(name='created')
    found_user = f.ProfileFactory.build(name='found')
    mock_import.return_value = ([created_user], [found_user])

    mock_get.return_value = f.ProfileFactory.build(
        user__email='teacher@example.com')

    args = ['import_users', 'teacher@example.com', 'somefile.csv']
    if sourcephone:
        args.append(sourcephone)
    call_command(*args, stdout=mock_stdout, verbosity='1' if verbosity else '0')

    expected_args = [mock_get.return_value, 'somefile.csv', sourcephone]
    mock_import.assert_called_once_with(*expected_args)
    mock_stdout.seek(0)
    output = mock_stdout.read()
    if verbosity:
        assert 'Created created.' in output
        assert 'Found found.' in output
    else:
        assert not output


def test_bad_teacher_email(monkeypatch):
    mock_get = mock.Mock()
    monkeypatch.setattr(Profile.objects, 'get', mock_get)

    mock_get.side_effect = Profile.DoesNotExist()

    command = import_users.Command()
    with pytest.raises(CommandError):
        command.handle('teacher@example.com', 'somefile.csv')


def test_bad_number_args(monkeypatch):
    command = import_users.Command()
    with pytest.raises(CommandError):
        command.handle()
