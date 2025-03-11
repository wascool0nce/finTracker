from datetime import timedelta

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db.models import Sum, Q
from django.db.models.functions import TruncMonth
from django.utils import timezone

class Category(models.Model):
    INCOME = 'income'
    EXPENSE = 'expense'
    TYPE_CHOICES = [
        (INCOME, 'Доход'),
        (EXPENSE, 'Расход'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, verbose_name="Название")
    type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES,
        verbose_name="Тип категории"
    )

    def __str__(self):
        return f"{self.get_type_display()} - {self.name}"

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name="Категория"
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name="Сумма"
    )
    date = models.DateField(
        default=timezone.now,
        verbose_name="Дата"
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Описание"
    )

    @property
    def transaction_type(self):
        return self.category.type

    def __str__(self):
        return f"{self.date} - {self.category.name}: {self.amount}"

    class Meta:
        verbose_name = "Транзакция"
        verbose_name_plural = "Транзакции"
        ordering = ['-date']

    @classmethod
    def get_monthly_balance(cls, user, months=6):

        """
        Возвращает разницу между доходами и расходами по месяцам.
        :param user: Пользователь, для которого запрашиваются данные
        :param months: Количество месяцев для анализа (по умолчанию 6)
        :return: Словарь с метками (месяцы) и данными (разница)
        """
        MONTH_TRANSLATIONS = {
            'Jan': 'Янв',
            'Feb': 'Фев',
            'Mar': 'Мар',
            'Apr': 'Апр',
            'May': 'Май',
            'Jun': 'Июн',
            'Jul': 'Июл',
            'Aug': 'Авг',
            'Sep': 'Сен',
            'Oct': 'Окт',
            'Nov': 'Ноя',
            'Dec': 'Дек'
        }
        # Определяем начальную и конечную даты
        monthly_data = cls.objects.filter(
            user=user,
            date__gte=timezone.now() - timedelta(days=30 * months)
        ).annotate(
            month=TruncMonth('date')
        ).values('month').annotate(
            income=Sum('amount', filter=Q(category__type='income')),
            expense=Sum('amount', filter=Q(category__type='expense'))
        ).order_by('month')

        # Форматируем месяцы и переводим их
        labels = [MONTH_TRANSLATIONS[entry['month'].strftime('%b')] for entry in monthly_data]
        data = [float((entry['income'] or 0) - (entry['expense'] or 0)) for entry in monthly_data]

        return {
            'labels': labels,
            'data': data
        }

class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        limit_choices_to={'type': Category.EXPENSE},
        verbose_name="Категория"
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name="Сумма бюджета"
    )
    start_date = models.DateField(
        verbose_name="Начало периода"
    )
    end_date = models.DateField(
        verbose_name="Конец периода"
    )

    def __str__(self):
        return f"{self.category.name} ({self.start_date} - {self.end_date})"

    class Meta:
        verbose_name = "Бюджет"
        verbose_name_plural = "Бюджеты"

class SavingsGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(
        max_length=255,
        verbose_name="Название цели"
    )
    target_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name="Целевая сумма"
    )
    current_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Текущая сумма"
    )
    target_date = models.DateField(
        verbose_name="Целевая дата"
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Описание"
    )

    def progress(self):
        return (self.current_amount / self.target_amount) * 100

    def __str__(self):
        return f"{self.name} - {self.progress():.1f}%"

    class Meta:
        verbose_name = "Цель накопления"
        verbose_name_plural = "Цели накопления"