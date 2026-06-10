from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('dashboard/books/', views.DashboardBooksView.as_view(), name='dashboard-books'),
    path('dashboard/users/', views.DashboardUsersView.as_view(), name='dashboard-users'),
    path('dashboard/orders/', views.DashboardOrdersView.as_view(), name='dashboard-orders'),
]
