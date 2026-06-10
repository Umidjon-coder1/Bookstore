from django.urls import path
from . import api_views

app_name = 'api-books'

urlpatterns = [
    path('', api_views.BookListCreateView.as_view(), name='list-create'),
    path('featured/', api_views.FeaturedBooksView.as_view(), name='featured'),
    path('categories/', api_views.CategoryListView.as_view(), name='categories'),
    path('authors/', api_views.AuthorListView.as_view(), name='authors'),
    path('<slug:slug>/', api_views.BookRetrieveUpdateDestroyView.as_view(), name='detail'),
]
