from django.contrib.auth.forms import UserCreationForm
from .models import User
from django import forms

class UserRegistrationForm(UserCreationForm):
    username= forms.CharField(widget=forms.TextInput(attrs={'class':'form-control my-2','placeholder':'Enter Username'}))
    email= forms.CharField(widget=forms.EmailInput(attrs={'class':'form-control my-2','placeholder':'Enter Email'}),required=True)
    password1= forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control my-2','placeholder':'Enter Password'}))
    password2= forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control my-2','placeholder':'Confirm Password'}))



class Meta:
    model = User
    fields = ['username','email','password1','password2']
 
def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email  
     
def save(self, commit=True):
        print("reached")
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']  # Explicitly save the email
        print(self.cleaned_data)
        if commit:
            user.save()
        return user