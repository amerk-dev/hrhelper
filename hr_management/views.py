import csv
from decimal import Decimal, ROUND_HALF_UP

from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin # Для контроля доступа
# PermissionRequiredMixin требует, чтобы у пользователя было определенное разрешение
# Например: 'hr_management.add_department'

from .models import Department, Employee, EmployeePerformance, BonusCalculationSettings
from .forms import DepartmentForm, EmployeeForm, BonusCalculationForm


# --- Department Views ---
class DepartmentListView(LoginRequiredMixin, ListView):
    model = Department
    template_name = 'hr_management/department_list.html' # Укажем путь к шаблону
    context_object_name = 'departments'

class DepartmentDetailView(LoginRequiredMixin, DetailView):
    model = Department
    template_name = 'hr_management/department_detail.html'
    context_object_name = 'department'

class DepartmentCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView): # Пример с PermissionRequiredMixin
    model = Department
    form_class = DepartmentForm
    template_name = 'hr_management/department_form.html'
    success_url = reverse_lazy('hr_management:department-list') # Куда перенаправить после успеха
    permission_required = 'hr_management.add_department'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = "Добавить подразделение"
        context['button_text'] = "Сохранить"
        return context

class DepartmentUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Department
    form_class = DepartmentForm
    template_name = 'hr_management/department_form.html'
    success_url = reverse_lazy('hr_management:department-list')
    permission_required = 'hr_management.change_department'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = "Изменить подразделение"
        context['button_text'] = "Сохранить изменения"
        return context

class DepartmentDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Department
    template_name = 'hr_management/department_confirm_delete.html'
    success_url = reverse_lazy('hr_management:department-list')
    context_object_name = 'department'
    permission_required = 'hr_management.delete_department'

# --- Employee Views ---
# --- Employee Views ---
class EmployeeListView(LoginRequiredMixin, ListView):
    model = Employee
    template_name = 'hr_management/employee_list.html'
    context_object_name = 'employees'
    paginate_by = 10  # Добавим пагинацию для больших списков


class EmployeeDetailView(LoginRequiredMixin, DetailView):
    model = Employee
    template_name = 'hr_management/employee_detail.html'
    context_object_name = 'employee'


class EmployeeCreateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'hr_management/employee_form.html'
    # success_url = reverse_lazy('hr_management:employee-list') # Можно так, или через get_success_url
    permission_required = 'hr_management.add_employee'
    success_message = "Сотрудник \"%(full_name)s\" успешно добавлен."  # %(field_name)s

    def get_success_url(self):  # Перенаправляем на детали созданного сотрудника
        return reverse_lazy('hr_management:employee-detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = "Добавить нового сотрудника"
        context['button_text'] = "Добавить сотрудника"
        return context


class EmployeeUpdateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'hr_management/employee_form.html'
    permission_required = 'hr_management.change_employee'
    success_message = "Данные сотрудника \"%(full_name)s\" успешно обновлены."

    def get_success_url(self):  # Перенаправляем на детали обновленного сотрудника
        return reverse_lazy('hr_management:employee-detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = f"Редактировать данные: {self.object.full_name}"
        context['button_text'] = "Сохранить изменения"
        return context


class EmployeeDeleteView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Employee
    template_name = 'hr_management/employee_confirm_delete.html'
    success_url = reverse_lazy('hr_management:employee-list')
    context_object_name = 'employee'
    permission_required = 'hr_management.delete_employee'

    # Сообщение об успехе для DeleteView нужно определять в методе delete или использовать кастомный миксин

    def get_success_message(self, cleaned_data):  # Этот метод не вызовется для DeleteView по умолчанию
        return f"Сотрудник \"{self.object.full_name}\" успешно удален."

    # Для DeleteView SuccessMessageMixin работает немного иначе,
    # обычно сообщение добавляют в методе post или delete.
    # Но можно и так, если переопределить form_valid, но для DeleteView это не form_valid
    # Проще всего будет добавить сообщение через Django Messages API в методе delete
    # from django.contrib import messages
    # def delete(self, request, *args, **kwargs):
    #     obj_name = self.get_object().full_name
    #     messages.success(self.request, f"Сотрудник \"{obj_name}\" успешно удален.")
    #     return super().delete(request, *args, **kwargs)


class CalculateBonusView(LoginRequiredMixin, PermissionRequiredMixin, View):
    template_name = 'hr_management/bonus_calculation.html'
    form_class = BonusCalculationForm
    permission_required = ('hr_management.view_employee', 'hr_management.view_kpi')  # Пример прав

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        bonus_results = []
        total_calculated_bonus = Decimal('0.00')
        calculation_summary = {}  # Для общей информации: бюджет, всего премий

        if form.is_valid():
            employee_param = form.cleaned_data.get('employee')
            department_param = form.cleaned_data.get('department')
            year = form.cleaned_data.get('period_year')
            month = form.cleaned_data.get('period_month')

            employees_to_calculate = Employee.objects.none()

            if employee_param:
                employees_to_calculate = Employee.objects.filter(pk=employee_param.pk)
                target_department = employee_param.department
            elif department_param:
                employees_to_calculate = Employee.objects.filter(department=department_param)
                target_department = department_param
            else:  # Этого не должно быть из-за валидации формы, но на всякий случай
                return render(request, self.template_name,
                              {'form': form, 'error': 'Не выбран сотрудник или подразделение'})

            # Получаем общий премиальный фонд, если он есть
            bonus_settings = BonusCalculationSettings.objects.filter(
                department=target_department if target_department else None,  # Если фонд общий, department=None
                period_year=year,
                period_month=month
            ).first()

            calculation_summary['bonus_pool'] = bonus_settings.total_bonus_pool if bonus_settings else None
            calculation_summary['period'] = f"{month:02d}/{year}"
            calculation_summary['target_entity'] = employee_param or target_department

            for emp in employees_to_calculate.filter(tariff_rate__isnull=False):
                if not emp.assigned_kpis.exists():  # <--- ПРОВЕРКА НАЗНАЧЕННЫХ KPI
                    bonus_results.append({
                        'employee_name': emp.full_name,
                        'tariff_rate': emp.tariff_rate,
                        'kpi_details': [],
                        'integral_coefficient_c': Decimal('0.00'),
                        'calculated_bonus': Decimal('0.00'),
                        'error': 'Сотруднику не назначены KPI для оценки.'
                    })
                    continue

                integral_coefficient_c = Decimal('0.00')
                kpi_details_for_template = []
                all_assigned_kpis_have_performance = True  # Флаг для проверки

                for assigned_kpi_obj in emp.assigned_kpis.all():  # <--- ИТЕРИРУЕМСЯ ПО НАЗНАЧЕННЫМ KPI
                    performance = EmployeePerformance.objects.filter(
                        employee=emp,
                        kpi=assigned_kpi_obj,  # <--- ИЩЕМ ДАННЫЕ ДЛЯ КОНКРЕТНОГО НАЗНАЧЕННОГО KPI
                        period_year=year,
                        period_month=month
                    ).first()  # Ожидаем одну запись или None

                    achievement_percentage_decimal = Decimal('0.00')
                    actual_val_for_tpl = None
                    planned_val_for_tpl = None

                    if performance:
                        actual_val_for_tpl = performance.actual_value
                        planned_val_for_tpl = performance.planned_value
                        if performance.planned_value and performance.planned_value != Decimal('0'):
                            achievement_percentage_decimal = (performance.actual_value / performance.planned_value)
                        # Если planned_value = 0, а actual_value > 0, это может быть 100% или специальная логика
                        elif performance.planned_value == Decimal('0') and performance.actual_value > Decimal('0'):
                            achievement_percentage_decimal = Decimal('1.0')  # Например, если план 0, а факт есть - 100%
                    else:
                        # Если для назначенного KPI нет записи о выполнении
                        all_assigned_kpis_have_performance = False  # Отмечаем, что не все данные есть
                        # achievement_percentage_decimal остается 0.00
                        # Можно здесь добавить сообщение в kpi_details_for_template, что нет данных

                    # Ограничение: например, не более 200% (2.0)
                    achievement_percentage_decimal = min(achievement_percentage_decimal, Decimal('2.0'))

                    weighted_achievement = achievement_percentage_decimal * assigned_kpi_obj.weight  # Используем вес из объекта KPI
                    integral_coefficient_c += weighted_achievement

                    kpi_details_for_template.append({
                        'name': assigned_kpi_obj.name,
                        'weight': assigned_kpi_obj.weight,
                        'planned': planned_val_for_tpl,
                        'actual': actual_val_for_tpl,
                        'achievement_percent': achievement_percentage_decimal * 100,
                        'weighted_achievement_points': weighted_achievement,
                        'has_data': bool(performance)  # Флаг, были ли данные по этому KPI
                    })

                integral_coefficient_c = integral_coefficient_c.quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)
                calculated_bonus = (emp.tariff_rate * integral_coefficient_c).quantize(Decimal('0.01'),
                                                                                       rounding=ROUND_HALF_UP)

                employee_result = {
                    'employee_name': emp.full_name,
                    'tariff_rate': emp.tariff_rate,
                    'kpi_details': kpi_details_for_template,
                    'integral_coefficient_c': integral_coefficient_c,
                    'calculated_bonus': calculated_bonus,
                }
                if not all_assigned_kpis_have_performance:
                    employee_result[
                        'warning'] = 'Не для всех назначенных KPI найдены данные о выполнении за период. Расчет произведен по имеющимся данным (отсутствующие KPI считаются выполненными на 0%).'

                bonus_results.append(employee_result)
                total_calculated_bonus += calculated_bonus

            calculation_summary['total_calculated_bonus'] = total_calculated_bonus
            if calculation_summary['bonus_pool'] is not None:
                calculation_summary['pool_vs_calculated_diff'] = calculation_summary[
                                                                     'bonus_pool'] - total_calculated_bonus

        return render(request, self.template_name, {
            'form': form,
            'bonus_results': bonus_results,
            'calculation_summary': calculation_summary
        })



class ReportSelectionView(LoginRequiredMixin, PermissionRequiredMixin, View):
    template_name = 'hr_management/report_selection.html'
    permission_required = ('hr_management.view_employee', 'hr_management.view_department') # Примерные права

    def get(self, request, *args, **kwargs):
        # Если бы были фильтры, здесь бы инициализировалась форма
        # form = ReportFilterForm()
        # return render(request, self.template_name, {'form': form})
        return render(request, self.template_name)


class EmployeeReportCSVView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'hr_management.view_employee' # Пользователь должен иметь право просматривать сотрудников

    def get(self, request, *args, **kwargs):
        # Создаем HttpResponse с типом CSV
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': f'attachment; filename="employee_report_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'},
        )
        response.write(u'\ufeff'.encode('utf8')) # BOM для корректного отображения кириллицы в Excel

        writer = csv.writer(response, delimiter=';') # Используем точку с запятой как разделитель

        # Заголовки CSV файла
        header = [
            'ФИО', 'Возраст', 'Пол', 'Семейное положение',
            'Подразделение', 'Должность', 'Разряд',
            'Дата начала работы', 'Дата окончания работы'
        ]
        writer.writerow(header)

        # Получаем данные сотрудников
        # Для ТЗ нужны фильтры по дате, но начнем без них для простоты
        # start_date_filter = request.GET.get('start_date')
        # end_date_filter = request.GET.get('end_date')
        # employees = Employee.objects.all()
        # if start_date_filter:
        #     employees = employees.filter(start_date__gte=start_date_filter)
        # if end_date_filter:
        #     employees = employees.filter(Q(end_date__lte=end_date_filter) | Q(end_date__isnull=True)) # немного сложнее логика с end_date

        employees = Employee.objects.select_related('department').all()

        for emp in employees:
            writer.writerow([
                emp.full_name,
                emp.age, # @property
                emp.get_gender_display(),
                emp.get_marital_status_display(),
                emp.department.name if emp.department else '-',
                emp.position,
                emp.grade if emp.grade is not None else '-',
                emp.start_date.strftime('%d.%m.%Y') if emp.start_date else '-',
                emp.end_date.strftime('%d.%m.%Y') if emp.end_date else 'Работает'
            ])

        return response