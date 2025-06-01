from django.urls import path
from . import views

app_name = 'hr_management' # Для пространства имен URL

urlpatterns = [
    # Department URLs
    path('departments/', views.DepartmentListView.as_view(), name='department-list'),
    path('departments/add/', views.DepartmentCreateView.as_view(), name='department-add'),
    path('departments/<int:pk>/', views.DepartmentDetailView.as_view(), name='department-detail'),
    path('departments/<int:pk>/edit/', views.DepartmentUpdateView.as_view(), name='department-edit'),
    path('departments/<int:pk>/delete/', views.DepartmentDeleteView.as_view(), name='department-delete'),

    # Employee URLs
    path('employees/', views.EmployeeListView.as_view(), name='employee-list'),
    path('employees/add/', views.EmployeeCreateView.as_view(), name='employee-add'),
    path('employees/<int:pk>/', views.EmployeeDetailView.as_view(), name='employee-detail'),
    path('employees/<int:pk>/edit/', views.EmployeeUpdateView.as_view(), name='employee-edit'),
    path('employees/<int:pk>/delete/', views.EmployeeDeleteView.as_view(), name='employee-delete'),

    path('bonuses/calculate/', views.CalculateBonusView.as_view(), name='bonus-calculate'),
path('reports/', views.ReportSelectionView.as_view(), name='report-selection'),
path('reports/employees/csv/', views.EmployeeReportCSVView.as_view(), name='employee-report-csv'),
]