from django.shortcuts import render,get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from CRM.models import UserProfile,Client,Estimate,Project
from CRM.controller import authView
from django.db.models import Q  # For complex queries (search functionality)
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger  # For pagination




@login_required
def estimate_save(request, estimate_id=None):
    userRole = authView.get_user_role(request.user)
    estimate = None
    if estimate_id:  # Edit existing estimate
        estimate = get_object_or_404(Estimate, id=estimate_id)
    
    if request.method == 'POST':
        project_id = request.POST.get('project')
        status = request.POST.get('status')
        estimate_doc = request.FILES.get('estimate_doc')
        notes = request.POST.get('notes')

        try:
            
            project = Project.objects.get(id=project_id)
            client = project.client
            
            if estimate:  # Update existing estimate
                estimate.admin = request.user
                estimate.project = project
                estimate.status = status
                estimate.client = client
                estimate.notes = notes
                if estimate_doc:  # Only update document if new file is provided
                    estimate.document = estimate_doc
                estimate.save()
            else:  # Create new estimate
                estimate = Estimate.objects.create(
                    admin=request.user,
                    project=project,
                    status=status,
                    client=client,
                    notes=notes
                )
                if estimate_doc:
                    estimate.document = estimate_doc
                    estimate.save()
                
            messages.success(request, 'Estimate saved successfully!')
            return redirect('CRM:estimates')
            
        except (Client.DoesNotExist, Project.DoesNotExist) as e:
            messages.error(request, f'Error: {str(e)}')
            return redirect('CRM:estimates')

    profile = UserProfile.objects.get(user=request.user)
    clients = Client.objects.all()
    projects = Project.filter(client=profile)  # You'll need to add this
    
    return render(request, 'app/webkit/Estimate/estimates.html', {
        'clients': clients, 
        'profile': profile, 
        'estimate': estimate,
        'projects': projects ,
        'userRole' : userRole
    })
    
@login_required
def estimate_list(request):
    userRole = authView.get_user_role(request.user)
    estimates = Estimate.objects.all()
    if userRole =='client':
        profile = Client.objects.get(user=request.user)
        estimates = estimates.filter(client=profile)
    # Status filter
    status = request.GET.get('status')
    if status:
        estimates = estimates.filter(status=status)
    
    # Client filter (for admin only)
    if request.user.is_superuser or request.user.is_staff:
        client_id = request.GET.get('client')
        if client_id:
            estimates = estimates.filter(client__id=client_id)
            
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        estimates = estimates.filter(
            Q(project__name__icontains=search) |
            Q(client__user__username__icontains=search) |
            Q(notes__icontains=search)
        )
    
    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(estimates, 25)  # Show 25 estimates per page
    
    try:
        estimates = paginator.page(page)
    except PageNotAnInteger:
        estimates = paginator.page(1)
    except EmptyPage:
        estimates = paginator.page(paginator.num_pages)
    
    context = {
        'estimates': estimates,
        'clients': Client.objects.all(),
        'projects': Project.objects.all(),
        'userRole' : userRole
    }
    
    return render(request, 'app/webkit/Estimate/estimates.html', context)

@login_required
def delete_estimate(request, estimate_id):
    estimate = get_object_or_404(Estimate, id=estimate_id)
    
    # Check permissions (only admin or estimate creator can delete)
    if not (request.user.is_superuser or request.user == estimate.admin):
        messages.error(request, "You don't have permission to delete this estimate.")
        return redirect('CRM:estimates')
    
    # if request.method == 'POST':
    if estimate.document:  # Check if document exists
        estimate.document.delete(save=False)
    estimate.delete()
    messages.success(request, "Estimate deleted successfully!")
    return redirect('CRM:estimates')
    
    # If not POST, show confirmation page (optional)
    return redirect('CRM:estimates')