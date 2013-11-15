import csv
import urllib

from django.conf import settings

from portfoliyo.model import Profile, Group, Relationship
from portfoliyo import xact


@xact.xact
def import_from_csv(teacher, fn, source_phone=None):
    """
    Import users from a CSV file and associate with given teacher.

    Both Student and Parent profiles are created for each imported user, both
    with the same name.

    The first three columns of the CSV file must be name, phone, and
    groups. All other columns are ignored. The groups column may contain
    multiple group names separated by "::".

    If a student with a matching name already exists within this teacher's
    account, that student's groups will not be modified. Similarly, if a parent
    with matching phone is already attached to that student, that parent's
    source-phone will not be modified.

    Optionally sets source-phone for all created users to given number.

    Return a tuple of two lists, (created_profiles, found_profiles).

    """
    if '://' in fn:
        fh = urllib.urlopen(fn)
    else:
        fh = open(fn, 'rb')
    source_phone = source_phone or settings.DEFAULT_NUMBER
    created = []
    found = []

    groups_by_name = {}
    def get_group(group_name):
        if group_name not in groups_by_name:
            groups_by_name[group_name], created = Group.objects.get_or_create(
                name=group_name, owner=teacher)
        return groups_by_name[group_name]

    try:
        reader = csv.reader(fh)
        for row in reader:
            name, phone, groups = [i.strip() for i in row[:3]]

            try:
                student_rel = Relationship.objects.get(
                    from_profile=teacher, to_profile__name=name)
            except Relationship.DoesNotExist:
                student = Profile.create_with_user(
                    name=name, school=teacher.school, invited_by=teacher)
                student_rel = Relationship.objects.create(
                    from_profile=teacher,
                    to_profile=student,
                    level=Relationship.LEVEL.owner,
                    )
                for group_name in groups.split('::'):
                    group = get_group(group_name)
                    group.students.add(student)

            try:
                parent_rel = Relationship.objects.get(
                    from_profile__phone=phone,
                    from_profile__name=name,
                    to_profile=student_rel.to_profile,
                    )
                found.append(parent_rel.from_profile)
            except Relationship.DoesNotExist:
                parent = Profile.create_with_user(
                    name=name,
                    phone=phone,
                    school=teacher.school,
                    invited_by=teacher,
                    is_active=True,
                    source_phone=source_phone,
                    )
                parent_rel = Relationship.objects.create(
                    from_profile=parent,
                    to_profile=student_rel.to_profile,
                    )
                created.append(parent)
    finally:
        fh.close()

    return created, found
