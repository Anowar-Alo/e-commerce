from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Order, OrderItem, ShippingAddress

@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = ('id', 'user', 'total', 'status', 'created_at')
    list_filter = ('status', 'created_at', 'payment_method')
    search_fields = ('id', 'user__email', 'shipping_address__address')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Order Information', {
            'fields': ('user', 'status', 'total')
        }),
        ('Payment', {
            'fields': ('payment_method', 'payment_status')
        }),
        ('Shipping', {
            'fields': ('shipping_address', 'shipping_method', 'tracking_number')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(OrderItem)
class OrderItemAdmin(ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'unit_price')
    list_filter = ('order__status',)
    search_fields = ('order__id', 'product__name')

@admin.register(ShippingAddress)
class ShippingAddressAdmin(ModelAdmin):
    list_display = ('user', 'address', 'city', 'state', 'country')
    list_filter = ('country', 'state')
    search_fields = ('user__email', 'address', 'city') 