from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Expense
from .forms import ExpenseForm
from roles.decorators import permission_required
from django.utils.decorators import method_decorator

@method_decorator(permission_required('expenses', 'ver'), name='dispatch')
class ExpenseListView(ListView):
    model = Expense
    template_name = 'expenses/expense_list.html'
    context_object_name = 'expenses'

@method_decorator(permission_required('expenses', 'crear'), name='dispatch')
class ExpenseCreateView(CreateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'expenses/expense_form.html'
    success_url = reverse_lazy('expenses:expense_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

@method_decorator(permission_required('expenses', 'editar'), name='dispatch')
class ExpenseUpdateView(UpdateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'expenses/expense_form.html'
    success_url = reverse_lazy('expenses:expense_list')

@method_decorator(permission_required('expenses', 'eliminar'), name='dispatch')
class ExpenseDeleteView(DeleteView):
    model = Expense
    template_name = 'expenses/expense_confirm_delete.html'
    success_url = reverse_lazy('expenses:expense_list')