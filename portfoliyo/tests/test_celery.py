"""Tests for our transactional Celery behavior."""
import pytest

from portfoliyo import celery, tasks, xact
from portfoliyo.tests import factories



class TestTransactionTask(object):
    def test_tasks_run_after_transaction(self, sms):
        """Task is not applied until after transaction-in-progress commits."""
        # If we actually touched the database in this test, we would need the
        # `transactional_db` fixture; but we don't, so we avoid the slowdown.
        with xact.xact():
            tasks.send_sms.delay('+15555555555', 'something')
            assert len(sms.outbox) == 0

        assert len(sms.outbox) == 1



    def test_tasks_discarded_if_transaction_rolled_back(self, sms):
        """If transaction is rolled back, pending tasks are discarded."""
        class TestException(Exception):
            pass
        try:
            with xact.xact():
                tasks.send_sms.delay('+15555555555', 'something')
                # exception causes transaction to be rolled back
                raise TestException()
        except TestException:
            pass

        # task was discarded because transaction was rolled back
        assert len(sms.outbox) == 0



class TestModelReference(object):
    def test_from_instance(self, db):
        """Can flatten a model instance into a reference."""
        u = factories.UserFactory.create()

        mr = celery.ModelReference.from_instance(u)

        assert mr.app_label == 'auth'
        assert mr.model_name == 'user'
        assert mr.pk == u.pk


    def test_from_instance_not_model(self):
        """A non-model arg to from_instance is returned as-is."""
        assert celery.ModelReference.from_instance(3) == 3


    def test_from_instance_list(self, db):
        """A list of model instances are converted to references."""
        l = [factories.UserFactory.create(), factories.UserFactory.create()]

        mrl = celery.ModelReference.from_instance(l)

        assert [mr.app_label for mr in mrl] == ['auth' for u in l]
        assert [mr.model_name for mr in mrl] == ['user' for u in l]
        assert [mr.pk for mr in mrl] == [u.pk for u in l]


    def test_dereference(self, db):
        """A model-reference can be de-referenced to an instance."""
        u = factories.UserFactory.create()
        mr = celery.ModelReference('auth', 'user', u.pk)

        assert celery.ModelReference.dereference(mr) == u


    def test_dereference_list(self, db):
        """A list of model references can be de-referenced as well."""
        l = [factories.UserFactory.create(), factories.UserFactory.create()]
        mrl = [celery.ModelReference('auth', 'user', u.pk) for u in l]

        assert celery.ModelReference.dereference(mrl) == l


    def test_dereference_other(self):
        """Trying to dereference a non-reference just returns it."""
        assert celery.ModelReference.dereference(3) == 3


    def test_dereference_bad_model_class(self):
        """If model class cannot be found, raises DereferenceFailed."""
        bad_mr = celery.ModelReference('no', 'such', 'class')
        with pytest.raises(celery.DereferenceFailed):
            celery.ModelReference.dereference(bad_mr)


    def test_dereference_missing_pk(self, db):
        """If model instance cannot be found, raises DereferenceFailed."""
        bad_mr = celery.ModelReference('auth', 'user', -1)
        with pytest.raises(celery.DereferenceFailed):
            celery.ModelReference.dereference(bad_mr)


    def test_cache_update(self, db):
        """If given cache dict, will store dereferenced instances in it."""
        u = factories.UserFactory.create()
        mr = celery.ModelReference('auth', 'user', u.pk)
        cache = {}

        assert celery.ModelReference.dereference(mr, cache) == u
        assert cache[('auth', 'user', u.pk)] == u


    def test_cache_lookup(self):
        """If given cache dict, will look up instances there first."""
        # This test does not take the db fixture, thus will fail if it actually
        # tries to access the database.
        mr = celery.ModelReference('auth', 'user', -1)
        cache = {('auth', 'user', -1): 'foo!'}

        assert celery.ModelReference.dereference(mr, cache) == 'foo!'



class TestModelTask(object):
    def test_dereference_fails(self):
        """If dereferencing fails, skips task execution and returns None."""
        bad_mr = celery.ModelReference('no', 'such', 'class')
        mt = celery.ModelTask()

        assert mt(bad_mr) is None
