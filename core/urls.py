from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('customer/register/', views.customer_register, name='customer_register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/customer/', views.customer_dashboard, name='customer_dashboard'),
    path('dashboard/manager/', views.manager_dashboard, name='manager_dashboard'),
    path('loan/request/', views.loan_request_view, name='loan_request'),
    path('customer/request-loan/', views.loan_request_view, name='loan_request'),
    path('manager/', views.manager_dashboard, name='manager_dashboard'),

]
