from django.shortcuts import render, get_object_or_404
from .models import ChatRoom, ChatMessage
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import ChatRoom, ChatMessage
from CRM.models import UserProfile,Team,Client,Project
from CRM.controller import authView
from django.db.models import Q
from .utils import get_or_create_private_chat

def chat_room(request, room_name):
    room = get_object_or_404(ChatRoom, name=room_name)
    messages = ChatMessage.objects.filter(room=room).order_by('timestamp')
    return render(request, 'chat/chat_room.html', {
        'room_name': room_name,
        'messages': messages,
    })
    
@login_required
def private_chat(request, username=None):
    """
    View for private messaging between the logged-in user and another user.
    """
    
    userRole = authView.get_user_role(request.user) 
    if userRole =='client':
        profile = Client.objects.get(user=request.user)
        projects = Project.objects.filter(client=profile)
        employees = UserProfile.objects.filter(assigned_projects__in=projects).distinct() 
    else:
        profile = UserProfile.objects.get(user=request.user)
        employees= UserProfile.objects.all().exclude(user=request.user)
        if not request.user.is_superuser:
            # Step 1: Get all teams the employee is part of
            teams = Team.objects.filter(Q(members=profile) | Q(leader=profile))

            # Step 2: Get all teammates from those teams
            teammates = set()  # Use a set to avoid duplicates
            for team in teams:
                # Add all members of the team
                teammates.update(team.members.all())
                # Add the team leader
                if team.leader:
                    teammates.add(team.leader)

            # Step 3: Exclude the employee themselves
            teammates.discard(profile)

            # Step 4: Convert the set back to a list for the template
            
            employees=list(teammates)
    if username:          
        other_user = get_object_or_404(User, username=username)
        room = get_or_create_private_chat(request.user, other_user)
        messages = ChatMessage.objects.filter(room=room).order_by('timestamp')
    else :          
         room = None
         messages = None
         other_user = None

    return render(request, 'chat/timeMessage.html', {
        'room': room,
        'messages': messages,
        'other_user': other_user,
        'userRole':userRole,
        'profile': profile,
        'employees':employees
    })
    #chat/private_chat.html
    
    