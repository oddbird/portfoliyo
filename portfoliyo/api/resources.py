"""Portfoliyo API resources."""
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from tastypie import constants, fields
from tastypie.authorization import ReadOnlyAuthorization
from tastypie.bundle import Bundle
from tastypie.exceptions import NotFound
from tastypie.resources import ModelResource

from portfoliyo.api.authentication import SessionAuthentication
from portfoliyo.api.authorization import (
    ProfileAuthorization, RelationshipAuthorization, GroupAuthorization)
from portfoliyo import model


class PortfoliyoResource(ModelResource):
    """
    Common default values for all resources.

    Also supports per-row authorization, for detail requests only, in the
    simplest way possible without switching to this incomplete branch of
    Tastypie:
    https://github.com/toastdriven/django-tastypie/compare/master...perms

    This implementation assumes that all action methods (e.g. get_detail,
    post_list, etc) will all eventually call obj_get_list/cached_obj_get_list
    or obj_get/cached_obj_get at least once passing the request object. It also
    assumes the authorization check is cheap enough that it's ok to potentially
    perform the authorization check twice in case of a cache miss when used a
    cached_* method.

    """
    class Meta:
        authentication = SessionAuthentication()
        authorization = ReadOnlyAuthorization()
        allowed_methods = ['get']
        # @@@ this should be high enough to never cause pagination in our use
        # cases, but we should have a better solution here than a magic number
        # (like maybe a custom paginator class that doesn't paginate?)
        limit = 200


    def wrap_view(self, view):
        """Undo csrf-exempt on view wrapper; we want session-csrf to run."""
        wrapper = super(PortfoliyoResource, self).wrap_view(view)
        wrapper.csrf_exempt = False
        return wrapper


    def is_authorized(self, request, object=None):
        """Neuter built-in to avoid failure when dispatch calls it w/o obj."""
        pass


    def real_is_authorized(self, request, object=None):
        """Provide real is_authorized method under different name."""
        return super(PortfoliyoResource, self).is_authorized(request, object)


    def cached_obj_get_list(self, request=None, **kwargs):
        """Get the object list (maybe from cache), then verify authorization."""
        objs = super(PortfoliyoResource, self).cached_obj_get_list(
            request, **kwargs)
        if request is not None: # pragma: no cover
            self.real_is_authorized(request)
        return objs


    def obj_get_list(self, request=None, **kwargs):
        """Get the object list, then verify authorization."""
        objs = super(PortfoliyoResource, self).obj_get_list(request, **kwargs)
        if request is not None: # pragma: no cover
            self.real_is_authorized(request)
        return objs


    def cached_obj_get(self, request=None, **kwargs):
        """Get the object (perhaps from cache) then verify authorization."""
        obj = super(PortfoliyoResource, self).cached_obj_get(request, **kwargs)
        if request is not None: # pragma: no cover
            self.real_is_authorized(request, obj)
        return obj


    def obj_get(self, request=None, **kwargs):
        """Get the object, then verify authorization."""
        obj = super(PortfoliyoResource, self).obj_get(request, **kwargs)
        if request is not None: # pragma: no cover
            self.real_is_authorized(request, obj)
        return obj


    def obj_delete_list(self, request, **kwargs):
        """
        Add filtering support to TastyPie's delete_list.

        Parent implementation has request optional; making it required until I
        hit a case where it needs to be optional.

        """
        filters = request.GET.copy()

        # Update with the provided kwargs.
        filters.update(kwargs)
        applicable_filters = self.build_filters(filters=filters)

        base_object_list = self.get_object_list(request).filter(
            **applicable_filters)
        authed_object_list = self.apply_authorization_limits(
            request, base_object_list)

        # parent impl has support here for iterables that aren't querysets;
        # leaving that out here until I know why I'd need it.
        authed_object_list.delete()



class SimpleToManyField(fields.ToManyField):
    """A to-many field that operates off a simple list-returning property."""
    def dehydrate(self, bundle):
        related = getattr(bundle.obj, self.attribute)

        dehydrated = []

        for obj in related:
            resource = self.get_related_resource(obj)
            related_bundle = Bundle(obj=obj, request=bundle.request)
            dehydrated.append(self.dehydrate_related(related_bundle, resource))

        return dehydrated



class SlimProfileResource(PortfoliyoResource):
    invited_by = fields.ForeignKey('self', 'invited_by', blank=True, null=True)
    email = fields.CharField()


    class Meta(PortfoliyoResource.Meta):
        queryset = model.Profile.objects.select_related('user').order_by('name')
        resource_name = 'user'
        fields = [
            'id',
            'name',
            'email',
            'phone',
            'role',
            'school_staff',
            'code',
            'invited_by',
            'declined',
            ]
        filtering = {
            'school_staff': constants.ALL,
            }
        authorization = ProfileAuthorization()


    def dehydrate_email(self, bundle):
        return bundle.obj.user.email


    def build_filters(self, filters=None):
        filters = filters or {}

        elders = filters.pop('elders', None)
        students = filters.pop('students', None)
        student_in_groups = filters.pop('student_in_groups', None)
        elder_in_groups = filters.pop('elder_in_groups', None)

        orm_filters = super(SlimProfileResource, self).build_filters(filters)

        if elders:
            orm_filters['relationships_to__from_profile__in'] = elders
        if students:
            orm_filters['relationships_from__to_profile__in'] = students
        if student_in_groups:
            orm_filters['student_in_groups__in'] = student_in_groups
        if elder_in_groups:
            orm_filters['elder_in_groups__in'] = elder_in_groups

        return orm_filters


    def dehydrate(self, bundle):
        bundle.data['village_uri'] = reverse(
            'village',
            kwargs={'student_id': bundle.obj.id},
            )
        bundle.data['edit_student_uri'] = reverse(
            'edit_student',
            kwargs={'student_id': bundle.obj.id},
            )
        user = getattr(bundle.request, 'user', None)
        if user is not None:
            bundle.data['unread_count'] = model.unread.unread_count(
                bundle.obj, user.profile)
        return bundle



