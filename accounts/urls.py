from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    path('profile/', views.profile, name='profile'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='account_login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='core:home'), name='account_logout'),
    path('signup/', views.signup, name='account_signup'),
] 