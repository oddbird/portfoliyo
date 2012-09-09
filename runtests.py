#!/usr/bin/env python
"""
Run py.test after setting up DJANGO_SETTINGS_MODULE.

"""
import os
import sys

from _pytest.core import main as pytest_main

def main():
    os.environ["DJANGO_SETTINGS_MODULE"] = "portfoliyo.settings.default"

    # Override pytest-django and run South migrations in tests
    from pytest_django import plugin
    def _enable_migrations_in_tests():
        from south.management.commands import patch_for_test_db_setup
        patch_for_test_db_setup()
    plugin._disable_south_management_command = _enable_migrations_in_tests


    args = sys.argv[1:]
    if not args:
        args = ["tests/", "--cov-report", "html", "--cov", "portfoliyo"]
    raise SystemExit(pytest_main(args))


if __name__ == "__main__":
    main()
