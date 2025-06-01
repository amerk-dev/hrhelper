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
        # Можно добавить уникальность, если ФИО+дата рождения должны быть уникальны
        # unique_together = [['full_name', 'birth_date']]