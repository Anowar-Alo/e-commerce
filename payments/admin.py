from django.contrib import admin
try:
    from unfold.admin import ModelAdmin
except ImportError:
    from django.contrib.admin import ModelAdmin
from .models import PaymentMethod, Transaction

# Payment models are not registered in admin to keep the interface clean

@admin.register(PaymentMethod)
class PaymentMethodAdmin(ModelAdmin):
    list_display = ('provider', 'type', 'is_active')
    list_filter = ('is_active', 'type')
    search_fields = ('provider', 'token')

@admin.register(Transaction)
class TransactionAdmin(ModelAdmin):
    list_display = ('order', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order__id', 'transaction_id')
    readonly_fields = ('created_at', 'updated_at')