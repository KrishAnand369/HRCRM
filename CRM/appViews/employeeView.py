from django.shortcuts import render,get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from CRM.models import UserProfile,Client,User,Project,Team
from CRM.controller import authView
from django.db.models import Q


def employee_list(request):
    userRole =authView.get_user_role(request.user)
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
        for employee in employees:
            employee.is_clocked_in = employee.is_clocked_in()  # Call the method to check clock-in status
    return render(request, 'app/webkit/Employee/employeeList.html',{'userRole':userRole,'profile': profile, 'employees': employees })  

@login_required
def employee_delete(request, employee_id):
    if not request.user.is_superuser:
        messages.error(request, "You do not have permission to delete employees.")
        return redirect('CRM:employees')

    employee = get_object_or_404(UserProfile, id=employee_id)
    employee.delete()
    messages.success(request, "Employee deleted successfully.")
    return redirect('CRM:employees')