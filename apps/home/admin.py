# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
# Register your models here.
from django.contrib import admin
from apps.home.models import Category, Transaction, Budget, SavingsGoal

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'user')  # Поля, отображаемые в списке
    list_filter = ('type', 'user')  # Фильтры в правой части админки
    search_fields = ('name',)  # Поля для поиска
    ordering = ('type', 'name')  # Сортировка по умолчанию

    def get_queryset(self, request):
        # Суперпользователь видит все, остальные — только свои объекты
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    def save_model(self, request, obj, form, change):
        # Автоматически назначаем пользователя при создании объекта
        if not obj.pk:
            obj.user = request.user
        super().save_model(request, obj, form, change)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('date', 'category', 'amount', 'user', 'transaction_type')  # Отображаемые поля
    list_filter = ('category__type', 'date', 'user')  # Фильтры
    search_fields = ('description', 'category__name')  # Поиск по описанию и названию категории
    date_hierarchy = 'date'  # Иерархия по дате
    ordering = ('-date',)  # Сортировка по дате (новые сверху)

    def get_queryset(self, request):
        # Суперпользователь видит все, остальные — только свои объекты
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    def save_model(self, request, obj, form, change):
        # Автоматически назначаем пользователя при создании объекта
        if not obj.pk:
            obj.user = request.user
        super().save_model(request, obj, form, change)

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('category', 'amount', 'start_date', 'end_date', 'user')  # Отображаемые поля
    list_filter = ('category__type', 'user')  # Фильтры
    search_fields = ('category__name',)  # Поиск по названию категории
    date_hierarchy = 'start_date'  # Иерархия по дате начала
    ordering = ('-start_date',)  # Сортировка по дате начала

@admin.register(SavingsGoal)
class SavingsGoalAdmin(admin.ModelAdmin):
    list_display = ('name', 'target_amount', 'current_amount', 'progress', 'target_date', 'user')  # Отображаемые поля
    list_filter = ('user',)  # Фильтры
    search_fields = ('name',)  # Поиск по названию цели
    date_hierarchy = 'target_date'  # Иерархия по целевой дате
    ordering = ('-target_date',)  # Сортировка по целевой дате

    # Добавляем вычисляемое поле progress в админку
    readonly_fields = ('progress',)  # Поле только для чтения

    def progress(self, obj):
        return f"{obj.progress():.1f}%"
    progress.short_description = "Прогресс"  # Название колонки