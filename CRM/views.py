
from django.shortcuts import render,get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import UserProfile,User,SalarySlip,Lead
from CRM.controller import authView
from datetime import datetime
from django.urls import reverse

from django.utils import timezone
from CRM.utils import notify_user

from django.contrib.auth import login, authenticate

def landing(request):
    return render(request,"app/webkit/index.html")


@login_required
def home(request):
    # //profile = UserProfile.objects.get(user=request.user)
    # {'profile': profile,}
    return render(request,"app/webkit/main.html")




@login_required
def userprofile(request):
    userRole = authView.get_user_role(request.user)
    profile = UserProfile.objects.get(user=request.user)
    skills = profile.skills.all()
    education = profile.education.all()

    context = {
        'userRole':userRole,
        'profile': profile,
        'skills': skills,
        'education': education,
    }
    return render(request,"app/webkit/user/user-profilepage.html",context)



@login_required
def save_profile(request):
    profile = UserProfile.objects.get(user=request.user)  # Fetch the logged-in user's profile
    
    userRole =authView.get_user_role(request.user)
    if request.method == 'POST':
        # Fetching basic info
        about = request.POST.get('about')
        profile.about = about
        role = request.POST.get('role')
        profile.role = role
        phone = request.POST.get('phone')
        profile.phone = phone
        country = request.POST.get('country')
        profile.country = country
        profile_pic = request.FILES.get('profile_pic')
        if profile_pic and profile_pic.content_type not in ['image/jpeg', 'image/png']:
            return render(request, 'app/webkit/user/user-edit-profile.html', {
                'error': 'Invalid file type. Only JPEG and PNG are allowed.',
            })
        if profile_pic:
            profile.profile_pic = profile_pic
        profile.save()
        
        # Saving skills (only add new skills)
        skill_names = request.POST.getlist('skill_name[]')
        skill_proficiency = request.POST.getlist('skill_proficiency[]')

        profile.skills.all().delete()
        
         # Add new skills without deleting existing ones
        for name, proficiency in zip(skill_names, skill_proficiency):
            if name.strip():  # Avoid empty entries
                profile.skills.create(name=name, proficiency=proficiency)
            
        
        # Saving education (only add new education entries)
        institutions = request.POST.getlist('institution[]')
        courses = request.POST.getlist('course[]')
        start_years = request.POST.getlist('start_year[]')
        end_years = request.POST.getlist('end_year[]')
        
        profile.education.all().delete()

        # Add new education records without deleting existing ones
        for institution, course, start_year, end_year in zip(institutions, courses, start_years, end_years):
            profile.education.get_or_create(
                institution=institution, 
                course=course, 
                start_year=start_year, 
                end_year=end_year
            )

        messages.success(request, "Profile updated successfully!")
        return redirect('CRM:userprofile')

    skills = profile.skills.all()
    education = profile.education.all()
    return render(request, 'app/webkit/user/user-edit-profile.html', {
        'profile': profile, 'skills': skills, 'education': education,'userRole':userRole
    })

@login_required
def employee_salary_slips(request,employee_id=None):
    profile = UserProfile.objects.get(user=request.user) 
    userRole =authView.get_user_role(request.user)
    if employee_id:
        if not request.user.is_superuser:
            messages.error(request, "You do not have permission to view this employee's salary slips.")
            return redirect('CRM:userprofile')
        
        else:
            employee = get_object_or_404(User, id=employee_id)
            slips = SalarySlip.objects.filter(employee=employee).order_by('-uploaded_at')
            return render(request, 'app/webkit/user/employeeSalary.html', {'profile': profile,'slips': slips,'userRole':userRole,'employee': employee})

    
    
    slips = SalarySlip.objects.filter(employee=request.user).order_by('-uploaded_at')
    return render(request, 'app/webkit/user/salary.html', {'profile': profile,'slips': slips,'userRole':userRole})


def upload_salary_slip(request):
    if request.method == 'POST':
        try:
            # Get form data directly from request
            user_id = request.POST.get('user_id')
            month = request.POST.get('month')
            salary_slip_file = request.FILES.get('salary_slip')
            
            # Basic validation
            if not all([user_id, month, salary_slip_file]):
                messages.error(request, "All fields are required!")
                return redirect(request.META.get('HTTP_REFERER'))
            
            try:
                employee = User.objects.get(id=user_id)
            except User.DoesNotExist:
                messages.error(request, "Employee not found!")
                return redirect(request.META.get('HTTP_REFERER'))
            
            # Create and save SalarySlip record
            SalarySlip.objects.create(
                employee=employee,
                month=month,
                slip_file=salary_slip_file,
                uploaded_at=timezone.now()
            )
            
            notify_user(employee, "admin uploaded your salary slip for "+ month)
            messages.success(request, "Salary slip uploaded successfully!")
            return redirect('CRM:employees')  # Redirect to your list view
            
        except Exception as e:
            messages.error(request, f"Error uploading salary slip: {str(e)}")
            return redirect('CRM:employees')
    
    # For GET requests (optional - if you need to render the form)
    return redirect('CRM:employees')


def contact_form(request):
    if request.method == 'POST':
        name = request.POST.get('Name')
        phone_number = request.POST.get('Phone Number')
        email = request.POST.get('Email')
        message = request.POST.get('Message')

        Lead.objects.create(
            name=name,
            phone_number=phone_number,
            email=email,
            message=message
        )

        messages.success(request, "Thank you for contacting us! We’ll get back to you soon.")
        superuser_profiles = UserProfile.objects.filter(user__is_superuser=True)
        for adm in superuser_profiles:
            notify_user(adm.user,reverse('CRM:lead_list'),name+" has contacted us through the contact form")
                  
    return redirect('CRM:landing')  # Use your contact page URL name




@login_required
def lead_list(request):
    profile = UserProfile.objects.get(user=request.user) 
    userRole =authView.get_user_role(request.user)
    if request.user.is_superuser:
        leads = Lead.objects.all().order_by('-created_at')
    return render(request, 'app/webkit/leadList.html', {'leads': leads,'profile': profile, 'userRole': userRole})

def terms_of_service(request):
    profile = UserProfile.objects.get(user=request.user) 
    userRole =authView.get_user_role(request.user)
    return render(request, 'app/webkit/terms-of-service.html', {'profile': profile, 'userRole': userRole})

def privacy_policy(request):
    profile = UserProfile.objects.get(user=request.user)
    userRole =authView.get_user_role(request.user)
    return render(request, 'app/webkit/privacy-policy.html', {'profile': profile, 'userRole': userRole})