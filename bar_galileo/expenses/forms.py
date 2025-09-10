
from django import forms
from .models import Expense

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['date', 'amount', 'category', 'description', 'receipt']
        labels = {
            'date': 'Fecha',
            'amount': 'Monto',
            'category': 'Categoría',
            'description': 'Descripción',
            'receipt': 'Recibo',
        }
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }
