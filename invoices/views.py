from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from datetime import datetime
from .models import Client,Invoice,InvoiceItem

def create_invoice(request):
    if request.method == 'POST':
        try:
            # Get main invoice data
            client_id = request.POST.get('client_id')
            due_date_str = request.POST.get('due_date')
            notes = request.POST.get('notes', '')
            terms = request.POST.get('terms', 'Payment due within 30 days')
            status = request.POST.get('status', 'draft')

            # Parse and validate data
            client = get_object_or_404(Client, id=client_id)
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()

            # Create invoice
            invoice = Invoice(
                client=client,
                due_date=due_date,
                notes=notes,
                terms=terms,
                status=status
            )
            invoice.save()  # Auto-generates invoice number via save()

            # Process invoice items
            item_descriptions = request.POST.getlist('item_description[]')
            item_quantities = request.POST.getlist('item_quantity[]')
            item_prices = request.POST.getlist('item_price[]')
            item_taxes = request.POST.getlist('item_tax[]')

            for i in range(len(item_descriptions)):
                InvoiceItem.objects.create(
                    invoice=invoice,
                    description=item_descriptions[i],
                    quantity=float(item_quantities[i]),
                    unit_price=float(item_prices[i]),
                    tax_rate=float(item_taxes[i]) if item_taxes[i] else 0.0
                )

            # Return success response
            return JsonResponse({
                'success': True,
                'invoice_id': invoice.id,
                'invoice_number': invoice.invoice_number,
                'redirect_url': f'/invoices/{invoice.id}/'
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)