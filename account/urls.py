from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('get-user/', views.get_user, name='get_user'),
    path('update-user/', views.update_user, name='update_user'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<str:token>/', views.reset_password, name='reset_password'),
]
