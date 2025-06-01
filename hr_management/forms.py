from django import forms
from .models import Department, Employee


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = '__all__'  # Включаем все поля
        # Или перечислить конкретные: ['name', 'short_name', ...]
        widgets = {  # Для улучшения интерфейса можно использовать виджеты
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'short_name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'min_grade': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_grade': forms.NumberInput(attrs={'class': 'form-control'}),
            'allocated_units': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def clean_name(self):  # Пример валидации на дубликаты (хотя unique=True в модели уже есть)
        name = self.cleaned_data.get('name')
        # Если это форма редактирования, исключаем текущий объект из проверки
        instance_pk = self.instance.pk if self.instance else None
        if Department.objects.filter(name=name).exclude(pk=instance_pk).exists():
            raise forms.ValidationError("Подразделение с таким названием уже существует.")
        return name


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = '__all__'  # ['full_name', 'birth_date', ...]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'marital_status': forms.Select(attrs={'class': 'form-select'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'grade': forms.NumberInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        # Валидация на пустые поля (required=True по умолчанию для полей модели, если не указано blank=False)
        # Валидация на дубликаты ФИО (если нужно, можно добавить метод clean_full_name или использовать unique_together в модели)