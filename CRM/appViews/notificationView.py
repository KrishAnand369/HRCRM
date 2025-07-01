from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from CRM.models import Notification
from CRM.controller import authView

@login_required
def notification_list(request):
    userRole = authView.get_user_role(request.user)
    notifications = Notification.objects.filter(user=request.user)
    return render(request, 'app/webkit/notification/notifications.html', {'notifications': notifications,'userRole' : userRole})

@login_required
def mark_as_read(request, pk):
    notification = Notification.objects.get(pk=pk, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect('CRM:notification_list')

@login_required
def mark_all_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect('CRM:notification_list')