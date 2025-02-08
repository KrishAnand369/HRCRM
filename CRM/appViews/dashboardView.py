from django.shortcuts import render,get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from CRM.models import UserProfile,Task,Project,Client
from CRM.controller import authView

@login_required
def dashboard(request):
    userRole = authView.get_user_role(request.user)
    if userRole =='client':
        profile = Client.objects.get(user=request.user)
        projects = Project.objects.filter(client=profile)
        tasks =Task.objects.filter(project__client=profile)
        if projects.count()==0:
            projectPercentage=0
        else: 
            projectPercentage=100*(projects.filter(status='Completed').count()/projects.count())
        project={
            'total':projects.count,
            'projects':projects.exclude(status='Completed'),
            'percentage':projectPercentage
                
        }
        if tasks.count()==0:
            taskPercentage=0
        else: 
            taskPercentage=100*(tasks.filter(status='Completed').count()/tasks.count())
        task={
            'total':tasks.count,
            'tasks':tasks.exclude(status='Completed'),
            'percentage':taskPercentage
        }
        return render(request, 'app/webkit/Dashboard/ClientDashboard.html', {'userRole':userRole,'profile':profile,'task':task,'project':project})
           
    profile = UserProfile.objects.get(user=request.user)
    if request.user.is_superuser:
        projects = Project.objects.all()
        tasks =Task.objects.all()
        employee_count = UserProfile.objects.all().count 
        if projects.count()==0:
            projectPercentage=0
        else: 
            projectPercentage=100*(projects.filter(status='Completed').count()/projects.count())
        project={
            'projects':projects.exclude(status='Completed'),
            'percentage':projectPercentage,
            'total':Project.objects.all().count
                
        }
        if tasks.count()==0:
            taskPercentage=0
        else: 
            taskPercentage=100*(tasks.filter(status='Completed').count()/tasks.count())
        task={
            'tasks':tasks.exclude(status='Completed'),
            'percentage':taskPercentage,
            'total':Task.objects.all().count
        }
        return render(request, 'app/webkit/Dashboard/Dashboard.html', {'userRole':userRole,'profile':profile,'task':task,'project':project,'employee_count':employee_count})
    else:
        projects = Project.objects.filter(assigned_users=profile)
        tasks =Task.objects.filter(assigned_to=profile)
        if projects.count()==0:
            projectPercentage=0
        else: 
            projectPercentage=100*(projects.filter(status='Completed').count()/projects.count())
        project={
            'total':projects.count,
            'projects':projects.exclude(status='Completed'),
            'percentage':projectPercentage
                
        }
        if tasks.count()==0:
            taskPercentage=0
        else: 
            taskPercentage=100*(tasks.filter(status='Completed').count()/tasks.count())
        task={
            'total':tasks.count,
            'tasks':tasks.exclude(status='Completed'),
            'percentage':taskPercentage
        }
        return render(request, 'app/webkit/Dashboard/DashboardUser.html', {'userRole':userRole,'profile':profile,'task':task,'project':project})
    
    