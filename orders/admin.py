from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.contrib import messages
from django.utils import timezone
from .models import Order, Refund, OrderStatusUpdate
from core.admin import admin_site
from core.models import Dashboard

@admin.register(Order, site=admin_site)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'total', 'status', 'payment_status', 'created_at', 'refund_action')
    list_filter = ('status', 'payment_status', 'created_at', 'payment_method')
    search_fields = ('order_number', 'user__email', 'shipping_address')
    readonly_fields = ('created_at', 'updated_at', 'order_number', 'status_history')
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'status', 'payment_status', 'total')
        }),
        ('Customer Information', {
            'fields': ('shipping_name', 'shipping_phone', 'shipping_email', 'shipping_address')
        }),
        ('Notes', {
            'fields': ('customer_notes', 'staff_notes')
        }),
        ('Status History', {
            'fields': ('status_history',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'paid_at', 'shipped_at', 'delivered_at'),
            'classes': ('collapse',)
        }),
    )
    
    def refund_action(self, obj):
        """Add refund button to the list display."""
        if obj.payment_status == 'paid' and obj.status not in ['refunded', 'cancelled']:
            return format_html(
                '<a href="{}" class="button" style="background-color: #dc3545; color: white; padding: 5px 10px; text-decoration: none; border-radius: 4px;">Refund</a>',
                reverse('admin:orders_order_change', args=[obj.id])
            )
        return '-'
    refund_action.short_description = 'Refund'
    
    def status_history(self, obj):
        """Display the order status history."""
        updates = obj.status_updates.all().order_by('-created_at')
        if not updates:
            return 'No status updates yet.'
        
        history = []
        for update in updates:
            history.append(
                f'<div class="status-update">'
                f'<strong>{update.status}</strong> by {update.created_by} '
                f'on {update.created_at.strftime("%Y-%m-%d %H:%M")}'
                f'<br><small>{update.notes}</small>'
                f'</div>'
            )
        return format_html(''.join(history))
    status_history.short_description = 'Status History'

    def save_model(self, request, obj, form, change):
        """Handle order updates and refunds."""
        try:
            if change and 'status' in form.changed_data:
                old_status = form.initial['status']
                
                # Create status update record
                obj.status_updates.create(
                    status=obj.status,
                    notes=f"Status updated to {obj.status}",
                    created_by=request.user
                )
                
                # Handle refund
                if obj.status == 'refunded' and obj.payment_status == 'paid':
                    # Create refund record
                    Refund.objects.create(
                        order=obj,
                        status='completed',
                        amount=obj.total,
                        reason="Refund processed through admin panel",
                        processed_by=request.user,
                        processed_at=timezone.now()
                    )
                    obj.payment_status = 'refunded'
                    obj.restore_product_stock()  # Restore stock on refund
                
                # Update stock and dashboard metrics if order is delivered
                if obj.status == 'delivered' and obj.payment_status == 'paid':
                    try:
                        obj.update_product_stock()  # Update stock on delivery
                    except ValueError as e:
                        messages.error(request, str(e))
                        obj.status = old_status  # Revert the status change
                        return
                    
                    # Update dashboard metrics
                    dashboard = Dashboard.objects.first()
                    if dashboard:
                        dashboard.update_metrics()
                
                # Handle cancelled orders
                if obj.status == 'cancelled':
                    obj.restore_product_stock()  # Restore stock on cancellation
            
            super().save_model(request, obj, form, change)
            
            # Show message to admin
            if change and 'status' in form.changed_data:
                if obj.status == 'delivered':
                    messages.success(request, f'Order {obj.order_number} marked as delivered. Product stock has been updated.')
                elif obj.status in ['cancelled', 'refunded']:
                    messages.info(request, f'Order {obj.order_number} {obj.status}. Product stock has been restored.')
        
        except Exception as e:
            messages.error(request, f'Error updating order: {str(e)}')
            if change and 'status' in form.changed_data:
                obj.status = form.initial['status']  # Revert the status change 