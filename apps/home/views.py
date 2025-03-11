# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from datetime import timedelta

from django import template
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.utils import timezone

from apps.home.models import Transaction


@login_required(login_url="/login/")
def index(request):
    # Получаем данные за последние 6 месяцев
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=180)  # 6 месяцев назад

    # Агрегируем доходы по месяцам
    monthly_income = Transaction.objects.filter(
        user=request.user,
        category__type='income',  # Фильтруем только доходы
        date__gte=start_date,
        date__lte=end_date
    ).annotate(
        month=TruncMonth('date')  # Группируем по месяцам
    ).values('month').annotate(
        total_income=Sum('amount')  # Суммируем доходы
    ).order_by('month')

    # Агрегируем расходы по месяцам
    monthly_expense = Transaction.objects.filter(
        user=request.user,
        category__type='expense',  # Фильтруем только расходы
        date__gte=start_date,
        date__lte=end_date
    ).annotate(
        month=TruncMonth('date')  # Группируем по месяцам
    ).values('month').annotate(
        total_expense=Sum('amount')  # Суммируем расходы
    ).order_by('month')

    # Подготавливаем данные для графиков
    labels = [entry['month'].strftime('%b') for entry in monthly_income]  # Месяцы
    income_data = [float(entry['total_income'] or 0) for entry in monthly_income]  # Доходы
    expense_data = [float(entry['total_expense'] or 0) for entry in monthly_expense]  # Расходы

    start_date = timezone.now().replace(day=1).date()  # Первый день текущего месяца
    end_date = timezone.now().date()  # Сегодняшняя дата

    # Агрегируем расходы по категориям за текущий месяц
    category_expenses = Transaction.objects.filter(
        user=request.user,
        category__type='expense',  # Фильтруем только расходы
        date__gte=start_date,
        date__lte=end_date
    ).values('category__name').annotate(
        total_expense=Sum('amount')  # Суммируем расходы по категориям
    ).order_by('-total_expense')  # Сортируем по убыванию

    # Подготавливаем данные для графика
    labels_category = [entry['category__name'] for entry in category_expenses]  # Названия категорий
    data = [float(entry['total_expense'] or 0) for entry in category_expenses]  # Суммы расходов
    # Данные для баланса (доходы - расходы)
    monthly_balance = Transaction.get_monthly_balance(request.user, months=6)

    # Подготавливаем данные для графиков
    context = {
        'main_chart': {
            'labels': monthly_balance['labels'],
            'datasets': [{
                'label': 'Баланс (доходы - расходы)',
                'data': monthly_balance['data'],
                'borderColor': '#d346b1',
                'pointBackgroundColor': '#d346b1',
                'borderWidth': 2,
                'fill': True
            }]
        },
        'income_chart': {
            'labels': labels,
            'datasets': [{
                'label': 'Доходы',
                'data': income_data,
                'borderColor': '#00d6b4',  # Зеленый для доходов
                'pointBackgroundColor': '#00d6b4',
                'borderWidth': 2,
                'fill': True
            }]
        },
        'expense_chart': {
            'labels': labels,
            'datasets': [{
                'label': 'Расходы',
                'data': expense_data,
                'borderColor': '#f44336',  # Красный для расходов
                'pointBackgroundColor': '#f44336',
                'borderWidth': 2,
                'fill': True
            }]
        },
        'category_chart': {
            'labels': labels_category,
            'datasets': [{
                'label': 'Расходы по категориям',
                'data': data,
                'backgroundColor': '#1f8ef1',  # Синий цвет
                'borderColor': '#1f8ef1',
                'borderWidth': 2,
            }]
        },
    }

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))


