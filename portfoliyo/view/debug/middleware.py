import debug_toolbar.middleware
import debug_toolbar.urls



class DebugToolbarMiddleware(debug_toolbar.middleware.DebugToolbarMiddleware):
    """Avoid conflict with AjaxMessagesMiddleware."""
    def process_response(self, request, response):
        response = super(DebugToolbarMiddleware, self).process_response(
            request, response)
        if request.path.lstrip('/').startswith(debug_toolbar.urls._PREFIX):
            response.no_messages = True
        return response
