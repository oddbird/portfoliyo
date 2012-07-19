Portfoliyo
==========

Development
-----------

If you want to run this project in a `virtualenv`_ to isolate it from
other Python projects on your system, create a virtualenv and activate
it.  Then run ``bin/install-reqs`` to install the dependencies for this
project into your Python environment.

You may need to create a ``portfoliyo/settings/local.py`` file with some
details of your local configuration.  See
``portfoliyo/settings/local.sample.py`` for a sample that can be copied to
``portfoliyo/settings/local.py`` and modified.

Once this configuration is done, you should be able to run ``./manage.py
syncdb --migrate``, then ``./manage.py runserver`` and access the site
in your browser at ``http://localhost:8000``.

.. _virtualenv: http://www.virtualenv.org

To install the necessary Ruby gems for Compass/Sass development (only
necessary if you plan to modify Sass files and re-generate CSS), install
Bundler (``gem install bundler``) and then run ``bundle install``.

Deployment
----------

In addition to the above configuration, in any production deployment
this entire app should be served exclusively over HTTPS (since serving
authenticated pages over HTTP invites session hijacking
attacks). Ideally, the non-HTTP URLs should redirect to the HTTPS
version.

``portfoliyo/settings/prod.py`` should be used as the settings module in a
production deployment in place of ``portfoliyo/settings/default.py`` (set
``DJANGO_SETTINGS_MODULE=portfoliyo.settings.prod``). Site-specific overrides
can still be placed in ``portfoliyo/settings/local.py``.

You can run ``./manage.py checksecure`` to verify that settings are correctly
configured for a secure deployment.

This app also uses the `staticfiles contrib app`_ in Django for
collecting static assets from reusable components into a single
directory for production serving.  Under "runserver" in development this
is handled automatically.  In production, run ``./manage.py
collectstatic`` to collect all static assets into the
``collected-assets`` directory (or whatever ``STATIC_ROOT`` is set to in
``settings_local.py``), and make those collected assets available by
HTTP at the ``STATIC_URL`` setting.

.. _staticfiles contrib app: http://docs.djangoproject.com/en/1.4/howto/static-files/
