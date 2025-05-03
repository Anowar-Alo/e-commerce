from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomAdminLoginForm
from django.urls import path, include
from django.shortcuts import render
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta
from products.models import Product, Category, Brand
from orders.models import Order, OrderItem, Refund
from payments.models import Transaction, PaymentMethod
from django.contrib.auth.models import User
from .models import Dashboard, UserProfile, SiteSettings
from .views import admin_analytics
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.views import LoginView
from django.conf import settings
from django.conf.urls.static import static
from django.utils.html import format_html

class CustomAdminSite(admin.AdminSite):
    login_form = CustomAdminLoginForm
    login_template = 'admin/login.html'
    index_template = 'admin/index.html'
    app_index_template = 'admin/app_index.html'
    site_header = settings.ADMIN_SITE_HEADER
    site_title = settings.ADMIN_SITE_TITLE
    index_title = settings.ADMIN_INDEX_TITLE

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('login/', LoginView.as_view(
                template_name='admin/login.html',
                authentication_form=CustomAdminLoginForm,
                extra_context={
                    'site_header': self.site_header,
                    'site_title': self.site_title,
                    'site_url': '/',
                }
            ), name='login'),
        ]
        return custom_urls + urls

    def get_app_list(self, request):
        app_list = super().get_app_list(request)
        return app_list

    def dashboard_view(self, request):
        # Get date ranges
        today = timezone.now()
        last_week = today - timedelta(days=7)
        last_month = today - timedelta(days=30)

        # Get order statistics
        total_orders = Order.objects.count()
        recent_orders = Order.objects.filter(created_at__gte=last_week).count()
        monthly_orders = Order.objects.filter(created_at__gte=last_month).count()
        
        # Get revenue statistics
        total_revenue = Order.objects.filter(status='completed').aggregate(Sum('total'))['total__sum'] or 0
        weekly_revenue = Order.objects.filter(status='completed', created_at__gte=last_week).aggregate(Sum('total'))['total__sum'] or 0
        monthly_revenue = Order.objects.filter(status='completed', created_at__gte=last_month).aggregate(Sum('total'))['total__sum'] or 0

        # Get product statistics
        total_products = Product.objects.count()
        low_stock_products = Product.objects.filter(stock__lt=10).count()
        out_of_stock_products = Product.objects.filter(stock=0).count()

        # Get customer statistics
        total_customers = User.objects.filter(is_staff=False).count()
        new_customers = User.objects.filter(is_staff=False, date_joined__gte=last_week).count()

        # Get recent orders
        recent_orders_list = Order.objects.select_related('user').order_by('-created_at')[:5]

        # Get top selling products
        top_products = Product.objects.annotate(
            total_sales=Sum('orderitem__quantity')
        ).order_by('-total_sales')[:5]

        context = {
            'total_orders': total_orders,
            'recent_orders': recent_orders,
            'monthly_orders': monthly_orders,
            'total_revenue': total_revenue,
            'weekly_revenue': weekly_revenue,
            'monthly_revenue': monthly_revenue,
            'total_products': total_products,
            'low_stock_products': low_stock_products,
            'out_of_stock_products': out_of_stock_products,
            'total_customers': total_customers,
            'new_customers': new_customers,
            'recent_orders_list': recent_orders_list,
            'top_products': top_products,
            'title': 'Dashboard',
            'available_apps': self.get_app_list(request),
        }
        return render(request, 'admin/dashboard.html', context)

# Create admin site instance
admin_site = CustomAdminSite(name='admin')

@admin.register(Product, site=admin_site)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'brand', 'price', 'stock', 'is_active')
    list_filter = ('category', 'brand', 'is_active')
    search_fields = ('name', 'description', 'sku')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'category', 'brand')
        }),
        ('Pricing and Stock', {
            'fields': ('price', 'stock', 'is_active')
        }),
        ('Images', {
            'fields': ('image', 'image_alt')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Category, site=admin_site)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'is_active')
    list_filter = ('parent', 'is_active')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'parent', 'is_active')
        }),
        ('Images', {
            'fields': ('image', 'image_alt')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Brand, site=admin_site)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'is_active')
        }),
        ('Images', {
            'fields': ('logo', 'logo_alt')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Order, site=admin_site)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('id', 'user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Order Information', {
            'fields': ('user', 'status', 'total')
        }),
        ('Shipping Information', {
            'fields': ('shipping_address', 'shipping_city', 'shipping_state', 'shipping_country', 'shipping_postal_code')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(OrderItem, site=admin_site)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'get_price')
    list_filter = ('order__status',)
    search_fields = ('order__id', 'product__name')
    
    def get_price(self, obj):
        return obj.product.price
    get_price.short_description = 'Price'

    fieldsets = (
        ('Order Item Information', {
            'fields': ('order', 'product', 'quantity')
        }),
    )

@admin.register(UserProfile, site=admin_site)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'city', 'country')
    list_filter = ('country', 'city')
    search_fields = ('user__username', 'user__email', 'phone_number', 'bio')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'avatar', 'bio', 'phone_number')
        }),
        ('Address Information', {
            'fields': ('address', 'city', 'state', 'country', 'postal_code')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(SiteSettings, site=admin_site)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'contact_email', 'contact_phone')
    fieldsets = (
        ('General Settings', {
            'fields': ('site_name', 'site_description', 'site_logo')
        }),
        ('Contact Information', {
            'fields': ('contact_email', 'contact_phone', 'contact_address')
        }),
        ('Social Media', {
            'fields': ('facebook_url', 'twitter_url', 'instagram_url'),
            'classes': ('collapse',)
        }),
    )

# Register the dashboard model
admin_site.register(Dashboard)

@admin.register(Refund, site=admin_site)
class RefundAdmin(admin.ModelAdmin):
    list_display = ('order', 'status', 'amount', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order__id', 'reason')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Refund Information', {
            'fields': ('order', 'status', 'amount', 'reason')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(PaymentMethod, site=admin_site)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'is_default', 'created_at')
    list_filter = ('type', 'is_default')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Payment Method Information', {
            'fields': ('user', 'type', 'is_default')
        }),
        ('Card Information', {
            'fields': ('card_last4', 'card_brand', 'card_exp_month', 'card_exp_year'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Transaction, site=admin_site)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('order', 'payment_method', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order__id', 'payment_method__user__username')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Transaction Information', {
            'fields': ('order', 'payment_method', 'amount', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    list_display = ('total_orders', 'total_revenue', 'total_products', 'total_customers', 'last_updated')
    readonly_fields = ('total_orders', 'total_revenue', 'total_products', 'total_customers', 'last_updated')
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def changelist_view(self, request, extra_context=None):
        # Update metrics when viewing the dashboard
        dashboard, created = Dashboard.objects.get_or_create(pk=1)
        dashboard.update_metrics()
        return super().changelist_view(request, extra_context) 