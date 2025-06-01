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
class EmployeeListView(LoginRequiredMixin, ListView):
    model = Employee
    template_name = 'hr_management/employee_list.html'
    context_object_name = 'employees'

class EmployeeDetailView(LoginRequiredMixin, DetailView):
    model = Employee
    template_name = 'hr_management/employee_detail.html'
    context_object_name = 'employee'

class EmployeeCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'hr_management/employee_form.html'
    success_url = reverse_lazy('hr_management:employee-list')
    permission_required = 'hr_management.add_employee'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = "Добавить сотрудника"
        context['button_text'] = "Сохранить"
        return context


class EmployeeUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'hr_management/employee_form.html'
    success_url = reverse_lazy('hr_management:employee-list')
    permission_required = 'hr_management.change_employee'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = "Изменить данные сотрудника"
        context['button_text'] = "Сохранить изменения"
        return context

class EmployeeDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Employee
    template_name = 'hr_management/employee_confirm_delete.html'
    success_url = reverse_lazy('hr_management:employee-list')
    context_object_name = 'employee'
    permission_required = 'hr_management.delete_employee'