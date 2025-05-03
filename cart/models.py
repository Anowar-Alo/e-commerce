from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from products.models import Product, ProductVariant


class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(_('session ID'), max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('cart')
        verbose_name_plural = _('carts')
    
    def __str__(self):
        return f"Cart {self.id} - {'User: ' + self.user.email if self.user else 'Session: ' + self.session_id}"
    
    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())
    
    @property
    def subtotal(self):
        return sum(item.total_price for item in self.items.all())
    
    @property
    def total_weight(self):
        return sum(item.total_weight for item in self.items.all())
    
    def clear(self):
        self.items.all().delete()
    
    def merge_with(self, other_cart):
        """Merge another cart into this one"""
        for item in other_cart.items.all():
            existing_item = self.items.filter(
                product=item.product,
                variant=item.variant
            ).first()
            
            if existing_item:
                existing_item.quantity += item.quantity
                existing_item.save()
            else:
                item.cart = self
                item.save()
        
        other_cart.delete()


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(_('quantity'), validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('cart item')
        verbose_name_plural = _('cart items')
        unique_together = ('cart', 'product', 'variant')
    
    def __str__(self):
        return f"{self.product.name} ({self.quantity}) in Cart {self.cart.id}"
    
    @property
    def unit_price(self):
        if self.variant:
            return self.variant.price
        return self.product.price
    
    @property
    def total_price(self):
        return self.unit_price * self.quantity
    
    @property
    def total_weight(self):
        if self.product.weight:
            return self.product.weight * self.quantity
        return 0
    
    def update_quantity(self, quantity):
        """Update item quantity ensuring it doesn't exceed available stock"""
        available_quantity = self.variant.quantity if self.variant else self.product.quantity
        self.quantity = min(quantity, available_quantity)
        self.save()


class SavedForLater(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('saved for later')
        verbose_name_plural = _('saved for later')
        unique_together = ('user', 'product', 'variant')
    
    def __str__(self):
        return f"{self.product.name} saved by {self.user.email}"
    
    def move_to_cart(self, cart):
        """Move item to cart and remove from saved items"""
        CartItem.objects.create(
            cart=cart,
            product=self.product,
            variant=self.variant,
            quantity=1
        )
        self.delete() 