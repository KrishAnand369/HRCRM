def profile_pic_processor(request):
    if request.user.is_authenticated:
        try:
            profile_pic_url = request.user.profile.profile_pic.url if request.user.profile.profile_pic else '/static/images/default.jpg'
        except Exception:
            profile_pic_url = '/static/images/default.jpg'
        return {'profile_pic_url': profile_pic_url}
    return {'profile_pic_url': '/static/images/default.jpg'}

from .models import Notification

def notification_context(request):
    if request.user.is_authenticated:
        return {
            'unread_count': Notification.objects.filter(user=request.user, is_read=False).count(),
            'recent_notifications': Notification.objects.filter(user=request.user).order_by('-created_at')[:5]
        }
    return {}