class ProfileResource(SlimProfileResource):
    elders = SimpleToManyField('self', 'elders')
    students = SimpleToManyField('self', 'students')


    class Meta(SlimProfileResource.Meta):
        queryset = SlimProfileResource.Meta.queryset.prefetch_related(
            'relationships_from', 'relationships_to')



class ElderRelationshipResource(PortfoliyoResource):
    elder = fields.ForeignKey(SlimProfileResource, 'from_profile', full=True)
    student = fields.ForeignKey(SlimProfileResource, 'to_profile', full=True)
    relationship = fields.CharField('description_or_role')


    class Meta(PortfoliyoResource.Meta):
        queryset = model.Relationship.objects.filter(
            kind=model.Relationship.KIND.elder).select_related(
            'from_profile', 'to_profile')
        resource_name = 'relationship'
        fields = ['id', 'elder', 'student', 'relationship']
        filtering = {
            'elder': ['exact'],
            'student': ['exact'],
            }
        authorization = RelationshipAuthorization()
        allowed_methods = ['get', 'delete']


    def obj_delete(self, request=None, **kwargs):
        """Deleting relationship also removes that student from your groups."""
        obj = kwargs.pop('_obj', None)

        if not hasattr(obj, 'save'): # pragma: no cover
            try:
                obj = self.obj_get(request, **kwargs)
            except ObjectDoesNotExist:
                raise NotFound(
                    "A model instance matching the provided arguments "
                    "could not be found."
                    )

        model.Group.students.through.objects.filter(
            group__owner=obj.elder, profile=obj.student).delete()

        obj.delete()




class GroupResource(PortfoliyoResource):
    owner = fields.ForeignKey(ProfileResource, 'owner')
    students = fields.ToManyField(SlimProfileResource, 'students', full=True)


    class Meta(PortfoliyoResource.Meta):
        queryset = model.Group.objects.order_by(
            'name').prefetch_related('students')
        resource_name = 'group'
        fields = ['id', 'name', 'owner', 'students']
        authorization = GroupAuthorization()
        detail_allowed_methods = ['get', 'delete']


    def full_dehydrate(self, bundle):
        """Special handling for all-students group."""
        if bundle.obj.is_all:
            profile_resource = SlimProfileResource()
            def dehydrate_student(student):
                b = profile_resource.build_bundle(
                    obj=student, request=bundle.request)
                return profile_resource.full_dehydrate(b)
            bundle.data.update({
                    'id': bundle.obj.id,
                    'name': bundle.obj.name,
                    'students_uri': reverse(
                        'api_dispatch_list',
                        kwargs={'resource_name': 'user', 'api_name': 'v1'},
                        ) + '?elders=%s' % bundle.obj.owner.id,
                    'group_uri': reverse('all_students'),
                    'add_student_uri': reverse('add_student'),
                    'owner': reverse(
                        'api_dispatch_detail',
                        kwargs={
                            'resource_name': 'user',
                            'api_name': 'v1',
                            'pk': bundle.obj.owner.id,
                            },
                        ),
                    'unread_count': sum(
                        [
                            model.unread.unread_count(s, bundle.obj.owner)
                            for s in bundle.obj.owner.students
                            ]
                        ),
                    'students': [
                        dehydrate_student(s) for s in bundle.obj.owner.students
                        ],
                    })
        else:
            bundle = super(GroupResource, self).full_dehydrate(bundle)
        return bundle


    def dehydrate(self, bundle):
        bundle.data['students_uri'] = reverse(
            'api_dispatch_list',
            kwargs={'resource_name': 'user', 'api_name': 'v1'},
            ) + '?student_in_groups=' + str(bundle.obj.id)
        bundle.data['group_uri'] = reverse(
            'group',
            kwargs={'group_id': bundle.obj.id},
            )
        bundle.data['edit_uri'] = reverse(
            'edit_group',
            kwargs={'group_id': bundle.obj.id},
            )
        bundle.data['add_student_uri'] = reverse(
            'add_student_in_group', kwargs={'group_id': bundle.obj.id})
        user = getattr(bundle.request, 'user', None)
        if user is not None:
            bundle.data['unread_count'] = model.unread.group_unread_count(
                bundle.obj, bundle.request.user.profile)
        return bundle


    def obj_get_list(self, request=None, **kwargs):
        qs = super(GroupResource, self).obj_get_list(request, **kwargs)
        groups = list(qs)
        if request is not None: # pragma: no cover
            groups.insert(0, model.AllStudentsGroup(request.user.profile))
        return groups



class PostResource(PortfoliyoResource):
    author = fields.ForeignKey(ProfileResource, 'author', blank=True, null=True)
    student = fields.ForeignKey(ProfileResource, 'student')


    class Meta(PortfoliyoResource.Meta):
        queryset = model.Post.objects.all()
        resource_name = 'post'
        fields = [
            'id',
            'author',
            'timestamp',
            'student',
            'original_text',
            'html_text',
            'to_sms',
            'from_sms',
            ]
        filtering = {
            'author': ['exact'],
            'student': ['exact'],
            }


    def dehydrate(self, bundle):
        bundle.data['unread'] = model.unread.is_unread(
            bundle.obj, bundle.request.user.profile)
        return bundle
