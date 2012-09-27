"""Portfoliyo API resources."""
from django.core.urlresolvers import reverse
from tastypie import constants, fields
from tastypie.authentication import SessionAuthentication
from tastypie.authorization import ReadOnlyAuthorization
from tastypie.bundle import Bundle
from tastypie.resources import ModelResource

from portfoliyo import model


class PortfoliyoResource(ModelResource):
    """Common default values for all resources."""
    class Meta:
        authentication = SessionAuthentication()
        authorization = ReadOnlyAuthorization()
        allowed_methods = ['get']



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




class ProfileResource(PortfoliyoResource):
    invited_by = fields.ForeignKey('self', 'invited_by', blank=True, null=True)
    elders = SimpleToManyField('self', 'elders')
    students = SimpleToManyField('self', 'students')
    email = fields.CharField()


    def dehydrate_email(self, bundle):
        return bundle.obj.user.email


    def build_filters(self, filters=None):
        filters = filters or {}

        elders = filters.pop('elders', None)
        students = filters.pop('students', None)
        groups = filters.pop('groups', None)

        orm_filters = super(ProfileResource, self).build_filters(filters)

        if elders:
            orm_filters['relationships_to__from_profile__in'] = elders
        if students:
            orm_filters['relationships_from__to_profile__in'] = students
        if groups:
            orm_filters['in_groups__in'] = groups

        return orm_filters


    class Meta(PortfoliyoResource.Meta):
        queryset = (
            model.Profile.objects.filter(deleted=False).select_related('user'))
        resource_name = 'user'
        fields = [
            'name',
            'email',
            'phone',
            'role',
            'school_staff',
            'code',
            'invited_by',
            'declined',
            'elders',
            'students',
            ]
        filtering = {
            'school_staff': constants.ALL,
            }



class ElderRelationshipResource(PortfoliyoResource):
    elder = fields.ForeignKey(ProfileResource, 'from_profile', full=True)
    student = fields.ForeignKey(ProfileResource, 'to_profile', full=True)
    relationship = fields.CharField('description_or_role')


    class Meta(PortfoliyoResource.Meta):
        queryset = model.Relationship.objects.filter(
            kind=model.Relationship.KIND.elder).select_related(
            'from_profile', 'to_profile')
        resource_name = 'relationship'
        fields = ['elder', 'student', 'relationship']
        filtering = {
            'elder': ['exact'],
            'student': ['exact'],
            }



class GroupResource(PortfoliyoResource):
    owner = fields.ForeignKey(ProfileResource, 'owner')
    members = fields.ManyToManyField(ProfileResource, 'members')


    def dehydrate(self, bundle):
        bundle.data['members_uri'] = reverse(
            'api_dispatch_list',
            kwargs={'resource_name': 'user', 'api_name': 'v1'},
            ) + '?groups=' + str(bundle.obj.id)

        return bundle


    class Meta(PortfoliyoResource.Meta):
        queryset = model.Group.objects.all()
        resource_name = 'group'
        fields = ['name', 'owner', 'members']
        filtering = {
            'owner': ['exact'],
            }



class PostResource(PortfoliyoResource):
    author = fields.ForeignKey(ProfileResource, 'author', blank=True, null=True)
    student = fields.ForeignKey(ProfileResource, 'student')


    class Meta(PortfoliyoResource.Meta):
        queryset = model.Post.objects.all()
        resource_name = 'post'
        fields = [
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
