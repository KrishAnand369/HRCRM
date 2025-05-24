from django import forms
from .models import Invoice
from CRM.models import Client

class InvoiceForm(forms.ModelForm):
    due_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True
    )
    
    class Meta:
        model = Invoice
        fields = ['client', 'due_date', 'status', 'terms', 'notes']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['client'].queryset = Client.objects.order_by('company_name')