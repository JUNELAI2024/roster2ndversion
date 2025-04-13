from django.utils.timezone import now
from .models import AccessLog

class AccessLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated:
            AccessLog.objects.create(
                user=request.user,
                timestamp=now(),
                page=request.path
            )

        return response