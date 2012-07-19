#!/usr/bin/env python
"""
Runs a Django management command.

"""
import os, sys


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "portfoliyo.settings.default")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
