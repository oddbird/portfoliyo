"""API Authorization."""
from tastypie import authorization, http


def forbidden(method):
    return http.HttpForbidden(
        "You are not authorized to %s this resource." % method)



class PortfoliyoAuthorization(authorization.Authorization):
    """Implements Portfoliyo API authorization."""
    def is_authorized(self, request, object=None):
        # GET requests permitted for any authenticated users
        if request.method == 'GET' and request.user.profile.school_staff:
            return True
        return forbidden(request.method)



class ProfileAuthorization(PortfoliyoAuthorization):
    def is_authorized(self, request, object=None):
        """Allow changes by same-school staff."""
        if (object and object.school_id == request.user.profile.school_id and
                request.user.profile.school_staff):
            return True
        return super(ProfileAuthorization, self).is_authorized(request, object)


    def apply_limits(self, request, object_list):
        """Only allow users to see same-school profiles."""
        return object_list.filter(school=request.user.profile.school_id)



class GroupAuthorization(PortfoliyoAuthorization):
    def is_authorized(self, request, object=None):
        """Allow changes only if you own the Group."""
        if (object and object.owner_id == request.user.profile.id and
                request.user.profile.school_staff):
            return True
        return super(GroupAuthorization, self).is_authorized(request, object)


    def apply_limits(self, request, object_list):
        """Only allow users to see same-school profiles."""
        return object_list.filter(owner=request.user.profile)
