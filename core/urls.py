from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/update/', login_required(views.profile_update), name='profile_update'),
    path('profile/payment-methods/delete/<int:payment_method_id>/', views.delete_payment_method, name='delete_payment_method'),
    path('profile/payment-methods/set-default/<int:payment_method_id>/', views.set_default_payment_method, name='set_default_payment_method'),
    path('contact/', views.contact, name='contact'),
    path('debug/csrf/', views.debug_csrf, name='debug_csrf'),
] 