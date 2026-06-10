from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    path('', views.BookListView.as_view(), name='list'),
    path('search/', views.SearchView.as_view(), name='search'),
    path('autocomplete/', views.AutocompleteView.as_view(), name='autocomplete'),
    path('<slug:slug>/', views.BookDetailView.as_view(), name='detail'),
]
