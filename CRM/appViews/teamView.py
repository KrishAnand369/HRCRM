from django.shortcuts import get_object_or_404, redirect,render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from CRM.models import Team, UserProfile
from CRM.controller import authView
from django.db.models import Q

@login_required
def create_team(request,team_id=None):
    userRole = authView.get_user_role(request.user)
    if team_id:
        team = get_object_or_404(Team,id=team_id)
    
        if request.method == 'POST':
            name = request.POST.get('name')
            leader_id = request.POST.get('leader')
            members = request.POST.getlist('members')
            
            if team: #update existing team
                team.members.set(members)
                if leader_id:
                        team.leader = get_object_or_404(UserProfile, id=leader_id)
                team.save()
                messages.success(request, 'Team edited successfully!')
                return redirect('/team/list')
                # return render(request,"app/webkit/team/teams.html",{'userRole':userRole})
            else:
                if request.user.is_superuser:
                    team = Team.objects.create(name=name)
                    team.members.set(members)
                    if leader_id:
                        team.leader = get_object_or_404(UserProfile, id=leader_id)
                    team.save()
                    messages.success(request, 'Team created successfully!')
                    return redirect('/team/list')
                    # return render(request,"app/webkit/team/teams.html")
                else:
                    messages.error(request, 'Only superusers can create teams.')
                    # return redirect('home')
                    return redirect('/team/list')
        return redirect('/team/list')
        # return render(request,"app/webkit/team/teams.html")
    

@login_required
def add_member(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        user = get_object_or_404(UserProfile, id=user_id)
        if team.add_member(user, request.user):
            messages.success(request, 'Member added successfully!')
        else:
            messages.error(request, 'You do not have permission to add members.')
    return redirect('team_detail', team_id=team.id)

@login_required
def set_leader(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        user = get_object_or_404(UserProfile, id=user_id)
        if team.set_leader(user, request.user):
            messages.success(request, 'Leader set successfully!')
        else:
            messages.error(request, 'You do not have permission to set the leader or the user is not a member of the team.')
    return redirect('team_detail', team_id=team.id)

def list_teams(request):
    userRole = authView.get_user_role(request.user)
    users= UserProfile.objects.all()
    profile = UserProfile.objects.get(user=request.user)
    teams = Team.objects.all()
    if not request.user.is_superuser:
        # Assuming `profile` is the logged-in user's profile
        teams = Team.objects.filter(Q(members=profile) | Q(leader=profile)).distinct()
    context = {
        'userRole':userRole,
        'teams': teams,
        'users': users,
        'profile': profile,
    }
    return render(request,"app/webkit/team/teams.html",context)

@login_required
def delete_team(request, team_id):
    if not request.user.is_superuser:
        messages.error(request, "You do not have permission to delete teams.")
        return redirect('CRM:list_team')
    team = get_object_or_404(Team, id=team_id)
    try:
        team.delete()
        messages.success(request, "Team deleted successfully.")
    except Exception as e:
        messages.error(request, f"An error occurred while deleting the team: {e}")
    return redirect('CRM:list_team')
        