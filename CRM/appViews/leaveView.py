from django.shortcuts import render,get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from CRM.models import UserProfile,Client,Project,LeaveApplication
from CRM.controller import authView
from CRM.utils import notify_user


@login_required
def leave_application_list(request):  # Get the selected status
    profile = UserProfile.objects.get(user=request.user)
    userRole = authView.get_user_role(request.user)
    if request.user.is_superuser:
        pending_applications = LeaveApplication.objects.filter(status='pending')
        # pending_applications = pending_applications.filter(as) # assigned admin
    else:
        messages.error(request, 'You do not have permission to approve this leave.')  
    context = {
        'userRole':userRole,
        'leave_applications':pending_applications
    }
    return render(request, 'app/webkit/Employee/leavApplList.html', context)

@login_required
def my_applications(request):  # Get the selected status
    profile = UserProfile.objects.get(user=request.user)
    userRole = authView.get_user_role(request.user)
    pending_applications = LeaveApplication.objects.filter(employee=profile)  
    context = {
        'profile': profile,
        'userRole':userRole,
        'leave_applications':pending_applications
    }
    return render(request, 'app/webkit/user/myLeaveApplication.html', context)

@login_required
def apply_leave(request):
    profile = UserProfile.objects.get(user=request.user)
    if request.method == 'POST':
        to = request.POST.get('to')
        reason = request.POST.get('reason')
        date = request.POST.get('date')
        notes = request.POST.get('notes') 
        documents = request.FILES.get('documents')

         # Create new project
        LeaveApplication.objects.create(
            
            employee = profile,
            reason=reason,
            date=date,
            documents =  documents,
            notes=notes,
            to_admin =to,
        )
        
        notify_user(to.user, "Employee" +request.user.username +"has applied for a leave")
        return redirect('CRM:userprofile')
    return redirect('/profile')


@login_required
def approve_leave(request, leave_id):
    # Retrieve the leave application or return 404 if not found
    leave_application = get_object_or_404(LeaveApplication, id=leave_id)
    
    # Check if the user is an admin or has permission to approve
    if request.user.is_superuser or request.user == leave_application.to_admin.user:
        # Update the status to 'approved'
        leave_application.status = 'approved'
        try:
            leave_application.save()
            notify_user(leave_application.employee.user, "Your leave application was Approved")
        except Exception as e:
            print(f"Error saving leave application: {e}")
    # Redirect back to the leave application list
    return redirect('/leave_applications') 

@login_required
def decline_leave(request, leave_id):
    # Retrieve the leave application or return 404 if not found
    leave_application = get_object_or_404(LeaveApplication, id=leave_id)
    
    # Check if the user is an admin or has permission to reject
    if request.user.is_superuser or request.user == leave_application.to_admin.user:
        # Update the status to 'rejected'
        leave_application.status = 'rejected'
        try:
            leave_application.save()
            print("Leave application rejecTed.")
            notify_user(leave_application.employee.user, "Your leave application was rejected")
        except Exception as e:
            print(f"Error saving leave application: {e}")
    # Redirect back to the leave application list
    return redirect('/leave_applications') 


@login_required
def save_commend_leave(request, leave_id):
    # Retrieve the leave application or return 404 if not found
    leave_application = get_object_or_404(LeaveApplication, id=leave_id)
    
    # Check if the user is an admin 
    if request.user.is_superuser or request.user == leave_application.to_admin.user:
        # Update the comment
        admin_comment= request.POST.get('comment')
        leave_application.admin_comment = admin_comment
        try:
            leave_application.save()
            notify_user(leave_application.employee.user, "admin made a commend on your leave application")
        except Exception as e:
            print(f"Error saving leave application: {e}")
    # Redirect back to the leave application list
    return redirect('/leave_applications') 