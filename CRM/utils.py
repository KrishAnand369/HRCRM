from .models import Notification

def notify_user(user,url, message):
    """Simple function to create notifications"""
    Notification.objects.create(user=user,url=url, message=message)