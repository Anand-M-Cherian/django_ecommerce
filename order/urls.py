from django.urls import path
from . import views

urlpatterns = [
    # stripe integration
    path('create-checkout-session/', views.create_checkout_session, name='create_checkout_session'),
    path('orders/webhook/', views.stripe_webhook, name='stripe_webhook'),

    # order management
    path('orders/create/', views.create_order, name='create_order'),
    path('orders/get/', views.get_orders, name='get_orders'),
    path('orders/<str:pk>/', views.get_order, name='get_order'),
    path('orders/<str:pk>/process/', views.process_order, name='process_order'),
    path('orders/<str:pk>/delete/', views.delete_order, name='delete_order'),
]
