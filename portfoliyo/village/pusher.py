from django.conf import settings

def context_processor(request):
    return {"PUSHER_KEY": settings.PUSHER_KEY}
