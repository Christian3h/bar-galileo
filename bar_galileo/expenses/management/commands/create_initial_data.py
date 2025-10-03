
from django.core.management.base import BaseCommand
from expenses.models import ExpenseCategory

class Command(BaseCommand):
    help = 'Creates the initial data for the expenses app'

    def handle(self, *args, **options):
        self.stdout.write('Creating expense categories...')
        categories = ['Gastos Operativos', 'Gastos Extraordinarios']
        for category in categories:
            ExpenseCategory.objects.get_or_create(name=category)
        self.stdout.write(self.style.SUCCESS('Successfully created expense categories'))
