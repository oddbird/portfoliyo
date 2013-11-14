from django.core.management import BaseCommand, CommandError

from portfoliyo.model.users.bulk import import_from_csv
from portfoliyo.model import Profile



class Command(BaseCommand):
    help = (
        "Import users from a 3-column (name, phone, groups) CSV file. "
        "Separate group names in the third column with ::."
        )
    args = "teacher@example.com filename.csv"


    def handle(self, *args, **options):
        verbosity = int(options.get('verbosity', 1))
        try:
            teacher_email, fn = args
        except ValueError:
            raise CommandError(
                "import_users accepts two args: teacher-email and CSV file.")
        try:
            teacher = Profile.objects.get(user__email=teacher_email)
        except Profile.DoesNotExist:
            raise CommandError(
                "Teacher with email %r not found." % teacher_email)
        if verbosity:
            self.stdout.write("\nLoading %s for %r:\n" % (fn, teacher_email))
        created, found = import_from_csv(teacher, fn)
        if verbosity:
            for p in created:
                self.stdout.write("  Created %s.\n" % p.name)
            for p in found:
                self.stdout.write("  Found %s.\n" % p.name)
