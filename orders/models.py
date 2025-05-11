from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField
from simple_history.models import HistoricalRecords
from django.db.models.signals import post_save
from django.dispatch import receiver
from core.models import Dashboard


class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('processing', _('Processing')),
        ('shipped', _('Shipped')),
        ('delivered', _('Delivered')),
        ('cancelled', _('Cancelled')),
        ('refunded', _('Refunded')),
    )
    
    PAYMENT_STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('paid', _('Paid')),
        ('failed', _('Failed')),
        ('refunded', _('Refunded')),
    )
    
    # Order information
    order_number = models.CharField(_('order number'), max_length=32, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    email = models.EmailField(_('email'))
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(_('payment status'), max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Customer information
    shipping_name = models.CharField(_('shipping name'), max_length=255)
    shipping_phone = PhoneNumberField(_('shipping phone'))
    shipping_email = models.EmailField(_('shipping email'))
    shipping_address = models.CharField(_('shipping address'), max_length=255)
    shipping_address2 = models.CharField(_('shipping address 2'), max_length=255, blank=True)
    shipping_city = models.CharField(_('shipping city'), max_length=100)
    shipping_state = models.CharField(_('shipping state'), max_length=100)
    shipping_country = CountryField(_('shipping country'))
    shipping_postal_code = models.CharField(_('shipping postal code'), max_length=20)
    
    # Billing information
    billing_name = models.CharField(_('billing name'), max_length=255)
    billing_phone = PhoneNumberField(_('billing phone'))
    billing_email = models.EmailField(_('billing email'))
    billing_address = models.CharField(_('billing address'), max_length=255)
    billing_address2 = models.CharField(_('billing address 2'), max_length=255, blank=True)
    billing_city = models.CharField(_('billing city'), max_length=100)
    billing_state = models.CharField(_('billing state'), max_length=100)
    billing_country = CountryField(_('billing country'))
    billing_postal_code = models.CharField(_('billing postal code'), max_length=20)
    
    # Amounts
    subtotal = models.DecimalField(_('subtotal'), max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(_('shipping cost'), max_digits=10, decimal_places=2)
    tax = models.DecimalField(_('tax'), max_digits=10, decimal_places=2)
    total = models.DecimalField(_('total'), max_digits=10, decimal_places=2)
    
    # Shipping information
    shipping_method = models.CharField(_('shipping method'), max_length=100)
    tracking_number = models.CharField(_('tracking number'), max_length=100, blank=True)
    estimated_delivery = models.DateField(_('estimated delivery'), null=True, blank=True)
    
    # Payment information
    payment_method = models.CharField(_('payment method'), max_length=100)
    transaction_id = models.CharField(_('transaction ID'), max_length=100, blank=True)
    payment_details = models.JSONField(_('payment details'), null=True, blank=True)
    
    # Notes and metadata
    customer_notes = models.TextField(_('customer notes'), blank=True)
    staff_notes = models.TextField(_('staff notes'), blank=True)
    metadata = models.JSONField(_('metadata'), null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    paid_at = models.DateTimeField(_('paid at'), null=True, blank=True)
    shipped_at = models.DateTimeField(_('shipped at'), null=True, blank=True)
    delivered_at = models.DateTimeField(_('delivered at'), null=True, blank=True)
    
    # History
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = _('order')
        verbose_name_plural = _('orders')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order {self.order_number}"
    
    @property
    def is_paid(self):
        return self.payment_status == 'paid'
    
    @property
    def can_cancel(self):
        return self.status in ['pending', 'processing']
    
    @property
    def can_refund(self):
        return self.status not in ['cancelled', 'refunded'] and self.is_paid

    def update_product_stock(self):
        """Update product stock when order is delivered."""
        if self.status == 'delivered' and self.payment_status == 'paid':
            for item in self.items.all():
                if item.product:
                    # Check if enough stock is available
                    if item.product.stock < item.quantity:
                        raise ValueError(f'Not enough stock for product {item.product.name}. Available: {item.product.stock}, Required: {item.quantity}')
                    
                    # Decrease product stock
                    item.product.stock -= item.quantity
                    item.product.save()
                    
                    # If product has variants, update variant stock
                    if item.variant:
                        if item.variant.stock < item.quantity:
                            raise ValueError(f'Not enough stock for variant {item.variant.name}. Available: {item.variant.stock}, Required: {item.quantity}')
                        item.variant.stock -= item.quantity
                        item.variant.save()

    def restore_product_stock(self):
        """Restore product stock when order is cancelled or refunded."""
        if self.status in ['cancelled', 'refunded']:
            for item in self.items.all():
                if item.product:
                    # Restore product stock
                    item.product.stock += item.quantity
                    item.product.save()
                    
                    # If product has variants, restore variant stock
                    if item.variant:
                        item.variant.stock += item.quantity
                        item.variant.save()

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        old_status = None
        old_payment_status = None
        
        if not is_new:
            old_instance = Order.objects.get(pk=self.pk)
            old_status = old_instance.status
            old_payment_status = old_instance.payment_status
        
        super().save(*args, **kwargs)
        
        # Handle stock updates
        if is_new:
            # New order - no stock changes yet
            pass
        else:
            # Status changed to delivered
            if self.status == 'delivered' and old_status != 'delivered':
                self.update_product_stock()
            # Status changed to cancelled/refunded
            elif self.status in ['cancelled', 'refunded'] and old_status not in ['cancelled', 'refunded']:
                self.restore_product_stock()
            # Payment status changed to refunded
            elif self.payment_status == 'refunded' and old_payment_status != 'refunded':
                self.restore_product_stock()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.SET_NULL, null=True)
    variant = models.ForeignKey('products.ProductVariant', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Product information at time of purchase
    product_name = models.CharField(_('product name'), max_length=255)
    variant_name = models.CharField(_('variant name'), max_length=100, blank=True)
    sku = models.CharField(_('SKU'), max_length=100)
    unit_price = models.DecimalField(_('unit price'), max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(_('quantity'))
    total_price = models.DecimalField(_('total price'), max_digits=10, decimal_places=2)
    
    # Product metadata at time of purchase
    product_data = models.JSONField(_('product data'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('order item')
        verbose_name_plural = _('order items')
    
    def __str__(self):
        return f"{self.product_name} ({self.quantity}) - Order {self.order.order_number}"


class OrderStatusUpdate(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_updates')
    status = models.CharField(_('status'), max_length=20, choices=Order.STATUS_CHOICES)
    notes = models.TextField(_('notes'), blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('order status update')
        verbose_name_plural = _('order status updates')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.order.order_number} - {self.status}"


class Refund(models.Model):
    STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
        ('completed', _('Completed')),
    )
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='refunds')
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default='pending')
    amount = models.DecimalField(_('amount'), max_digits=10, decimal_places=2)
    reason = models.TextField(_('reason'))
    notes = models.TextField(_('notes'), blank=True)
    
    # Refund processing
    processed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='processed_refunds')
    processed_at = models.DateTimeField(_('processed at'), null=True, blank=True)
    transaction_id = models.CharField(_('transaction ID'), max_length=100, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('refund')
        verbose_name_plural = _('refunds')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Refund for Order {self.order.order_number}"


class ShippingAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='shipping_addresses')
    address = models.CharField(_('address'), max_length=255)
    address2 = models.CharField(_('address 2'), max_length=255, blank=True)
    city = models.CharField(_('city'), max_length=100)
    state = models.CharField(_('state'), max_length=100)
    country = CountryField(_('country'))
    postal_code = models.CharField(_('postal code'), max_length=20)
    is_default = models.BooleanField(_('is default'), default=False)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('shipping address')
        verbose_name_plural = _('shipping addresses')
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.address}, {self.city}, {self.state} {self.postal_code}"


@receiver(post_save, sender=Order)
def handle_order_status_changes(sender, instance, created, **kwargs):
    """Handle stock updates when order status changes."""
    if not created:  # Only for existing orders
        try:
            old_instance = Order.objects.get(pk=instance.pk)
            
            # Order just marked as delivered
            if instance.status == 'delivered' and old_instance.status != 'delivered':
                if instance.payment_status == 'paid':
                    instance.update_product_stock()
            
            # Order just cancelled or refunded
            elif instance.status in ['cancelled', 'refunded'] and old_instance.status not in ['cancelled', 'refunded']:
                instance.restore_product_stock()
            
            # Payment status changed to refunded
            elif instance.payment_status == 'refunded' and old_instance.payment_status != 'refunded':
                instance.restore_product_stock()
                
        except Order.DoesNotExist:
            pass  # Handle case where old instance doesn't exist


@receiver(post_save, sender=Order)
def update_revenue_on_order_completion(sender, instance, created, **kwargs):
    """Update revenue when an order is completed."""
    if instance.status == 'delivered' and instance.payment_status == 'paid':
        # Update dashboard metrics
        dashboard = Dashboard.objects.first()
        if dashboard:
            dashboard.update_metrics() 