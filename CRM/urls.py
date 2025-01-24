from django.urls import path
from . import views
from CRM.controller import authView
from django.contrib.auth.views import LoginView, LogoutView

app_name ="CRM"
urlpatterns = [
    path('', views.landing,name='landing'),
    
    path('register/', authView.register, name='register'),
    path('login/',authView.loginPage,name='loginpage'),
    path('logout/',authView.logoutPage,name='logoutpage'),
    
    
    path('home',views.home,name='home'),
    
    path('profile',views.userprofile,name='userprofile'),
    path('saveprofile/',views.save_profile,name='save_profile'),
    
    path('projects',views.project_list,name='project'),
    path('new-project/', views.new_project_view, name='new_project'),
    
    path('clients',views.client_list,name='clientList'),
    path('new-client/', views.client_register, name='new_client'),
]