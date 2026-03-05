
from django import forms
from django.utils import timezone
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
            'date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }
    
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is None:
            raise forms.ValidationError('El monto es obligatorio.')
        if amount <= 0:
            raise forms.ValidationError('El monto debe ser mayor que cero.')
        if amount > 1000000000:  # Límite razonable
            raise forms.ValidationError('El monto no puede superar $1,000,000,000.')
        return amount
    
    def clean_date(self):
        date = self.cleaned_data.get('date')
        if not date:
            raise forms.ValidationError('La fecha es obligatoria.')
        if date > timezone.now().date():
            raise forms.ValidationError('La fecha no puede ser futura.')
        return date
    
    def clean_category(self):
        category = self.cleaned_data.get('category')
        if not category:
            raise forms.ValidationError('La categoría es obligatoria.')
        return category
    
    def clean_description(self):
        description = self.cleaned_data.get('description')
        if description and len(description) > 500:
            raise forms.ValidationError('La descripción no puede exceder 500 caracteres.')
        return description
    
    def clean_receipt(self):
        receipt = self.cleaned_data.get('receipt')
        if receipt:
            # Validar tamaño (máximo 5MB)
            if receipt.size > 5 * 1024 * 1024:
                raise forms.ValidationError('El archivo no puede superar 5MB.')
            
            # Validar tipo de archivo
            allowed_types = ['image/jpeg', 'image/png', 'image/jpg', 'application/pdf']
            if receipt.content_type not in allowed_types:
                raise forms.ValidationError('Solo se permiten imágenes (JPG, PNG) o archivos PDF.')
            
            # Validar extensión
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.pdf']
            import os
            ext = os.path.splitext(receipt.name)[1].lower()
            if ext not in allowed_extensions:
                raise forms.ValidationError('Extensión de archivo no permitida.')
        return receipt
