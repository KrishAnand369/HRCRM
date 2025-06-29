from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from CRM.models import Ticket,Client,UserProfile
from CRM.controller import authView
from django.contrib import messages
from django.db.models import Q

@login_required
def ticket_save(request, ticket_id=None):
    userRole = authView.get_user_role(request.user)
    ticket = None
    if ticket_id:  # Edit existing ticket
        ticket = get_object_or_404(Ticket, id=ticket_id)
    
    if request.method == 'POST':
        status = request.POST.get('status')
        ticket_doc = request.FILES.get('ticket_doc')
        topic = request.POST.get('topic')
        description = request.POST.get('description')
        assigned_to_id = request.POST.get("assignMember")

        try:
            if userRole =='client':
                profile = Client.objects.get(user=request.user)
                
            else:
                profile = UserProfile.objects.get(user=request.user)
            
            if ticket and request.user.is_superuser:  # Update existing ticket
                ticket.status = status
                if ticket_doc:
                    ticket.document = ticket_doc
                if assigned_to_id:
                    ticket.assigned_employee = get_object_or_404(UserProfile, id=assigned_to_id)
                    if ticket.status == "Created":
                        ticket.status = "Assigned"
                        
                else:
                    ticket.assigned_employee = None  # Unassign if no user is selected
                ticket.save()
            elif ticket and ticket.assigned_employee.user == request.user:
                ticket.status = status
                if status == "Solved" or status == "Pending":
                    ticket.save()
                
            elif ticket and ticket.client.user == request.user:
                ticket.topic = topic
                ticket.description = description
                if ticket_doc:
                    ticket.document = ticket_doc
                ticket.save()    
            else:  # Create new ticket
                ticket = Ticket.objects.create(
                    client=profile,
                    topic = topic,
                    description = description
                )
                if ticket_doc:
                    ticket.document = ticket_doc
                    ticket.save()
                
            messages.success(request, 'ticket saved successfully!')
            return redirect('CRM:ticket_list')
            
        except (Client.DoesNotExist,) as e:
            messages.error(request, f'Error: {str(e)}')
            return redirect('CRM:ticket_list')

    
    clients = Client.objects.all()
    
    return render(request, 'app/webkit/ticket/tickets.html', {
        'clients': clients, 
        'profile': profile, 
        'ticket': ticket,
        'userRole' : userRole
    })
    
  
    
@login_required
def ticket_list(request):
    status = request.GET.get('status', 'all')
    userRole = authView.get_user_role(request.user)
    
    tickets = Ticket.objects.all()
    if status != 'all':
        tickets = tickets.filter(status=status)
    
    if userRole == 'client':
        profile = Client.objects.get(user=request.user)
        tickets = tickets.filter(client=profile)
    else:
        profile = UserProfile.objects.get(user=request.user)
        if not request.user.is_superuser:
            tickets = tickets.filter(assigned_employee=profile)
    
    clients = Client.objects.all()
    employees = UserProfile.objects.filter(user__is_superuser=False)
    
    context = {
        'tickets': tickets.order_by('-created_at'),
        'userRole': userRole,
        'status': status,
        'clients': clients,
        'employees': employees,
        'profile': profile ,
    }
    return render(request, 'app/webkit/ticket/tickets.html', context)