from django.contrib import admin
from .models import Department, Employee

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_name', 'code', 'allocated_units', 'min_grade', 'max_grade')
    search_fields = ('name', 'code')

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'department', 'position', 'grade', 'age', 'start_date', 'end_date')
    list_filter = ('department', 'gender', 'marital_status', 'grade')
    search_fields = ('full_name', 'position')
    date_hierarchy = 'start_date'

    readonly_fields = ('age',) # Поле age вычисляемое