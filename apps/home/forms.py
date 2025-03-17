from django.contrib.admin.widgets import AdminDateWidget
from django import forms
from .models import Transaction

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ('date', 'category', 'amount', 'description')
        widgets = {
            'date': AdminDateWidget(),  # Добавляем календарь
        }