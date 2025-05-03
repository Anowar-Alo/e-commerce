from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.email


class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(_('bio'), blank=True)
    website = models.URLField(_('website'), blank=True)
    social_links = models.JSONField(_('social links'), default=dict, blank=True)
    preferences = models.JSONField(_('preferences'), default=dict, blank=True)
    
    # Shipping addresses
    shipping_addresses = models.JSONField(_('shipping addresses'), default=list, blank=True)
    default_shipping_address = models.IntegerField(_('default shipping address'), null=True, blank=True)
    
    # Payment methods
    payment_methods = models.JSONField(_('payment methods'), default=list, blank=True)
    default_payment_method = models.CharField(_('default payment method'), max_length=100, blank=True)
    
    # Wishlist and recently viewed
    wishlist = models.ManyToManyField('products.Product', related_name='wishlists', blank=True)
    recently_viewed = models.JSONField(_('recently viewed'), default=list, blank=True)
    
    class Meta:
        verbose_name = _('user profile')
        verbose_name_plural = _('user profiles')
    
    def __str__(self):
        return f"{self.user.email}'s profile"
    
    def add_to_wishlist(self, product):
        self.wishlist.add(product)
    
    def remove_from_wishlist(self, product):
        self.wishlist.remove(product)
    
    def add_shipping_address(self, address):
        addresses = self.shipping_addresses
        addresses.append(address)
        self.shipping_addresses = addresses
        self.save()
    
    def set_default_shipping_address(self, index):
        if 0 <= index < len(self.shipping_addresses):
            self.default_shipping_address = index
            self.save()
    
    def add_payment_method(self, payment_method):
        methods = self.payment_methods
        methods.append(payment_method)
        self.payment_methods = methods
        self.save()
    
    def set_default_payment_method(self, payment_method_id):
        self.default_payment_method = payment_method_id
        self.save()
    
    def add_recently_viewed(self, product_id):
        recently_viewed = self.recently_viewed
        if product_id in recently_viewed:
            recently_viewed.remove(product_id)
        recently_viewed.insert(0, product_id)
        self.recently_viewed = recently_viewed[:10]  # Keep only last 10 items
        self.save() 