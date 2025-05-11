from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomAdminLoginForm
from django.urls import path, include
from django.shortcuts import render
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta
from products.models import Product, Category, Brand, ProductAttribute
from orders.models import Order, OrderItem, Refund
from django.contrib.auth.models import User
from .models import Dashboard, UserProfile, SiteSettings, ContactMessage
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
    site_header = "ASM"
    site_title = "ASM"
    index_title = "ASM"

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

    def get_app_list(self, request, app_label=None):
        app_list = super().get_app_list(request, app_label)
        # Remove payments app from the list
        app_list = [app for app in app_list if app['app_label'] != 'payments']
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
        
        # Get revenue statistics - only count delivered and paid orders
        total_revenue = Order.objects.filter(status='delivered', payment_status='paid').aggregate(Sum('total'))['total__sum'] or 0
        weekly_revenue = Order.objects.filter(status='delivered', payment_status='paid', created_at__gte=last_week).aggregate(Sum('total'))['total__sum'] or 0
        monthly_revenue = Order.objects.filter(status='delivered', payment_status='paid', created_at__gte=last_month).aggregate(Sum('total'))['total__sum'] or 0

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

class ProductAttributeInline(admin.TabularInline):
    model = ProductAttribute
    extra = 1
    fields = ('attribute', 'value')

@admin.register(Product, site=admin_site)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'brand', 'price', 'stock', 'is_active')
    list_filter = ('category', 'brand', 'is_active')
    search_fields = ('name', 'description', 'sku')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'category', 'brand', 'sku')
        }),
        ('Pricing and Stock', {
            'fields': ('price', 'stock', 'is_active')
        }),
        ('Images', {
            'fields': ('image', 'gallery')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    # Add inline for product attributes
    inlines = [ProductAttributeInline]

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
            'fields': ('image',)
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
            'fields': ('logo',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
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
        ('Basic Information', {
            'fields': ('site_name', 'site_description', 'logo', 'favicon')
        }),
        ('Contact Information', {
            'fields': ('contact_email', 'contact_phone', 'address')
        }),
        ('Social Media', {
            'fields': ('facebook_url', 'twitter_url', 'instagram_url', 'linkedin_url')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords')
        }),
        ('Maintenance', {
            'fields': ('maintenance_mode', 'maintenance_message')
        }),
        ('Analytics', {
            'fields': ('google_analytics_id', 'facebook_pixel_id')
        }),
        ('Shipping', {
            'fields': ('free_shipping_threshold', 'shipping_cost')
        }),
        ('Theme', {
            'fields': ('primary_color', 'secondary_color', 'accent_color')
        }),
        ('Cache', {
            'fields': ('cache_timeout',)
        })
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

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = "Mark selected messages as read"
    
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
    mark_as_unread.short_description = "Mark selected messages as unread"
    
    actions = ['mark_as_read', 'mark_as_unread'] 