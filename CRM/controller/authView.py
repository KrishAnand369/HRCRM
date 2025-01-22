from django.contrib import messages
from django.shortcuts import render, redirect
from CRM.signupForm import UserRegistrationForm
from django.contrib.auth import authenticate,login,logout
from CRM.models import UserProfile




def register(request):
    form = UserRegistrationForm()
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user=form.save()
            user.email = form.cleaned_data.get('email')
            user.save()
            messages.success(request,'Registered Successfuly! Login to Continue')
            return redirect('/login')
        else:
            print(form.errors)
    context = {'form':form}

    return render(request,'registration.html',context)

def loginPage(request):
    if request.method == 'POST':
        name=request.POST.get('username')
        password=request.POST.get('password')
        user = authenticate(request,username=name,password =password)

        if user is not None:
            login(request,user)
            messages.success(request,"Logged in Successfully")
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            return redirect('/home')
        else:
            messages.error(request,"Invalid username or password")
            return redirect('/login')
    return render(request,'SignIn.html')

def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')  # Changed to username instead of email
        password = request.POST.get('password')

        # Authenticate using the username and password directly
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, "You have successfully signed in!")
            return redirect('CRM:dashboard')  # Redirect to dashboard after login
        else:
            messages.error(request, "Invalid credentials. Please try again.")
            return redirect('CRM:signin')

    return render(request, 'CRM/static/html/backend/auth-sign-in.html')

def signinwithemail(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Authenticate using the default User model
        try:
            user = User.objects.get(email=email)  # Fetch user by email
        except User.DoesNotExist:
            messages.error(request, "User with this email does not exist.")
            return redirect('CRM:signin')

        # Authenticate using username and password
        user = authenticate(request, username=user.username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, "You have successfully signed in!")
            return redirect('CRM:dashboard')  # Change 'dashboard' as needed
        else:
            messages.error(request, "Invalid credentials. Please try again.")
            return redirect('CRM:signin')

    return render(request, 'CRM/static/html/backend/auth-sign-in.html')


def logoutPage(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request,"Logged Out Successfully")
        return redirect('/')
    return redirect('/')

