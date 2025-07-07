from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from CRM.models import Event,UserProfile
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from CRM.controller import authView
from django.db.models import Q

@login_required
def calendar_view(request):
    return render(request, 'app/webkit/Event/event.html',{'userRole': authView.get_user_role(request.user),
        'profile': UserProfile.objects.get(user=request.user),})

@login_required
def all_events(request):
    if request.user.is_staff:
        events = Event.objects.filter(Q(is_global=True) | Q(created_by=request.user))
    else:
        events = Event.objects.filter(Q(is_global=True) | Q(user=request.user))
    
    event_list = []
    for event in events:
        event_list.append({
            'id': event.id,
            'title': event.title,
            'start': event.start_time.strftime("%Y-%m-%dT%H:%M:%S"),
            'end': event.end_time.strftime("%Y-%m-%dT%H:%M:%S"),
            'color': event.event_color,
            'description': event.description,
        })
    
    return JsonResponse(event_list, safe=False)

@csrf_exempt
@login_required
def add_event(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            event = Event(
                title=data.get('title'),
                description=data.get('description', ''),
                start_time=data.get('start_time'),
                end_time=data.get('end_time'),
                created_by=request.user
            )
            
            if request.user.is_staff and data.get('is_global', False):
                event.is_global = True
            else:
                event.user = request.user
            
            event.save()
            
            return JsonResponse({'status': 'success', 'event_id': event.id})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})