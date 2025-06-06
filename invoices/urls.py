from django.urls import path
from .views import (
    create_invoice, edit_invoice,
    invoice_detail, invoice_list,
    get_client_details,mark_invoice_paid
)

app_name = 'invoices'

urlpatterns = [
    path('invoices/', invoice_list, name='invoice_list'),
    path('create/', create_invoice, name='create_invoice'),
    path('<int:pk>/', invoice_detail, name='invoice_detail'),
    path('<int:pk>/edit/', edit_invoice, name='edit_invoice'),
    path('<int:pk>/mark_paid/',mark_invoice_paid, name='mark_invoice_paid'),
    path('client/<int:client_id>/details/', get_client_details, name='client_details'),
]