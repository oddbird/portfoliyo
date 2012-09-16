from django.conf import settings

def context_processor(request):
    return {
        "USERVOICE_ID": getattr(settings, "USERVOICE_ID", "")}
