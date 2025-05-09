from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from accounts.models import CustomUser

User = CustomUser


class Notification(models.Model):
    TYPE_CHOICES = (
        ('order', _('Order')),
        ('payment', _('Payment')),
        ('shipping', _('Shipping')),
        ('account', _('Account')),
        ('product', _('Product')),
        ('system', _('System')),
    )
    
    LEVEL_CHOICES = (
        ('info', _('Information')),
        ('success', _('Success')),
        ('warning', _('Warning')),
        ('error', _('Error')),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(_('type'), max_length=20, choices=TYPE_CHOICES)
    level = models.CharField(_('level'), max_length=20, choices=LEVEL_CHOICES, default='info')
    title = models.CharField(_('title'), max_length=255)
    message = models.TextField(_('message'))
    
    # Generic relation to any model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Status
    is_read = models.BooleanField(_('read'), default=False)
    is_sent = models.BooleanField(_('sent'), default=False)
    
    # Metadata
    metadata = models.JSONField(_('metadata'), null=True, blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('notification')
        verbose_name_plural = _('notifications')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.email}"
    
    def mark_as_read(self):
        self.is_read = True
        self.save()
    
    def mark_as_sent(self):
        self.is_sent = True
        self.save()


class EmailTemplate(models.Model):
    name = models.CharField(_('name'), max_length=100, unique=True)
    subject = models.CharField(_('subject'), max_length=255)
    html_content = models.TextField(_('HTML content'))
    text_content = models.TextField(_('text content'))
    is_active = models.BooleanField(_('active'), default=True)
    
    # Variables that can be used in the template
    variables = models.JSONField(_('variables'), help_text=_('Variables that can be used in the template'))
    
    # Metadata
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('email template')
        verbose_name_plural = _('email templates')
    
    def __str__(self):
        return self.name


class SMSTemplate(models.Model):
    name = models.CharField(_('name'), max_length=100, unique=True)
    content = models.TextField(_('content'))
    is_active = models.BooleanField(_('active'), default=True)
    
    # Variables that can be used in the template
    variables = models.JSONField(_('variables'), help_text=_('Variables that can be used in the template'))
    
    # Metadata
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('SMS template')
        verbose_name_plural = _('SMS templates')
    
    def __str__(self):
        return self.name


class PushNotificationTemplate(models.Model):
    name = models.CharField(_('name'), max_length=100, unique=True)
    title = models.CharField(_('title'), max_length=255)
    body = models.TextField(_('body'))
    image_url = models.URLField(_('image URL'), blank=True)
    action_url = models.URLField(_('action URL'), blank=True)
    is_active = models.BooleanField(_('active'), default=True)
    
    # Variables that can be used in the template
    variables = models.JSONField(_('variables'), help_text=_('Variables that can be used in the template'))
    
    # Metadata
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('push notification template')
        verbose_name_plural = _('push notification templates')
    
    def __str__(self):
        return self.name


class Audit(models.Model):
    ACTION_CHOICES = (
        ('create', _('Create')),
        ('update', _('Update')),
        ('delete', _('Delete')),
        ('view', _('View')),
        ('login', _('Login')),
        ('logout', _('Logout')),
        ('other', _('Other')),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    action = models.CharField(_('action'), max_length=20, choices=ACTION_CHOICES)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Request information
    ip_address = models.GenericIPAddressField(_('IP address'))
    user_agent = models.CharField(_('user agent'), max_length=255)
    
    # Change details
    changes = models.JSONField(_('changes'), null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('audit log')
        verbose_name_plural = _('audit logs')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.action} by {self.user} at {self.created_at}"


class Dashboard(models.Model):
    total_orders = models.IntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_products = models.IntegerField(default=0)
    total_customers = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    monthly_revenue = models.JSONField(default=dict, help_text="Monthly revenue data")

    class Meta:
        verbose_name = _('Dashboard')
        verbose_name_plural = _('Dashboard')

    def __str__(self):
        return f'Dashboard - {self.last_updated}'

    def update_metrics(self):
        from orders.models import Order
        from products.models import Product
        from django.contrib.auth import get_user_model
        from django.utils import timezone
        from django.db.models import Sum
        from datetime import datetime

        User = get_user_model()
        
        # Update basic metrics
        self.total_orders = Order.objects.count()
        self.total_revenue = Order.objects.filter(status='completed', payment_status='paid').aggregate(
            total=Sum('total')
        )['total'] or 0
        self.total_products = Product.objects.count()
        self.total_customers = User.objects.filter(is_staff=False).count()

        # Update monthly revenue
        current_year = timezone.now().year
        monthly_data = {}
        
        for month in range(1, 13):
            month_start = timezone.make_aware(datetime(current_year, month, 1))
            if month == 12:
                next_month = timezone.make_aware(datetime(current_year + 1, 1, 1))
            else:
                next_month = timezone.make_aware(datetime(current_year, month + 1, 1))
            
            month_revenue = Order.objects.filter(
                status='completed',
                payment_status='paid',
                created_at__gte=month_start,
                created_at__lt=next_month
            ).aggregate(total=Sum('total'))['total'] or 0
            
            monthly_data[str(month)] = float(month_revenue)
        
        self.monthly_revenue = monthly_data
        self.save()


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='core_profile')
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s profile"


class SiteSettings(models.Model):
    """Singleton model for site-wide settings."""
    site_name = models.CharField(max_length=100)
    site_description = models.TextField(blank=True)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)
    address = models.TextField(_('address'), blank=True)
    
    # Social Media
    facebook_url = models.URLField(_('Facebook URL'), blank=True)
    twitter_url = models.URLField(_('Twitter URL'), blank=True)
    instagram_url = models.URLField(_('Instagram URL'), blank=True)
    linkedin_url = models.URLField(_('LinkedIn URL'), blank=True)
    
    # SEO
    meta_title = models.CharField(_('meta title'), max_length=100, blank=True)
    meta_description = models.TextField(_('meta description'), blank=True)
    meta_keywords = models.CharField(_('meta keywords'), max_length=255, blank=True)
    
    # Maintenance
    maintenance_mode = models.BooleanField(_('maintenance mode'), default=False)
    maintenance_message = models.TextField(_('maintenance message'), blank=True)
    
    # Analytics
    google_analytics_id = models.CharField(_('Google Analytics ID'), max_length=50, blank=True)
    facebook_pixel_id = models.CharField(_('Facebook Pixel ID'), max_length=50, blank=True)
    
    # Payment
    currency = models.CharField(_('currency'), max_length=3, default='USD')
    currency_symbol = models.CharField(_('currency symbol'), max_length=5, default='$')
    tax_rate = models.DecimalField(_('tax rate'), max_digits=5, decimal_places=2, default=0)
    
    # Shipping
    free_shipping_threshold = models.DecimalField(_('free shipping threshold'), max_digits=10, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(_('shipping cost'), max_digits=10, decimal_places=2, default=0)
    
    # Theme
    primary_color = models.CharField(_('primary color'), max_length=7, default='#4CAF50')
    secondary_color = models.CharField(_('secondary color'), max_length=7, default='#2196F3')
    accent_color = models.CharField(_('accent color'), max_length=7, default='#FF9800')
    
    # Logo and Favicon
    logo = models.ImageField(_('logo'), upload_to='settings/', blank=True, null=True)
    favicon = models.ImageField(_('favicon'), upload_to='settings/', blank=True, null=True)
    
    # Cache
    cache_timeout = models.IntegerField(_('cache timeout'), default=3600)  # 1 hour
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Site Setting')
        verbose_name_plural = _('Site Settings')
    
    def __str__(self):
        return self.site_name
    
    def save(self, *args, **kwargs):
        if not self.pk and SiteSettings.objects.exists():
            raise ValidationError(_('There can be only one SiteSettings instance'))
        super().save(*args, **kwargs)
        self.clear_cache()
    
    def delete(self, *args, **kwargs):
        raise ValidationError(_('SiteSettings cannot be deleted'))
    
    def clear_cache(self):
        cache.delete('site_settings')
    
    @classmethod
    def get_settings(cls):
        settings, created = cls.objects.get_or_create(
            id=1,
            defaults={
                'site_name': 'E-commerce Site',
                'site_description': 'Your one-stop shop for all your needs',
                'contact_email': 'kamrulhasan9047@gmail.com',
                'contact_phone': '+8801757704783'
            }
        )
        return settings


class ContactMessage(models.Model):
    """Model for storing contact form submissions."""
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'
    
    def __str__(self):
        return f"{self.name} - {self.subject}" 