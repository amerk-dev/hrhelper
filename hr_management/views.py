from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin # Для контроля доступа
# PermissionRequiredMixin требует, чтобы у пользователя было определенное разрешение
# Например: 'hr_management.add_department'

from .models import Department, Employee
from .forms import DepartmentForm, EmployeeForm

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