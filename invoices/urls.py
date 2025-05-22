from django.urls import path
from .views import create_invoice

app_name = 'invoices'

urlpatterns = [
    path('create/', create_invoice, name='create_invoice'),
]