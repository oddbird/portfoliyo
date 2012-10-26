"""API Authorization."""
from tastypie import authorization, http


def forbidden(method):
    return http.HttpForbidden(
        "You are not authorized to %s this resource." % method)



class PortfoliyoAuthorization(authorization.Authorization):
    """Implements Portfoliyo API authorization."""
    def is_authorized(self, request, object=None):
        # GET requests permitted for any user
        if request.method == 'GET':
            return True
        return forbidden(request.method)



class RelationshipAuthorization(PortfoliyoAuthorization):
    def is_authorized(self, request, object=None):
        """Allow changes by the elder of the relationship."""
        if (object and object.from_profile_id == request.user.profile.id):
            return True
        return super(RelationshipAuthorization, self).is_authorized(
            request, object)


    def apply_limits(self, request, object_list):
        """Only allow users to see their own relationships."""
        return object_list.filter(from_profile=request.user.profile)



class ProfileAuthorization(PortfoliyoAuthorization):
    """Only allow users to see same-school profiles."""
    def apply_limits(self, request, object_list):
        """Only allow users to see same-school profiles."""
        return object_list.filter(school=request.user.profile.school_id)



class GroupAuthorization(PortfoliyoAuthorization):
    def is_authorized(self, request, object=None):
        """Allow changes only if you own the Group."""
        if (object and object.owner_id == request.user.profile.id):
            return True
        return super(GroupAuthorization, self).is_authorized(request, object)


    def apply_limits(self, request, object_list):
        """Only allow users to see their own groups."""
        return object_list.filter(owner=request.user.profile)
