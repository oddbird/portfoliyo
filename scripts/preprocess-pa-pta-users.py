"""
Script to transform 6-col CSV provided by PA PTA to 3-col for import_users.

Usage: scripts/preprocess-pta-users.py in.csv

Combines first/last name fields into a single name field.

Combines region field and role field into ::-separated "groups" field.

De-duplicates multiple rows with same name/phone and different roles, adding
all roles to groups field.

Removes extraneous asterisks from all fields.

Only processes users with a valid (10-digit) phone number.

Reports any unprocessable users to stderr.

Send output CSV to stdout.

"""
