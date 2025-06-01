from django.contrib import admin
from .models import Department, Employee, KPI, EmployeePerformance, BonusCalculationSettings

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_name', 'code', 'allocated_units', 'min_grade', 'max_grade')
    search_fields = ('name', 'code')


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'department', 'position', 'grade', 'age', 'start_date', 'end_date',
                    'tariff_rate')  # добавил tariff_rate
    list_filter = ('department', 'gender', 'marital_status', 'grade')
    search_fields = ('full_name', 'position')
    date_hierarchy = 'start_date'
    readonly_fields = ('age',)
    filter_horizontal = ('assigned_kpis',)  # <--- ДЛЯ M2M ПОЛЯ

    fieldsets = (  # <--- Для лучшей организации полей в админке (опционально)
        (None, {
            'fields': ('full_name', 'birth_date', 'gender', 'marital_status')
        }),
        ('Работа', {
            'fields': ('department', 'position', 'grade', 'tariff_rate', 'start_date', 'end_date')
        }),
        ('Назначенные KPI', {  # <--- Отдельная секция для KPI
            'fields': ('assigned_kpis',)
        }),
    )

@admin.register(KPI)
class KPIAdmin(admin.ModelAdmin):
    list_display = ('name', 'weight', 'description')
    search_fields = ('name',)

@admin.register(EmployeePerformance)
class EmployeePerformanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'kpi', 'period_year', 'period_month', 'planned_value', 'actual_value')
    list_filter = ('period_year', 'period_month', 'kpi', 'employee__department')
    search_fields = ('employee__full_name', 'kpi__name')
    autocomplete_fields = ['employee', 'kpi'] # Для удобного выбора

@admin.register(BonusCalculationSettings)
class BonusCalculationSettingsAdmin(admin.ModelAdmin):
    list_display = ('department', 'period_year', 'period_month', 'total_bonus_pool')
    list_filter = ('period_year', 'period_month', 'department')