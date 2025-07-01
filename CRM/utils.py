from .models import Notification

def notify_user(user, message):
    """Simple function to create notifications"""
    Notification.objects.create(user=user, message=message)