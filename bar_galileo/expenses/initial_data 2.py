
from .models import ExpenseCategory

def create_expense_categories():
    categories = ['Gastos Operativos', 'Gastos Extraordinarios']
    for category in categories:
        ExpenseCategory.objects.get_or_create(name=category)
