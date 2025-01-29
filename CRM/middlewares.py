from django.utils.functional import SimpleLazyObject
from django.contrib.auth.models import AnonymousUser

def get_profile_pic(request):
    if request.user.is_authenticated and not isinstance(request.user, AnonymousUser):
        try:
            return request.user.profile.profile_pic.url if request.user.profile.profile_pic else None
        except Exception:
            return None
    return None

class ProfilePicMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.profile_pic_url = SimpleLazyObject(lambda: get_profile_pic(request))
        response = self.get_response(request)
        return response
