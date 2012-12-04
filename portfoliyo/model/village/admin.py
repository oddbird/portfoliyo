from django.contrib import admin

from . import models


class NoListFilter(admin.SimpleListFilter):
    def lookups(self, request, model_admin):
        return [('0', "None")]



class AuthorFilter(NoListFilter):
    title = "Author"
    parameter_name = "author"


    def queryset(self, request, queryset):
        v = self.value()
        if v == '0':
            return queryset.filter(author__isnull=True)
        elif v:
            return queryset.filter(author=v)



class StudentFilter(NoListFilter):
    title = "Student"
    parameter_name = "student"


    def queryset(self, request, queryset):
        v = self.value()
        if v is not None:
            return queryset.filter(student=v)



class SchoolFilter(NoListFilter):
    title = "School"
    parameter_name = "school"


    def queryset(self, request, queryset):
        v = self.value()
        if v is not None:
            return queryset.filter(student__school=v)


class PostAdmin(admin.ModelAdmin):
    list_display=[
        '__unicode__',
        'linked_author',
        'school',
        'linked_student',
        'teacher_email',
        'linked_timestamp',
        ]
    list_filter=[AuthorFilter, StudentFilter, SchoolFilter]


    def queryset(self, request):
        return super(PostAdmin, self).queryset(request).select_related(
            'author', 'student', 'student__school', 'student__invited_by__user')


    def linked_author(self, post):
        return u'<a href="?author=%s">%s</a>' % (
            post.author_id or 'none', post.author)
    linked_author.short_description = 'author'
    linked_author.allow_tags = True
    linked_author.admin_order_field = 'author'


    def linked_student(self, post):
        return u'<a href="?student=%s">%s</a>' % (
            post.student_id or 'none', post.student)
    linked_student.short_description = 'student'
    linked_student.allow_tags = True
    linked_student.admin_order_field = 'student'


    def linked_timestamp(self, post):
        return u'<a href="%s">%s</a>' % (
            post.get_absolute_url(),
            post.timestamp.strftime('%b. %d, %Y, %I:%M %p'),
            )
    linked_timestamp.short_description = 'timestamp'
    linked_timestamp.allow_tags = True
    linked_timestamp.admin_order_field = 'timestamp'


    def school(self, post):
        return u'<a href="?school=%s">%s</a>' % (
            post.student.school_id, post.student.school)
    school.allow_tags = True
    school.admin_order_field = 'student_school'


    def teacher_email(self, post):
        teacher = post.student.invited_by
        return teacher.user.email if teacher else None
    teacher_email.short_description = 'teacher email'
    teacher_email.admin_order_field = 'student__invited_by'



admin.site.register(models.Post, PostAdmin)
