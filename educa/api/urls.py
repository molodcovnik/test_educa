from django.urls import path

from .views import ProductsList, ProductDetailView, ProductGroupsView, GroupsRefactorView

urlpatterns = [
    path('products/', ProductsList.as_view()),
    path('products/<int:pk>/', ProductDetailView.as_view()),
    path('products/<int:pk>/groups/', ProductGroupsView.as_view()),
    path('products/<int:pk>/groups/refactor/', GroupsRefactorView.as_view()),
]