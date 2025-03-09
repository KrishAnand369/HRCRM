from django.shortcuts import render,get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from CRM.models import UserProfile,Client,User,Project
from CRM.controller import authView
def employee_list(request):
    userRole =authView.get_user_role(request.user)
    if userRole =='client':
        profile = Client.objects.get(user=request.user)
        projects = Project.objects.filter(client=profile)
        employees = UserProfile.objects.filter(assigned_projects__in=projects).distinct() 
    else:
        profile = UserProfile.objects.get(user=request.user)
        employees= UserProfile.objects.all()
        # if not request.user.is_superuser:
        #     employees=none
    for employee in employees:
        employee.is_clocked_in = employee.is_clocked_in()  # Call the method to check clock-in status
    return render(request, 'app/webkit/Employee/employeeList.html',{'userRole':userRole,'profile': profile, 'employees': employees })  