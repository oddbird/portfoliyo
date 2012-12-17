"""Tests for user/account views."""
from django.contrib.auth import models as auth_models
from django.core import mail
from django.core.urlresolvers import reverse

from portfoliyo.tests import factories, utils


class TestLogin(object):
    """Tests for login."""
    @property
    def url(self):
        """Shortcut for login url."""
        return reverse('login')


    def test_login(self, client, db):
        """Successful login redirects."""
        factories.UserFactory.create(
            email='test@example.com', password='sekrit')

        form = client.get(self.url).forms['loginform']
        form['username'] = 'test@example.com'
        form['password'] = 'sekrit'
        res = form.submit(status=302)

        assert res['Location'] == utils.location(reverse('home'))


    def test_login_failed(self, client, db):
        """Failed login returns error message."""
        factories.UserFactory.create(
            email='test@example.com', password='sekrit')

        form = client.get(self.url).forms['loginform']
        form['username'] = 'test@example.com'
        form['password'] = 'blah'
        res = form.submit(status=200)

        res.mustcontain("Please enter a correct username and password")


    def test_display_captcha(self, client, db):
        """Sixth login attempt within a minute returns form with captcha."""
        res = client.get(self.url)
        for i in range(6):
            res = res.forms['loginform'].submit()

        form = res.forms['loginform']

        assert 'captcha' in form.fields


    def test_bad_captcha(self, client, db):
        """Bad value for captcha fails login, even with correct user/pw."""
        factories.UserFactory.create(
            email='test@example.com', password='sekrit')

        session_data = {}

        with utils.patch_session(session_data):
            res = client.get(self.url)
            for i in range(6):
                res = res.forms['loginform'].submit()

            form = res.forms['loginform']
            answer = session_data['auth_captcha_answer']
            form['captcha'] = answer + 1 # oops, wrong answer!
            form['username'] = 'test'
            form['password'] = 'sekrit'
            res = form.submit(status=200)

        res.mustcontain("not the answer we were looking for")


    def test_good_captcha(self, client, db):
        """Good value for captcha allows login."""
        factories.UserFactory.create(
            email='test@example.com', password='sekrit')

        session_data = {}

        with utils.patch_session(session_data):
            res = client.get(self.url)
            for i in range(6):
                res = res.forms['loginform'].submit()

            form = res.forms['loginform']
            answer = session_data['auth_captcha_answer']
            form['captcha'] = answer
            form['username'] = 'test@example.com'
            form['password'] = 'sekrit'
            res = form.submit(status=302)

        assert res['Location'] == utils.location(reverse('home'))



class TestLogout(object):
    """Tests for logout view."""
    @property
    def url(self):
        """Shortcut for logout url."""
        return reverse('logout')


    def test_get_405(self, client, db):
        """GETting the logout view results in HTTP 405 Method Not Allowed."""
        client.get(self.url, status=405)


    def test_logout_redirect(self, client, db):
        """Successful logout POST redirects to the home page."""
        user = factories.UserFactory.create()

        url = reverse('no_students')

        form = client.get(url, user=user).forms['logoutform']
        res = form.submit(status=302)

        assert res['Location'] == utils.location(reverse('home'))



class TestPasswordChange(object):
    """Tests for change-password view."""
    form_id = 'changepasswordform'
    extra_form_data = {'old_password': 'sekrit'}


    @property
    def url(self):
        """Shortcut for password-change url."""
        return reverse('password_change')


    def test_login_required(self, client, db):
        """Redirects to signup if user is unauthenticated."""
        res = client.get(self.url, status=302)

        assert res['Location'] == utils.location(
            reverse('login') + '?next=' + self.url)


    def test_change_password(self, client, db):
        """Get a confirmation message after changing password."""
        profile = factories.ProfileFactory.create(user__password='sekrit')
        form = client.get(
            self.url, user=profile.user).forms['change-password-form']
        new_password = 'sekrit123'
        form['old_password'] = 'sekrit'
        form['new_password1'] = new_password
        form['new_password2'] = new_password
        res = form.submit(status=302).follow()

        res.mustcontain("Password changed")



class TestPasswordReset(object):
    """Tests for reset-password view."""
    @property
    def url(self):
        """Shortcut for password-reset url."""
        return reverse('password_reset')


    def test_reset_password(self, client, db):
        """Get a confirmation message and reset email."""
        factories.UserFactory.create(email='user@example.com')

        form = client.get(self.url).forms['reset-password-form']
        form['email'] = 'user@example.com'

        res = form.submit(status=302).follow()

        res.mustcontain("Password reset email sent")
        assert len(mail.outbox) == 1
        assert mail.outbox[0].to == ['user@example.com']


    def test_inactive_user(self, client, db):
        """An inactive user can get a password reset email."""
        factories.UserFactory.create(email='user@example.com', is_active=False)

        form = client.get(self.url).forms['reset-password-form']
        form['email'] = 'user@example.com'

        res = form.submit(status=302).follow()

        res.mustcontain("Password reset email sent")
        assert len(mail.outbox) == 1
        assert mail.outbox[0].to == ['user@example.com']


    def test_bad_email(self, client, db):
        """Nonexistent user emails give no clue to an attacker."""
        form = client.get(self.url).forms['reset-password-form']
        form['email'] = 'doesnotexist@example.com'

        res = form.submit(status=302).follow()

        res.mustcontain("Password reset email sent")
        assert len(mail.outbox) == 0



