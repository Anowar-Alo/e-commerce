from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('payment-methods/', views.payment_methods, name='payment_methods'),
    path('create-payment-intent/<int:order_id>/', views.create_payment_intent, name='create_payment_intent'),
    path('process-payment/<int:order_id>/', views.process_payment, name='process_payment'),
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),
] 