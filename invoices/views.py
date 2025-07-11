from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from datetime import datetime
from decimal import Decimal

from .models import InvoiceItem, Invoice
from CRM.models import Client
from CRM.controller import authView
from CRM.utils import notify_user

@login_required
def create_invoice(request):
    if request.method == 'POST':
        try:
            
            print("POST data:", request.POST)
            
            
            client_id = request.POST.get('client_id')
            due_date_str = request.POST.get('due_date')
            status = request.POST.get('status', 'draft')
            terms = request.POST.get('terms', 'Payment due within 30 days')
            notes = request.POST.get('notes', '')
            
            if not client_id or not due_date_str:
                messages.error(request, "Client and Due Date are required")
                return redirect('invoices:create_invoice')
            
            try:
                client = Client.objects.get(id=client_id)
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
            except (Client.DoesNotExist, ValueError) as e:
                messages.error(request, f"Invalid data: {str(e)}")
                return redirect('invoices:create_invoice')
            
            # Create the invoice
            invoice = Invoice.objects.create(
                client=client,
                due_date=due_date,
                status=status,
                terms=terms,
                notes=notes,
                created_by=request.user,
                invoice_number=generate_invoice_number()
            )
            
            # Process invoice items
            names = request.POST.getlist('item_name[]')
            descriptions = request.POST.getlist('item_description[]')
            quantities = request.POST.getlist('item_quantity[]')
            prices = request.POST.getlist('item_price[]')
            tax_rates = request.POST.getlist('item_tax[]')
            
            for i in range(len(descriptions)):
                try:
                    InvoiceItem.objects.create(
                        invoice=invoice,
                        name=names[i] if i < len(names) else descriptions[i][:30],
                        description=descriptions[i],
                        quantity=Decimal(quantities[i]),
                        price=Decimal(prices[i]),
                        tax_rate=Decimal(tax_rates[i]) if i < len(tax_rates) else Decimal(0)
                    )
                except (IndexError, ValueError) as e:
                    messages.warning(request, f"Error processing item {i+1}: {str(e)}")
                    continue
            
            # Update invoice totals
            update_invoice_totals(invoice)
            
            messages.success(request, 'Invoice created successfully!')
            notify_user(client.user,"you have a new invoice with No: "+ invoice.invoice_number)
            return redirect('invoices:invoice_list')
            
        except Exception as e:
            messages.error(request, f"Error creating invoice: {str(e)}")
            return redirect('invoices:create_invoice')
    
    # GET request - show create form
    clients = Client.objects.all()
    userRole = authView.get_user_role(request.user)
    return render(request, 'createInvoice.html', {
        'userRole':userRole,
        'clients': clients
    })

@login_required
def edit_invoice(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    
    if request.method == 'POST':
        try:
            client_id = request.POST.get('client_id')
            due_date_str = request.POST.get('due_date')
            
            if not client_id or not due_date_str:
                messages.error(request, "Client and Due Date are required")
                return redirect('invoices:edit_invoice', pk=pk)
            
            try:
                client = Client.objects.get(id=client_id)
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
            except (Client.DoesNotExist, ValueError) as e:
                messages.error(request, f"Invalid data: {str(e)}")
                return redirect('invoices:edit_invoice', pk=pk)
            
            # Update invoice
            invoice.client = client
            invoice.due_date = due_date
            invoice.status = request.POST.get('status', 'draft')
            invoice.terms = request.POST.get('terms', 'Payment due within 30 days')
            invoice.notes = request.POST.get('notes', '')
            invoice.save()
            
            # Clear existing items
            invoice.items.all().delete()
            
            # Add new items
            names = request.POST.getlist('item_name[]')
            descriptions = request.POST.getlist('item_description[]')
            quantities = request.POST.getlist('item_quantity[]')
            prices = request.POST.getlist('item_price[]')
            tax_rates = request.POST.getlist('item_tax[]')
            
            for i in range(len(descriptions)):
                try:
                    InvoiceItem.objects.create(
                        invoice=invoice,
                        name=names[i] if i < len(names) else descriptions[i][:30],
                        description=descriptions[i],
                        quantity=Decimal(quantities[i]),
                        price=Decimal(prices[i]),
                        tax_rate=Decimal(tax_rates[i]) if i < len(tax_rates) else Decimal(0)
                    )
                except (IndexError, ValueError) as e:
                    messages.warning(request, f"Error processing item {i+1}: {str(e)}")
                    continue
            
            # Update totals
            update_invoice_totals(invoice)
            
            messages.success(request, 'Invoice updated successfully!')
            return redirect('invoices:invoice_detail', pk=invoice.id)
            
        except Exception as e:
            messages.error(request, f"Error updating invoice: {str(e)}")
            return redirect('invoices:edit_invoice', pk=pk)
    
    # GET request - show existing invoice
    clients = Client.objects.all()
    userRole = authView.get_user_role(request.user)
    return render(request, 'edit_invoice.html', {
        'invoice': invoice,
        'userRole':userRole,
        'clients': clients
    })
    
    
@login_required
def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    userRole = authView.get_user_role(request.user)
    return render(request, 'invoice_detail.html', {
        'userRole':userRole,
        'invoice': invoice
    })

@login_required
def invoice_list(request):
    invoices = Invoice.objects.order_by('-date')
    userRole = authView.get_user_role(request.user)
    if userRole =='client':
        profile = Client.objects.get(user=request.user)
        invoices = invoices.filter(client=profile)
    return render(request, 'invoice_list.html', {
        'userRole':userRole,
        'invoices': invoices
    })
    
@login_required
def invoice_list_new(request):
    status = request.GET.get('status')
    if status == 'All' or not status:  # If 'All projects' is selected or no status is provided
        invoices = Invoice.objects.all()
    elif status:    
        invoices = Invoice.objects.filter(status=status)
    invoices = invoices.order_by('-date')
    userRole = authView.get_user_role(request.user)
    if userRole =='client':
        profile = Client.objects.get(user=request.user)
        invoices = invoices.filter(client=profile)
    return render(request, 'invoice_list.html', {
        'userRole':userRole,
        'invoices': invoices,
        'status': status,
    })

def get_client_details(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    return JsonResponse({
        'contact_name': client.contact_name,
        'email': client.email,
        'address': client.address
    })

# Helper functions
def generate_invoice_number():
    last_invoice = Invoice.objects.order_by('-id').first()
    return f"INV-{1000 + (last_invoice.id if last_invoice else 0)}"

def update_invoice_totals(invoice):
    items = invoice.items.all()
    subtotal = sum(item.quantity * item.price for item in items)
    tax_amount = sum((item.quantity * item.price) * (item.tax_rate / 100) for item in items)
    total = subtotal + tax_amount
    
    invoice.subtotal = subtotal
    invoice.tax_amount = tax_amount
    invoice.total = total
    invoice.save()
    
@login_required
def mark_invoice_paid(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    try:
        # Update invoice status to paid
        invoice.status = 'paid'
        invoice.save()
        messages.success(request, 'Invoice updated successfully!')
        return redirect('invoices:invoice_detail', pk=invoice.id)
        
    except Exception as e:
        messages.error(request, f"Error updating invoice: {str(e)}")
        return redirect('invoices:invoice_detail', pk=pk)
 
@login_required
def delete_invoice(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    try:
        invoice.delete()
        messages.success(request, 'Invoice deleted successfully!')
    except Exception as e:
        messages.error(request, f"Error deleting invoice: {str(e)}")
    return redirect('invoices:invoice_list')
     