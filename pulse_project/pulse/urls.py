from django.urls import path
from . import views

urlpatterns = [
    path('auth/register/', views.RegisterView.as_any_views() if hasattr(views.RegisterView, 'as_any_views') else views.RegisterView.as_view(), name='register'),
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('alerts/', views.PriceAlertListCreateView.as_view(), name='alerts_list_create'),
    path('alerts/<int:id>/', views.PriceAlertDeleteView.as_view(), name='alert_deactivate'),
    path('flights/price/', views.get_flight_price, name='mock_price_feed'),
    path('admin/summary/', views.AdminSummaryView.as_view(), name='admin_summary'),
]