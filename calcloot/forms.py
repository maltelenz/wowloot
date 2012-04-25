from django import forms
from calcloot.models import *

class HomeForm(forms.ModelForm):
    class Meta:
        model = Calculation
        exclude = ('involved',)

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        exclude = ('calculation', 'benefactors',)
        widgets = {
            'amount': forms.TextInput(attrs={'size': '8'}),
            'name': forms.TextInput(attrs={'size': '25'}),
            }

class AddPersonForm(forms.Form):
    name = forms.CharField(max_length = 200)
