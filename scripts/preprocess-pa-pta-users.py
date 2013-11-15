#!/usr/bin/env python
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
import csv
import os
import sys



def clean(val):
    """Remove asterisks and trim whitespace."""
    val = val.replace('*', '')
    val = val.strip()
    return val



def main(fn):
    from portfoliyo.formats import normalize_phone
    with open(fn, 'rb') as fh:
        reader = csv.reader(fh)
        names_by_phone = {}
        # maps (name, phone) to full person data
        people = {}
        for row in reader:
            first, last, region, phone, email, role = map(clean, row[:6])
            name = '%s %s' % (first, last)
            validated_phone = normalize_phone(phone)
            if validated_phone is None:
                sys.stderr.write(
                    "%s, %s\n" % (name, phone))
                continue
            if phone in names_by_phone and names_by_phone[phone] != name:
                sys.stderr.write(
                    'Name mismatch: %s vs %s\n' % (name, names_by_phone[phone]))
                continue
            names_by_phone[phone] = name
            groups = {"Region %s" % region, role}
            uid = (name, validated_phone)
            if uid in people:
                people[uid]['groups'].update(groups)
            else:
                people[uid] = {
                    'name': name, 'phone': validated_phone, 'groups': groups}

    writer = csv.DictWriter(sys.stdout, ['name', 'phone', 'groups'])
    for row in people.values():
        row['groups'] = '::'.join(row['groups'])
        writer.writerow(row)


if __name__ == '__main__':
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.environ.setdefault(
        'DJANGO_SETTINGS_MODULE', 'portfoliyo.settings.default')
    main(sys.argv[1])
