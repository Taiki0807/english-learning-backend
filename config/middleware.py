from django.conf import settings


class SameSiteMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        for key in response.cookies.keys():
            if response.cookies.get(key):
                response.cookies[key]["samesite"] = "Lax" if settings.DEBUG else "None"
                response.cookies[key]["secure"] = not settings.DEBUG
        return response
