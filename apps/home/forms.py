from django.contrib.admin.widgets import AdminDateWidget
from django import forms
from .models import Transaction, Category


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ('date', 'category', 'amount', 'description')
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            # или для виджета из админки:
            # 'date': admin.widgets.AdminDateWidget(),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Достаём пользователя из аргументов
        super().__init__(*args, **kwargs)
        if user:
            self.fields['category'].queryset = Category.objects.filter(user=user)


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('name', 'type')