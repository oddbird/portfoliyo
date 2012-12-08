from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import int_to_base36
from django.utils.crypto import salted_hmac



class EmailConfirmTokenGenerator(PasswordResetTokenGenerator):
    def _make_token_with_timestamp(self, user, timestamp):
        # timestamp is number of days since 2001-1-1.  Converted to
        # base 36, this gives us a 3 digit string until about 2121
        ts_b36 = int_to_base36(timestamp)


        # We limit the hash to 20 chars to keep URL short
        key_salt = "portfoliyo.view.users.tokens.EmailConfirmTokenGenerator"

        # By hashing on user ID and email, we ensure this token can only ever
        # be used to confirm this email address for this user.
        value = (unicode(user.id) + user.email + unicode(timestamp))
        hash = salted_hmac(key_salt, value).hexdigest()[::2]
        return "%s-%s" % (ts_b36, hash)
