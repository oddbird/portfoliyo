from django.core import mail
import mock

from portfoliyo import email



def test_send_templated_multipart():
    with mock.patch('portfoliyo.email.render_to_string') as mock_render:
        mock_render.side_effect = ['first', 'second', 'third\nhere']
        email.send_templated_multipart(
            'some/template', {'a': 1}, ['foo@example.com'])

    mock_render.assert_any_call('some/template.txt', {'a': 1})
    mock_render.assert_any_call('some/template.html', {'a': 1})
    mock_render.assert_any_call('some/template.subject.txt', {'a': 1})

    assert len(mail.outbox) == 1
    msg = mail.outbox[0]
    assert msg.to == ['foo@example.com']
    assert msg.subject == 'third here'
    assert msg.body == 'first'
    assert msg.alternatives == [('second', 'text/html')]
