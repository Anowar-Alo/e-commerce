from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.order_list, name='order_list'),
    path('create/', views.order_create, name='create'),
    path('<int:order_id>/', views.order_detail, name='detail'),
    path('<int:order_id>/update/', views.order_update, name='update'),
    path('<int:order_id>/cancel/', views.cancel_order, name='cancel'),
] 