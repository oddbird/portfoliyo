from ... import types

from .added_to_village import AddedToVillageCollector
from .bulk_posts import BulkPostCollector
from .new_parent import NewParentCollector
from .new_teacher import NewTeacherCollector
from .posts import PostCollector


COLLECTOR_CLASSES = {
    types.ADDED_TO_VILLAGE: AddedToVillageCollector,
    types.NEW_TEACHER: NewTeacherCollector,
    types.NEW_PARENT: NewParentCollector,
    types.POST: PostCollector,
    types.BULK_POST: BulkPostCollector,
    }
