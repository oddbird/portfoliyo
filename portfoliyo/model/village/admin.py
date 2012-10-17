from django.contrib import admin

from . import models


admin.site.register(
    models.Post,
    list_display=['__unicode__', 'author', 'student', 'timestamp'],
    )
