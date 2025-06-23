from django.db.models import Sum, Q
from django.utils import timezone
from decimal import Decimal
from .models import Invoice

def get_invoice_totals():
    """
    Returns a dictionary with total invoices, paid amount, and percentage paid for a given month
    """
    
    # Calculate totals
    total_invoices = Invoice.objects.all().aggregate(
        total=Sum('total')
    )['total'] or Decimal('0.00')
    
    paid_invoices = Invoice.objects.all().filter(
        status='paid'  # Only count fully paid invoices
    ).aggregate(
        paid=Sum('total')
    )['paid'] or Decimal('0.00')
    
    # Calculate percentage paid
    percentage_paid = (paid_invoices / total_invoices * 100) if total_invoices > 0 else 0
    
    return {
        'total_invoices':round(float( total_invoices),4),
        'paid_amount': paid_invoices,
        'percentage_paid': round(float(percentage_paid), 2)
    }

def get_monthly_invoice_totals(year, month):
    """
    Returns a dictionary with total invoices, paid amount, and percentage paid for a given month
    """
    # Get the first and last day of the month
    first_day = timezone.datetime(year=year, month=month, day=1).date()
    last_day = timezone.datetime(
        year=year + (month // 12), 
        month=(month % 12) + 1, 
        day=1
    ).date() - timezone.timedelta(days=1)
    
    # Filter invoices for the month
    monthly_invoices = Invoice.objects.filter(
        date__gte=first_day,
        date__lte=last_day
    )
    
    # Calculate totals
    total_invoices = monthly_invoices.aggregate(
        total=Sum('total')
    )['total'] or Decimal('0.00')
    
    paid_invoices = monthly_invoices.filter(
        status='paid'  # Only count fully paid invoices
    ).aggregate(
        paid=Sum('total')
    )['paid'] or Decimal('0.00')
    
    # Calculate percentage paid
    percentage_paid = (paid_invoices / total_invoices * 100) if total_invoices > 0 else 0
    
    return {
        'total_invoices':round(float( total_invoices),4),
        'paid_amount': paid_invoices,
        'percentage_paid': round(float(percentage_paid), 2),
        'month': first_day.strftime('%B %Y')
    }
    
def get_monthly_invoice_totals_client(year, month,client):
    """
    Returns a dictionary with total invoices, paid amount, and percentage paid for a given month
    """
    # Get the first and last day of the month
    first_day = timezone.datetime(year=year, month=month, day=1).date()
    last_day = timezone.datetime(
        year=year + (month // 12), 
        month=(month % 12) + 1, 
        day=1
    ).date() - timezone.timedelta(days=1)
    
    # Filter invoices for the month
    monthly_invoices = Invoice.objects.filter(
        client= client,
        date__gte=first_day,
        date__lte=last_day
    )
    
    # Calculate totals
    total_invoices = monthly_invoices.aggregate(
        total=Sum('total')
    )['total'] or Decimal('0.00')
    
    paid_invoices = monthly_invoices.filter(
        status='paid'  # Only count fully paid invoices
    ).aggregate(
        paid=Sum('total')
    )['paid'] or Decimal('0.00')
    
    # Calculate percentage paid
    percentage_paid = (paid_invoices / total_invoices * 100) if total_invoices > 0 else 0
    
    return {
        'total_invoices':round(float( total_invoices),4),
        'paid_amount': paid_invoices,
        'percentage_paid': round(float(percentage_paid), 2),
        'month': first_day.strftime('%B %Y')
    }
    
def get_invoice_totals_client(client):
    
    # Filter invoices for the month
    client_invoices = Invoice.objects.filter(
        client= client
    )
    
    # Calculate totals
    total_invoices = client_invoices.aggregate(
        total=Sum('total')
    )['total'] or Decimal('0.00')
    
    paid_invoices = client_invoices.filter(
        status='paid'  # Only count fully paid invoices
    ).aggregate(
        paid=Sum('total')
    )['paid'] or Decimal('0.00')
    
    # Calculate percentage paid
    percentage_paid = (paid_invoices / total_invoices * 100) if total_invoices > 0 else 0
    
    return {
        'total_invoices':round(float( total_invoices),4),
        'paid_amount': paid_invoices,
        'percentage_paid': round(float(percentage_paid), 2),
    }

def get_current_month_invoice_totals():
    """Returns totals for the current month"""
    today = timezone.now().date()
    return get_monthly_invoice_totals(today.year, today.month)

def get_current_month_invoice_totals_client(client):
    """Returns totals for the current month"""
    today = timezone.now().date()
    return get_monthly_invoice_totals_client(today.year, today.month,client)