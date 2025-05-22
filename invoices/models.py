from django.db import models

# Create your models here.
from django.db import models
from CRM.models import Client
from django.core.validators import MinValueValidator

class Invoice(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
    ]
    
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name='invoices')
    invoice_number = models.CharField(max_length=50, unique=True, editable=False)
    date_issued = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    notes = models.TextField(blank=True)
    terms = models.TextField(default="Payment due within 30 days")

    class Meta:
        ordering = ['-date_issued']

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = self.generate_invoice_number()
        super().save(*args, **kwargs)

    def generate_invoice_number(self):
        last_invoice = Invoice.objects.order_by('-id').first()
        if last_invoice:
            last_num = int(last_invoice.invoice_number.split('-')[-1])
            return f"INV-{last_num + 1:04d}"
        return "INV-0001"

    @property
    def total_amount(self):
        return sum(item.total for item in self.items.all())

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, related_name='items', on_delete=models.CASCADE)
    description = models.CharField(max_length=200)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    @property
    def total(self):
        return self.quantity * self.unit_price * (1 + self.tax_rate/100)