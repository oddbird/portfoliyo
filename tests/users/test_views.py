"""Tests for user/account views."""
from django.core.urlresolvers import reverse

from tests.users import factories
from tests.utils import patch_session


class TestLogin(object):
    """Tests for login."""
    @property
    def url(self):
        """Shortcut for login url."""
        return reverse("login")


    def test_login(self, client):
        """Successful login redirects."""
        factories.UserFactory.create(
            email="test@example.com", password="sekrit")

        form = client.get(self.url).forms["loginform"]
        form["username"] = "test@example.com"
        form["password"] = "sekrit"
        res = form.submit(status=302)

        assert res["Location"] == "http://testserver/"


    def test_login_failed(self, client):
        """Failed login returns error message."""
        factories.UserFactory.create(
            email="test@example.com", password="sekrit")

        form = client.get(self.url).forms["loginform"]
        form["username"] = "test@example.com"
        form["password"] = "blah"
        res = form.submit(status=200)

        res.mustcontain("Please enter a correct username and password")


    def test_display_captcha(self, client):
        """Sixth login attempt within a minute returns form with captcha."""
        res = client.get(self.url)
        for i in range(6):
            res = res.forms["loginform"].submit()

        form = res.forms["loginform"]

        assert "captcha" in form.fields


    def test_bad_captcha(self, client):
        """Bad value for captcha fails login, even with correct user/pw."""
        factories.UserFactory.create(
            email="test@example.com", password="sekrit")

        session_data = {}

        with patch_session(session_data):
            res = client.get(self.url)
            for i in range(6):
                res = res.forms["loginform"].submit()

            form = res.forms["loginform"]
            answer = session_data["auth_captcha_answer"]
            form["captcha"] = answer + 1 # oops, wrong answer!
            form["username"] = "test"
            form["password"] = "sekrit"
            res = form.submit(status=200)

        res.mustcontain("not the answer we were looking for")


    def test_good_captcha(self, client):
        """Good value for captcha allows login."""
        factories.UserFactory.create(
            email="test@example.com", password="sekrit")

        session_data = {}

        with patch_session(session_data):
            res = client.get(self.url)
            for i in range(6):
                res = res.forms["loginform"].submit()

            form = res.forms["loginform"]
            answer = session_data["auth_captcha_answer"]
            form["captcha"] = answer
            form["username"] = "test@example.com"
            form["password"] = "sekrit"
            res = form.submit(status=302)

        assert res["Location"] == "http://testserver/"
