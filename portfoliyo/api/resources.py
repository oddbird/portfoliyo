"""Portfoliyo API resources."""
from tastypie import constants, fields
from tastypie.authentication import SessionAuthentication
from tastypie.authorization import ReadOnlyAuthorization
from tastypie.resources import ModelResource

from portfoliyo import model


class PortfoliyoResource(ModelResource):
    """Common default values for all resources."""
    class Meta:
        authentication = SessionAuthentication()
        authorization = ReadOnlyAuthorization()
        allowed_methods = ['get']



class ProfileResource(PortfoliyoResource):
    invited_by = fields.ForeignKey('self', 'invited_by', blank=True, null=True)
    email = fields.CharField()


    def dehydrate_email(self, bundle):
        return bundle.obj.user.email


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
            ]
        filtering = {
            'school_staff': constants.ALL,
            }



class GroupResource(PortfoliyoResource):
    owner = fields.ForeignKey(ProfileResource, 'owner')
    members = fields.ManyToManyField(ProfileResource, 'members')


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
