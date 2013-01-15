"""Collecting, re-hydrating, and aggregating notifications."""



class Village(object):
    """Encapsulates some event involving a single teacher & a single village."""
    def __init__(self, teacher, student):
        self.teacher = teacher
        self.student = student



class VillageList(object):
    """Provides summary data about a list of ``Village`` instances."""
    def __init__(self, villages):
        self.villages = villages

        self.teachers = set()
        self.teachers_by_student = {}
        self.students = set()
        self.students_by_teacher = {}

        for v in self.villages:
            self.teachers.add(v.teacher)
            self.students.add(v.student)
            self.teachers_by_student.setdefault(v.student, set()).add(v.teacher)
            self.students_by_teacher.setdefault(v.teacher, set()).add(v.student)


    def __iter__(self):
        return iter(self.villages)



class RehydrationFailed(Exception):
    pass



class NotificationTypeCollector(object):
    """
    Base class for collections of notifications of the same type.

    Encapsulates the logic for re-hydrating data for each individual
    notification (querying the database to convert the database IDs stored in
    Redis into model instances), and aggregating a set of independent
    notifications of the same type (e.g. "Teacher 1 added you to Student X's
    village", "Teacher 2 added you to Student Y's village") into an object that
    allows for the necessary summary renderings in the actual notification
    email (e.g. "Two teachers added you to 2 new student villages").

    """
    # these should be overridden by subclasses
    #  notification type this class aggregates (constant from types module)
    type_name = None
    #  name of template for email subject if this is only notification type
    subject_template = None
    #  mapping of source data ID keys to lookup model and hydrated data key
    db_lookup = {}


    """Base class for notification types."""
    def __init__(self):
        self.notifications = []


    def __nonzero__(self):
        return bool(self.notifications)


    def add(self, data):
        """
        Rehydrate given notification data and add to internal list.

        If rehydration fails (``hydrate`` method raises ``RehydrationFailed``),
        don't add anything and return ``False``.

        """
        try:
            self.notifications.append(self.hydrate(data))
        except RehydrationFailed:
            return False
        return True


    def hydrate(self, data):
        """
        Rehydrate given notification data.

        Rehydrating means to take any database object IDs in the given
        notification data, and query for the actual database objects needed.

        If any needed objects aren't found (as defined in the ``db_lookup``
        class attribute, which maps a key in the source ``data`` to a tuple of
        model class and key for the hydrated data), raise
        ``RehydrationFailed``.

        """
        hydrated = {}
        for src_key, (model_class, dest_key) in self.db_lookup.items():
            try:
                hydrated[dest_key] = model_class.objects.get(pk=data[src_key])
            except (KeyError, model_class.DoesNotExist):
                raise RehydrationFailed()

        return hydrated


    def get_context(self):
        """Get template context for this notification type."""
        return {}


    def get_students(self):
        return [n['student'] for n in self.notifications if 'student' in n]
