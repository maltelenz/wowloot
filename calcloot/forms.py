from django.forms import ModelForm
from calcloot.models import *

class HomeForm(ModelForm):
    class Meta:
        model = Calculation

class ExpenseForm(ModelForm):
    class Meta:
        model = Expense
        exclude = ('calculation',)
