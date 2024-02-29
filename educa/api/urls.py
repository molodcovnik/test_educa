from django.urls import path

from .views import ProductsList, ProductDetailView

urlpatterns = [
    path('products/', ProductsList.as_view()),
    path('products/<int:pk>/', ProductDetailView.as_view()),
]