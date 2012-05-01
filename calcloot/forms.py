from django import forms
from calcloot.models import *

class HomeForm(forms.ModelForm):
    class Meta:
        model = Calculation
        fields = ('name',)

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

class ShareForm(forms.Form):
    address = forms.EmailField(widget = forms.TextInput(attrs={'size': '50'}))

class ChangeCurrencyForm(forms.ModelForm):
    class Meta:
        model = Calculation
        fields = ('currency',)
