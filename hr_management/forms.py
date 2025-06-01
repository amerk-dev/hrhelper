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
        fields = [
            'full_name', 'birth_date', 'gender', 'marital_status',
            'department', 'position', 'grade', 'start_date', 'end_date'
        ]  # Явно перечисляем поля для лучшего контроля

        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Иванов Иван Иванович'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            # type='date' для HTML5 Date Picker
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'marital_status': forms.Select(attrs={'class': 'form-select'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'position': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Например, Менеджер'}),
            'grade': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '10'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        # Можно добавить кастомные сообщения об ошибках или labels, если нужно
        labels = {
            'full_name': 'Полное имя (ФИО)',
            'birth_date': 'Дата рождения',
            # ... и так далее для других полей
        }
        help_texts = {
            'end_date': 'Оставьте пустым, если сотрудник все еще работает.',
        }

    def clean(self):  # Кастомная валидация для формы
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date and end_date < start_date:
            self.add_error('end_date', "Дата окончания работы не может быть раньше даты начала работы.")

        # Валидация на уникальность ФИО + дата рождения (если не используется unique_together в модели)
        # full_name = cleaned_data.get("full_name")
        # birth_date = cleaned_data.get("birth_date")
        # if full_name and birth_date:
        #     query = Employee.objects.filter(full_name=full_name, birth_date=birth_date)
        #     if self.instance and self.instance.pk: # Если это редактирование, исключаем текущий объект
        #         query = query.exclude(pk=self.instance.pk)
        #     if query.exists():
        #         self.add_error('full_name', "Сотрудник с таким ФИО и датой рождения уже существует.")
        #         # или self.add_error(None, "Сотрудник...") для не-полевой ошибки

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Делаем поле 'department' не обязательным на уровне формы, если оно blank=True, null=True в модели
        # self.fields['department'].required = False
        # (Django ModelForm обычно делает это автоматически на основе blank= атрибута модели)

        # Если подразделения должны быть отфильтрованы или упорядочены особым образом
        self.fields['department'].queryset = Department.objects.order_by('name')