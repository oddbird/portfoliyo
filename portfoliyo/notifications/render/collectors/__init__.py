from ... import types

from .added_to_village import AddedToVillageCollector
from .new_teacher import NewTeacherCollector


COLLECTOR_CLASSES = {
    types.ADDED_TO_VILLAGE: AddedToVillageCollector,
    types.NEW_TEACHER: NewTeacherCollector,
    }
