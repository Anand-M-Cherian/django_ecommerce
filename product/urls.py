from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.get_products, name='get_products'),
    path('products/create/', views.create_product, name='create_product'),
    path('products/upload-images/', views.upload_product_images, name='upload_product_images'),
    path('products/<str:pk>/', views.get_product, name='get_product'),
    path('products/<str:pk>/update/', views.update_product, name='update_product'),
    path('products/<str:pk>/delete/', views.delete_product, name='delete_product'),
    path('products/<str:pk>/add-review/', views.add_product_review, name='add_product_review'),
    path('products/<str:pk>/delete-review/', views.delete_product_review, name='delete_product_reviews'),
]
