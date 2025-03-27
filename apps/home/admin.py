# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
# Register your models here.
from django.contrib import admin

from apps.home.forms import TransactionForm, CategoryForm
from apps.home.models import Category, Transaction, Budget, SavingsGoal

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'type')  # Поля, отображаемые в списке
    list_filter = ('type',)  # Фильтры в правой части админки
    search_fields = ('name',)  # Поля для поиска
    ordering = ('type', 'name')  # Сортировка по умолчанию
    form = CategoryForm

    def get_queryset(self, request):
        # Суперпользователь видит все, остальные — только свои объекты
        qs = super().get_queryset(request)
        # if request.user.is_superuser:
        #     return qs
        return qs.filter(user=request.user)

    def save_model(self, request, obj, form, change):
        # Автоматически назначаем пользователя при создании объекта
        if not obj.pk:
            obj.user = request.user
        super().save_model(request, obj, form, change)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('date', 'category', 'amount', 'get_transaction_type')
    list_filter = ('category__type', 'date')
    search_fields = ('description', 'category__name')
    date_hierarchy = 'date'
    ordering = ('-date',)
    form = TransactionForm  # Указываем нашу форму

    # Убираем поле user из формы
    exclude = ('user',)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        class CustomForm(form):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.fields['category'].queryset = Category.objects.filter(user=request.user)

        return CustomForm

    def get_queryset(self, request):
        # Суперпользователь видит все, остальные — только свои объекты
        qs = super().get_queryset(request)
        # if request.user.is_superuser:
        #     return qs
        return qs.filter(user=request.user)

    def get_transaction_type(self, obj):
        return "Доход" if obj.transaction_type == "income" else "Расход"

    get_transaction_type.short_description = "Тип транзакции"

    def save_model(self, request, obj, form, change):
        # Автоматически назначаем пользователя при создании объекта
        if not obj.pk:
            obj.user = request.user
        super().save_model(request, obj, form, change)

# @admin.register(Budget)
# class BudgetAdmin(admin.ModelAdmin):
#     list_display = ('category', 'amount', 'start_date', 'end_date', 'user')  # Отображаемые поля
#     list_filter = ('category__type', 'user')  # Фильтры
#     search_fields = ('category__name',)  # Поиск по названию категории
#     date_hierarchy = 'start_date'  # Иерархия по дате начала
#     ordering = ('-start_date',)  # Сортировка по дате начала
#
# @admin.register(SavingsGoal)
# class SavingsGoalAdmin(admin.ModelAdmin):
#     list_display = ('name', 'target_amount', 'current_amount', 'progress', 'target_date', 'user')  # Отображаемые поля
#     list_filter = ('user',)  # Фильтры
#     search_fields = ('name',)  # Поиск по названию цели
#     date_hierarchy = 'target_date'  # Иерархия по целевой дате
#     ordering = ('-target_date',)  # Сортировка по целевой дате
#
#     # Добавляем вычисляемое поле progress в админку
#     readonly_fields = ('progress',)  # Поле только для чтения
#
#     def progress(self, obj):
#         return f"{obj.progress():.1f}%"
#     progress.short_description = "Прогресс"  # Название колонки