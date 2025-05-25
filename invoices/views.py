# from django.shortcuts import get_object_or_404
# from django.http import JsonResponse
# from datetime import datetime
# from .models import Client,Invoice,InvoiceItem

# def create_invoice(request):
#     if request.method == 'POST':
#         try:
#             # Get main invoice data
#             client_id = request.POST.get('client_id')
#             due_date_str = request.POST.get('due_date')
#             notes = request.POST.get('notes', '')
#             terms = request.POST.get('terms', 'Payment due within 30 days')
#             status = request.POST.get('status', 'draft')

#             # Parse and validate data
#             client = get_object_or_404(Client, id=client_id)
#             due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()

#             # Create invoice
#             invoice = Invoice(
#                 client=client,
#                 due_date=due_date,
#                 notes=notes,
#                 terms=terms,
#                 status=status
#             )
#             invoice.save()  # Auto-generates invoice number via save()

#             # Process invoice items
#             item_descriptions = request.POST.getlist('item_description[]')
#             item_quantities = request.POST.getlist('item_quantity[]')
#             item_prices = request.POST.getlist('item_price[]')
#             item_taxes = request.POST.getlist('item_tax[]')

#             for i in range(len(item_descriptions)):
#                 InvoiceItem.objects.create(
#                     invoice=invoice,
#                     description=item_descriptions[i],
#                     quantity=float(item_quantities[i]),
#                     unit_price=float(item_prices[i]),
#                     tax_rate=float(item_taxes[i]) if item_taxes[i] else 0.0
#                 )

#             # Return success response
#             return JsonResponse({
#                 'success': True,
#                 'invoice_id': invoice.id,
#                 'invoice_number': invoice.invoice_number,
#                 'redirect_url': f'/invoices/{invoice.id}/'
#             })

#         except Exception as e:
#             return JsonResponse({
#                 'success': False,
#                 'error': str(e)
#             }, status=400)

#     return JsonResponse({'error': 'Invalid request method'}, status=405)

# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages
# from django.http import JsonResponse

# from .models import InvoiceItem,Invoice
# from CRM.models import Client
# from .forms import InvoiceForm

# @login_required
# def create_invoice(request):
#     if request.method == 'POST':
#         form = InvoiceForm(request.POST)
        
#         print( 'reached 1')
#         print("POST data:", request.POST)
#         if form.is_valid():
#             # Create invoice
#             print( 'reached 2')
#             invoice = form.save(commit=False)
#             invoice.created_by = request.user
#             invoice.invoice_number = generate_invoice_number()
#             invoice.save()
            
#             # Add items
#             names = request.POST.getlist('item_description[]')
#             descriptions = request.POST.getlist('item_description[]')
#             quantities = request.POST.getlist('item_quantity[]')
#             prices = request.POST.getlist('item_price[]')
#             tax_rates = request.POST.getlist('item_tax[]')
            
#             for i in range(len(descriptions)):
#                 InvoiceItem.objects.create(
#                     invoice=invoice,
#                     name=names[i],
#                     description=descriptions[i],
#                     quantity=quantities[i],
#                     price=prices[i],
#                     tax_rate=tax_rates[i]
#                 )
#                 print( 'reached 3')
            
#             # Update totals
#             update_invoice_totals(invoice)
            
#             messages.success(request, 'Invoice created successfully!')
#             print( 'Invoice created successfully!')
#             return redirect('invoices:invoice_list')
#     else:
#         form = InvoiceForm()
    
#     clients = Client.objects.all()
#     return render(request, 'createInvoice.html', {
#         'form': form,
#         'clients': clients
#     })

# @login_required
# def edit_invoice(request, pk):
#     invoice = get_object_or_404(Invoice, pk=pk)
    
#     if request.method == 'POST':
#         form = InvoiceForm(request.POST, instance=invoice)
#         if form.is_valid():
#             # Update invoice
#             updated_invoice = form.save()
            
#             # Clear existing items
#             InvoiceItem.objects.filter(invoice=invoice).delete()
            
#             # Add new items
#             names = request.POST.getlist('item_description[]')
#             descriptions = request.POST.getlist('item_description[]')
#             quantities = request.POST.getlist('item_quantity[]')
#             prices = request.POST.getlist('item_price[]')
#             tax_rates = request.POST.getlist('item_tax[]')
            
#             for i in range(len(descriptions)):
#                 InvoiceItem.objects.create(
#                     invoice=updated_invoice,
#                     name=names[i],
#                     description=descriptions[i],
#                     quantity=quantities[i],
#                     price=prices[i],
#                     tax_rate=tax_rates[i]
#                 )
            
#             # Update totals
#             update_invoice_totals(updated_invoice)
            
#             messages.success(request, 'Invoice updated successfully!')
#             return redirect('invoices:invoice_list')
#     else:
#         form = InvoiceForm(instance=invoice)
    
#     clients = Client.objects.all()
#     items = invoice.items.all()
#     return render(request, 'invoices/edit_invoice.html', {
#         'form': form,
#         'clients': clients,
#         'items': items,
#         'invoice': invoice
#     })

# @login_required
# def invoice_detail(request, pk):
#     invoice = get_object_or_404(Invoice, pk=pk)
#     return render(request, 'invoices/invoice_detail.html', {
#         'invoice': invoice
#     })

# @login_required
# def invoice_list(request):
#     invoices = Invoice.objects.order_by('-date')
#     return render(request, 'invoices/invoice_list.html', {
#         'invoices': invoices
#     })

# def get_client_details(request, client_id):
#     client = get_object_or_404(Client, id=client_id)
#     return JsonResponse({
#         'contact_name': client.contact_name,
#         'email': client.email,
#         'address': client.address,
#         'payment_terms': client.payment_terms,
#     })

# # Helper functions
# def generate_invoice_number():
#     last_invoice = Invoice.objects.order_by('-id').first()
#     return f"INV-{1000 + (last_invoice.id if last_invoice else 0)}"

# def update_invoice_totals(invoice):
#     items = invoice.items.all()
#     subtotal = sum(item.quantity * item.price for item in items)
#     tax_amount = sum((item.quantity * item.price) * (item.tax_rate / 100) for item in items)
#     total = subtotal + tax_amount
    
#     invoice.subtotal = subtotal
#     invoice.tax_amount = tax_amount
#     invoice.total = total
#     invoice.save()

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from datetime import datetime
from decimal import Decimal

from .models import InvoiceItem, Invoice
from CRM.models import Client
from CRM.controller import authView

@login_required
def create_invoice(request):
    if request.method == 'POST':
        try:
            # Debug: Print all POST data
            print("POST data:", request.POST)
            
            # Extract and validate main invoice data
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
            return redirect('invoices:invoice_list')
            
        except Exception as e:
            messages.error(request, f"Error creating invoice: {str(e)}")
            return redirect('invoices:create_invoice')
    
    # GET request - show empty form
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
            # Extract and validate main invoice data
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
    return render(request, 'invoice_list.html', {
        'userRole':userRole,
        'invoices': invoices
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