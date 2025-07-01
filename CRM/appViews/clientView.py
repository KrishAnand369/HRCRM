from django.shortcuts import render,get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from CRM.models import UserProfile,Client,User,Project
from CRM.controller import authView
from CRM.utils import notify_user

def client_register(request, client_id=None):
    if request.method == 'POST':
        profile = UserProfile.objects.get(user=request.user)
        username = request.POST.get('clientName')
        email = request.POST.get('clientemail')
        password = request.POST.get('clientPassword')
        company_name = request.POST.get('companyName')
        contact_number = request.POST.get('contactNumber')
        address = request.POST.get('address')
        company_logo = request.FILES.get('client_logo')

        if company_logo and company_logo.content_type not in ['image/jpeg', 'image/png']:
            messages.error(request, 'Invalid file type. Only JPEG and PNG are allowed.')
            return redirect('CRM:clientList')

        if client_id:
            # Update existing client
            client = get_object_or_404(Client, id=client_id)
            client.company_name = company_name
            client.contact_number = contact_number
            client.address = address
            if company_logo:
                client.company_logo = company_logo
            client.user.username = username
            client.user.email = email
            if password:
                client.user.set_password(password)  # Only update password if provided
            client.user.save()
            client.save()
            messages.success(request, "Client updated successfully!")
            notify_user(request.user, "client details is updated")
            notify_user(client.user, "your details is updated")
        else:
            # Create new client
            user = User.objects.create_user(username=username, email=email, password=password)
            Client.objects.create(user=user, company_name=company_name, company_logo=company_logo, contact_number=contact_number, address=address)
            messages.success(request, "Client registered successfully!")
            notify_user(request.user, "client for company :"+ company_name +" is created")

        return redirect('CRM:clientList')

    client = None
    if client_id:
        client = get_object_or_404(Client, id=client_id)

    return render(request, 'app/webkit/client/clientlist.html', {'client': client,'profile':profile})

@login_required
def client_list(request):
    userRole = authView.get_user_role(request.user) 
    profile = UserProfile.objects.get(user=request.user)
    clients = Client.objects.all()
    if not request.user.is_superuser:
        projects_with_user = Project.objects.filter(assigned_users=profile)
        clients = Client.objects.filter(projects__in=projects_with_user).distinct()
    return render(request, 'app/webkit/client/clientlist.html',{'userRole':userRole,'profile': profile, 'clients': clients })  

