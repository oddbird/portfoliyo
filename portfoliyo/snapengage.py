from django.conf import settings

def context_processor(request):
    return {
        "SNAPENGAGE_ID": getattr(settings, "SNAPENGAGE_ID", "")}
