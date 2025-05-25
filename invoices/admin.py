from django.contrib import admin
from invoices.models import Invoice,InvoiceItem

# Register your models here.
admin.site.register(Invoice)
admin.site.register(InvoiceItem)
#admin.site.register(Invoice)
