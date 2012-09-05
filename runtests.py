#!/usr/bin/env python
"""
Run py.test after setting up DJANGO_SETTINGS_MODULE.

"""
import os
import sys

from _pytest.core import main as pytest_main

def main():
    os.environ["DJANGO_SETTINGS_MODULE"] = "portfoliyo.settings.default"
    args = sys.argv[1:]
    if not args:
        args = ["tests/", "--cov-report", "html", "--cov", "portfoliyo"]
    raise SystemExit(pytest_main(args))


if __name__ == "__main__":
    main()
