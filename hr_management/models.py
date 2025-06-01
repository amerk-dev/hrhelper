from decimal import Decimal

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.contrib.auth.models import User  # Для привязки пользователей


class Department(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name="Название подразделения")
    short_name = models.CharField(max_length=50, blank=True, null=True, verbose_name="Краткое название")
    code = models.CharField(max_length=20, blank=True, null=True, verbose_name="Шифр")
    min_grade = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        blank=True, null=True,
        verbose_name="Нижняя граница разряда (ЕТС)"
    )
    max_grade = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        blank=True, null=True,
        verbose_name="Верхняя граница разряда (ЕТС)"
    )
    allocated_units = models.PositiveIntegerField(default=0, verbose_name="Кол-во выделенных штатных единиц")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Подразделение"
        verbose_name_plural = "Подразделения"
        ordering = ['name']

class KPI(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Название KPI")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    # unit = models.CharField(max_length=50, blank=True, null=True, verbose_name="Единица измерения") # например, %, шт, руб.
    weight = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],  # Вес должен быть положительным
        default=Decimal('1.0'),
        verbose_name="Вес KPI (в долях от 1)"
    )  # Вес этого KPI в общей оценке

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Показатель эффективности (KPI)"
        verbose_name_plural = "Показатели эффективности (KPI)"
        ordering = ['name']


class Employee(models.Model):
    GENDER_CHOICES = [
        ('M', 'Мужской'),
        ('F', 'Женский'),
    ]
    MARITAL_STATUS_CHOICES = [
        ('SINGLE', 'Холост/Не замужем'),
        ('MARRIED', 'Женат/Замужем'),
        ('DIVORCED', 'Разведен(а)'),
        ('WIDOWED', 'Вдовец/Вдова'),
    ]

    full_name = models.CharField(max_length=255, verbose_name="ФИО")
    birth_date = models.DateField(verbose_name="Дата рождения")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name="Пол")
    marital_status = models.CharField(max_length=10, choices=MARITAL_STATUS_CHOICES, verbose_name="Семейное положение")

    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,  # При удалении подразделения, поле у сотрудника станет NULL
        null=True, blank=True,  # Сотрудник может быть без подразделения (временно)
        related_name='employees',
        verbose_name="Подразделение"
    )
    position = models.CharField(max_length=150, verbose_name="Должность")
    grade = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        blank=True, null=True,
        verbose_name="Разряд"
    )
    tariff_rate = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        verbose_name="Тарифная ставка (оклад)"
    )  # Добавили тарифную ставку
    assigned_kpis = models.ManyToManyField(  # <--- НОВОЕ ПОЛЕ
        KPI,
        blank=True,  # Сотруднику могут быть еще не назначены KPI
        verbose_name="Назначенные KPI",
        related_name="assigned_to_employees"
    )
    start_date = models.DateField(verbose_name="Дата начала работы")
    end_date = models.DateField(blank=True, null=True, verbose_name="Дата окончания работы")

    # user_account = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Учетная запись пользователя")
    # Поле user_account можно добавить, если каждому сотруднику нужно сопоставить пользователя системы Django

    @property
    def age(self):
        today = timezone.now().date()
        return today.year - self.birth_date.year - (
                    (today.month, today.day) < (self.birth_date.month, self.birth_date.day))

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = "Сотрудник (Кадр)"
        verbose_name_plural = "Сотрудники (Кадры)"
        ordering = ['full_name']
        unique_together = [['full_name', 'birth_date']]




class EmployeePerformance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="performance_records",
                                 verbose_name="Сотрудник")
    kpi = models.ForeignKey(KPI, on_delete=models.CASCADE, verbose_name="Показатель KPI")
    period_year = models.PositiveIntegerField(verbose_name="Год периода")
    # Можно использовать месяц или квартал
    period_month = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)],
        verbose_name="Месяц периода"
    )
    # или period_quarter = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(4)], verbose_name="Квартал периода")

    planned_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True,
                                        verbose_name="Плановое значение")
    actual_value = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Фактическое значение")

    # achievement_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="% выполнения")
    # Можно вычислять на лету или хранить

    # @property
    # def achievement_percentage_calc(self):
    #     if self.planned_value and self.planned_value != Decimal(0):
    #         return round((self.actual_value / self.planned_value) * 100, 2)
    #     return None

    def __str__(self):
        return f"{self.employee.full_name} - {self.kpi.name} ({self.period_month}/{self.period_year})"

    class Meta:
        verbose_name = "Результат KPI сотрудника"
        verbose_name_plural = "Результаты KPI сотрудников"
        unique_together = [
            ['employee', 'kpi', 'period_year', 'period_month']]  # Гарантирует одну запись для KPI сотрудника за период
        ordering = ['-period_year', '-period_month', 'employee', 'kpi']


class BonusCalculationSettings(models.Model):  # Настройки для расчета премий (опционально, но полезно)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True,
                                   verbose_name="Подразделение (если бюджет по подразделениям)")
    period_year = models.PositiveIntegerField(verbose_name="Год периода")
    period_month = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)],
                                               verbose_name="Месяц периода")
    total_bonus_pool = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Общий премиальный фонд (S)")

    # Здесь можно добавить правила для расчета коэффициента C, если они сложные

    def __str__(self):
        dep_name = self.department.name if self.department else "Общий"
        return f"Фонд премий для {dep_name} ({self.period_month}/{self.period_year})"

    class Meta:
        verbose_name = "Настройка расчета премий"
        verbose_name_plural = "Настройки расчета премий"
        unique_together = [['department', 'period_year', 'period_month']]