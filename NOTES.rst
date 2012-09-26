Miscellaneous thoughts on possible future refactorings:

* Profile "state" and "invited_by" fields maybe could be on Relationship
  instead to better support the same parent going through the process multiple
  times with different students.

* portfoliyo/sms/hooks.py may be due for refactoring into something more
  structured than a long series of conditionals.
