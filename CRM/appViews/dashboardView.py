from django.shortcuts import render,get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from CRM.models import UserProfile,Task,Project,Client,ClockEvent,User
from CRM.controller import authView
from django.utils import timezone
from datetime import time
from invoices.utils import get_current_month_invoice_totals,get_current_month_invoice_totals_client,get_invoice_totals_client,get_invoice_totals

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
            'percentage':round(projectPercentage,2)
                
        }
        if tasks.count()==0:
            taskPercentage=0
        else: 
            taskPercentage=100*(tasks.filter(status='Completed').count()/tasks.count())
        task={
            'total':tasks.count,
            'tasks':tasks.exclude(status='Completed'),
            'percentage':round(taskPercentage,2)
        }
        invoice_sum = get_invoice_totals_client(profile)
        return render(request, 'app/webkit/Dashboard/ClientDashboard.html', {'userRole':userRole,'profile':profile,'task':task,'project':project,'invoice_sum':invoice_sum})
           
    profile = UserProfile.objects.get(user=request.user)
    if request.user.is_superuser:
        projects = Project.objects.all()
        tasks =Task.objects.all()
        admincount =  User.objects.filter(is_superuser=True).count()
        employee_count = UserProfile.objects.all().count()
        employee_count =employee_count-admincount
        todays_attendence = get_clocked_in_users_count()/employee_count*100
        invoice_sum = get_invoice_totals()
        if projects.count()==0:
            projectPercentage=0
        else: 
            projectPercentage=100*(projects.filter(status='Completed').count()/projects.count())
        project={
            'projects':projects.exclude(status='Completed'),
            'percentage':round(projectPercentage,2),
            'total':Project.objects.all().count
                
        }
        if tasks.count()==0:
            taskPercentage=0
        else: 
            taskPercentage=100*(tasks.filter(status='Completed').count()/tasks.count())
        task={
            'tasks':tasks.exclude(status='Completed'),
            'percentage':round(taskPercentage,2),
            'total':Task.objects.all().count
        }
        return render(request, 'app/webkit/Dashboard/Dashboard.html', {'userRole':userRole,'profile':profile,'task':task,'project':project,'employee_count':employee_count,'todays_attendence':todays_attendence,'invoice_sum':invoice_sum})
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
            'percentage':round(projectPercentage,2)
                
        }
        if tasks.count()==0:
            taskPercentage=0
        else: 
            taskPercentage=100*(tasks.filter(status='Completed').count()/tasks.count())
        task={
            'total':tasks.count,
            'tasks':tasks.exclude(status='Completed'),
            'percentage':round(taskPercentage,2)
        }
        daily_hours = request.user.profile.daily_hours_worked()
        is_clocked_in = request.user.profile.is_clocked_in()
        # context = {}
        # # Calculate total time in seconds
        # total_seconds = request.user.profile.daily_hours_worked()
        # context['total_seconds'] = total_seconds
        return render(request, 'app/webkit/Dashboard/DashboardUser.html', {'userRole':userRole,'profile':profile,'task':task,'project':project,'daily_hours':daily_hours,'is_clocked_in':is_clocked_in})
    
@login_required
def clock_in(request):
    # Check if the user has a profile (i.e., is an employee)
    userRole = authView.get_user_role(request.user)
    if userRole =='client' or request.user.is_superuser:
        messages.warning(request, "Only employees can clock in.")
    else:
        current_time = timezone.now()
        start_of_day = timezone.make_aware(timezone.datetime.combine(current_time.date(), time(2, 0)))  # 7:30 PM
        end_of_day = timezone.make_aware(timezone.datetime.combine(current_time.date(), time(12, 0)))  # 5:30 PM

        # Check if the current time is after 5:00 PM
        if current_time > end_of_day:
            messages.warning(request, "You cannot clock in after 5:30 PM.")    
        elif current_time < start_of_day:
            messages.warning(request, "You cannot clock in before 7:30 PM.")    
        else :
            # Check if the user is already clocked in
            if request.user.profile.is_clocked_in():
                messages.warning(request, "You are already clocked in.")
            else:
                # Create a new clock-in event
                ClockEvent.objects.create(profile=request.user.profile, event_type='IN')
                messages.success(request, "You have successfully clocked in.")

    return redirect('/dashboard')

@login_required
def clock_out(request):
    # Check if the user has a profile (i.e., is an employee)
    userRole = authView.get_user_role(request.user)
    if userRole =='client' or request.user.is_superuser:
        messages.warning(request, "Only employees can clock in.")
    else :
        # Check if the user is already clocked out
        if not request.user.profile.is_clocked_in():
            messages.warning(request, "You are already clocked out.")
        else:
            # Create a new clock-out event
            ClockEvent.objects.create(profile=request.user.profile, event_type='OUT')
            messages.success(request, "You have successfully clocked out.")

    return redirect('/dashboard')

def get_clocked_in_users_count():
    """
    Returns the number of users currently clocked in.
    """
    # Fetch all employees
    employees = UserProfile.objects.all()

    # Count the number of employees who are currently clocked in
    clocked_in_count = 0
    for employee in employees:
        if employee.is_clocked_in():  # Call the method to check clock-in status
            clocked_in_count += 1

    return clocked_in_count