class TestPasswordResetConfirm(object):
    """Tests for reset-password-confirm view."""
    def url(self, client, user):
        """Shortcut for password-reset-confirm url."""
        form = client.get(
            reverse('password_reset')).forms['reset-password-form']
        form['email'] = user.email
        form.submit(status=302)

        for line in mail.outbox[0].body.splitlines():
            if '://' in line:
                return line.strip()

        assert False, "No password reset confirm URL found in reset email."


    def test_reset_password_confirm(self, client, db):
        """Get a confirmation message after resetting password."""
        user = factories.UserFactory.create(
            email='user@example.com', password='sekrit')
        form = client.get(self.url(client, user)).forms['set-password-form']
        new_password = 'sekrit123'
        form['new_password1'] = new_password
        form['new_password2'] = new_password
        res = form.submit(status=302).follow()

        res.mustcontain("Password changed")


    def test_inactive_user_becomes_active(self, client, db):
        """An inactive user who completes a reset becomes active."""
        user = factories.UserFactory.create(
            email='user@example.com', is_active=False)
        form = client.get(self.url(client, user)).forms['set-password-form']
        new_password = 'sekrit123'
        form['new_password1'] = new_password
        form['new_password2'] = new_password
        form.submit(status=302).follow()

        assert utils.refresh(user).is_active



class TestRegister(object):
    """Tests for register view."""
    @property
    def url(self):
        """Shortcut for register url."""
        return reverse('register')


    def test_register(self, client, db):
        """Get logged in and redirected to home after registering."""
        school = factories.SchoolFactory.create()
        form = client.get(self.url).forms['register-form']
        form['name'] = 'Some Body'
        form['email'] = 'some@example.com'
        form['password'] = 'sekrit123'
        form['password_confirm'] = 'sekrit123'
        form['role'] = 'Test User'
        form['school'] = str(school.id)
        res = form.submit(status=302)

        assert res['Location'] == utils.location(reverse('add_group'))

        res.follow(status=200)


    def test_register_failed(self, client, db):
        """Form redisplayed with any errors."""
        school = factories.SchoolFactory.create()
        form = client.get(self.url).forms['register-form']
        form['email'] = 'some@example.com'
        form['password'] = 'sekrit123'
        form['password_confirm'] = 'sekrit123'
        form['role'] = 'Test User'
        form['school'] = str(school.id)
        res = form.submit(status=200)

        res.mustcontain('field is required')



class TestConfirmEmail(object):
    """Tests for confirm_email view."""
    def url(self, client):
        """Shortcut for confirm_email url."""
        school = factories.SchoolFactory.create()
        form = client.get(reverse('register')).forms['register-form']
        form['name'] = 'New Body'
        form['email'] = 'new@example.com'
        form['password'] = 'sekrit123'
        form['password_confirm'] = 'sekrit123'
        form['role'] = 'New Role'
        form['school'] = str(school.id)
        form.submit(status=302)

        for line in mail.outbox[0].body.splitlines():
            if '://' in line:
                return line.strip()

        assert False, "Email-confirm link not found in activation email."


    def test_confirm(self, client, db):
        """Get a confirmation message after activating."""
        res = client.get(self.url(client), status=302).follow()

        res.mustcontain("address new@example.com confirmed")


    def test_failed_confirm(self, client, db):
        """Failed confirm returns a failure message."""
        res = client.get(
            reverse(
                'confirm_email', kwargs={'uidb36': 'foo', 'token': 'foo-bar'})
            )

        res.mustcontain("doesn't seem to be valid")



class TestAcceptEmailInvite(object):
    """Tests for accept-email-invite view."""
    def url(self, client, profile):
        """Shortcut for accept-email-invite url."""
        rel = factories.RelationshipFactory(from_profile=profile)
        response = client.get(
            reverse('invite_teacher', kwargs=dict(student_id=rel.student.id)),
            user=profile.user,
            )
        form = response.forms['invite-teacher-form']
        form['email'] = 'new@example.com'
        form['role'] = 'teacher'
        form.submit(status=302)

        for line in mail.outbox[0].body.splitlines():
            if '://' in line:
                return line.strip()

        assert False, "No invite URL found in invite-elder email."


    def test_accept_email_invite(self, client, db):
        """Accepting email invite sets is_active True."""
        profile = factories.ProfileFactory.create(school_staff=True)
        response = client.get(self.url(client, profile))
        form = response.forms['set-password-form']
        new_password = 'sekrit123'
        form['new_password1'] = new_password
        form['new_password2'] = new_password
        res = form.submit(status=302).follow()
        invitee = auth_models.User.objects.get(email='new@example.com')

        res.mustcontain("chosen a password")
        assert invitee.is_active



class TestEditProfile(object):
    """Tests for edit-profile view."""
    @property
    def url(self):
        """Shortcut for edit-profile view URL."""
        return reverse('edit_profile')


    def test_edit_profile(self, client, db):
        """Can edit profile."""
        profile = factories.ProfileFactory.create()
        form = client.get(self.url, user=profile.user).forms['edit-profile-form']
        form['name'] = 'New Name'
        form['role'] = 'New Role'
        response = form.submit().follow()

        response.mustcontain('saved')
        profile = utils.refresh(profile)
        assert profile.name == u'New Name'
        assert profile.role == u'New Role'


    def test_validation_error(self, client, db):
        profile = factories.ProfileFactory.create()
        form = client.get(self.url, user=profile.user).forms['edit-profile-form']
        form['name'] = 'New Name'
        form['role'] = ''
        response = form.submit(status=200)

        response.mustcontain('field is required')


    def test_login_required(self, client, db):
        """Redirects to signup if user is unauthenticated."""
        res = client.get(self.url, status=302)

        assert res['Location'] == utils.location(
            reverse('login') + '?next=' + self.url)
