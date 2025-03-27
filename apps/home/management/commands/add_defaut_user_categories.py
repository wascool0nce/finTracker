import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.home.models import Category, Transaction  # Замените your_app на имя вашего приложения

User = get_user_model()


class Command(BaseCommand):
    help = 'Заполняет базу данных тестовыми категориями и транзакциями'

    def handle(self, *args, **options):
        self.stdout.write("Создание тестовых данных...")

        # Создаем тестового пользователя, если его нет
        user, created = User.objects.get_or_create(
            username='Maxim',
        )
        if created:
            user.set_password('testpass123')
            user.save()
            self.stdout.write(self.style.SUCCESS('Создан тестовый пользователь: test_user'))

        # Создаем категории
        income_categories = [
            ('Зарплата', 'Доход от основной работы'),
            ('Фриланс', 'Дополнительный доход'),
            ('Инвестиции', 'Доход от инвестиций'),
            ('Подарки', 'Денежные подарки'),
            ('Возврат долгов', 'Возвращенные деньги')
        ]

        expense_categories = [
            ('Продукты', 'Покупка продуктов питания'),
            ('Транспорт', 'Транспортные расходы'),
            ('Жилье', 'Аренда и коммунальные услуги'),
            ('Развлечения', 'Кино, концерты и т.д.'),
            ('Одежда', 'Покупка одежды и обуви'),
            ('Здоровье', 'Медицинские расходы'),
            ('Образование', 'Курсы, книги и т.д.'),
            ('Кафе и рестораны', 'Питание вне дома'),
            ('Путешествия', 'Расходы на поездки'),
            ('Техника', 'Покупка электроники')
        ]

        created_categories = {
            'income': {},
            'expense': {}
        }

        for name, desc in income_categories:
            cat, created = Category.objects.get_or_create(
                user=user,
                name=name,
                defaults={
                    'type': Category.INCOME,
                }
            )
            created_categories['income'][name] = cat

        for name, desc in expense_categories:
            cat, created = Category.objects.get_or_create(
                user=user,
                name=name,
                defaults={
                    'type': Category.EXPENSE,
                }
            )
            created_categories['expense'][name] = cat

        self.stdout.write(self.style.SUCCESS('Созданы категории доходов и расходов'))

        # Создаем транзакции за последние 6 месяцев
        for i in range(6):
            month_ago = timezone.now() - timedelta(days=30 * i)

            # Доходы
            Transaction.objects.create(
                user=user,
                category=created_categories['income']['Зарплата'],
                amount=random.randint(80000, 120000),
                date=month_ago.replace(day=5),
                description='Зарплата за месяц'
            )

            if i % 2 == 0:
                Transaction.objects.create(
                    user=user,
                    category=created_categories['income']['Фриланс'],
                    amount=random.randint(10000, 30000),
                    date=month_ago.replace(day=15),
                    description='Проект для клиента'
                )

            # Расходы
            Transaction.objects.create(
                user=user,
                category=created_categories['expense']['Продукты'],
                amount=random.randint(15000, 25000),
                date=month_ago.replace(day=10),
                description='Продукты на неделю'
            )

            Transaction.objects.create(
                user=user,
                category=created_categories['expense']['Транспорт'],
                amount=random.randint(3000, 8000),
                date=month_ago.replace(day=12),
                description='Проездной и такси'
            )

            Transaction.objects.create(
                user=user,
                category=created_categories['expense']['Жилье'],
                amount=random.randint(30000, 40000),
                date=month_ago.replace(day=1),
                description='Аренда квартиры'
            )

            if i % 3 == 0:
                Transaction.objects.create(
                    user=user,
                    category=created_categories['expense']['Развлечения'],
                    amount=random.randint(5000, 15000),
                    date=month_ago.replace(day=20),
                    description='Поход в кино'
                )

        self.stdout.write(self.style.SUCCESS(
            f'Успешно созданы тестовые данные: '
            f'{Category.objects.filter(user=user).count()} категорий и '
            f'{Transaction.objects.filter(user=user).count()} транзакций'
        ))