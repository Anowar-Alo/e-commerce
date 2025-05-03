from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import RangeNumericListFilter
from import_export.admin import ImportExportModelAdmin
from simple_history.admin import SimpleHistoryAdmin
from .models import (
    Product, Category, Brand, ProductVariant, ProductImage, ProductReview,
    Attribute, ProductAttribute, VariantAttribute
)

@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin, SimpleHistoryAdmin, ModelAdmin):
    list_display = ('name', 'category', 'brand', 'price', 'stock', 'is_active')
    list_filter = ('is_active', 'category', 'brand')
    search_fields = ('name', 'description', 'sku')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'sku')
        }),
        ('Pricing & Stock', {
            'fields': ('price', 'stock', 'is_active')
        }),
        ('Categories & Brand', {
            'fields': ('category', 'brand')
        }),
        ('Media', {
            'fields': ('image', 'gallery')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(Category)
class CategoryAdmin(ImportExportModelAdmin, SimpleHistoryAdmin, ModelAdmin):
    list_display = ('name', 'slug', 'parent', 'is_active')
    list_filter = ('is_active', 'parent')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'image')
        }),
        ('Hierarchy', {
            'fields': ('parent',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(Brand)
class BrandAdmin(ImportExportModelAdmin, SimpleHistoryAdmin, ModelAdmin):
    list_display = ('name', 'slug', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'logo')
        }),
        ('Contact', {
            'fields': ('website',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(ProductVariant)
class ProductVariantAdmin(ImportExportModelAdmin, SimpleHistoryAdmin, ModelAdmin):
    list_display = ('product', 'name', 'sku', 'price_adjustment', 'quantity', 'is_active')
    list_filter = ('is_active', 'product')
    search_fields = ('name', 'sku', 'product__name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('product', 'name', 'sku')
        }),
        ('Pricing & Stock', {
            'fields': ('price_adjustment', 'quantity')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(ProductImage)
class ProductImageAdmin(SimpleHistoryAdmin, ModelAdmin):
    list_display = ('product', 'alt_text', 'is_feature', 'created_at')
    list_filter = ('is_feature', 'created_at')
    search_fields = ('product__name', 'alt_text')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('product', 'image', 'alt_text')
        }),
        ('Settings', {
            'fields': ('is_feature',)
        }),
        ('Metadata', {
            'fields': ('created_at',)
        }),
    )

@admin.register(ProductReview)
class ProductReviewAdmin(SimpleHistoryAdmin, ModelAdmin):
    list_display = ('product', 'user', 'rating', 'is_verified_purchase', 'created_at')
    list_filter = ('rating', 'is_verified_purchase', 'created_at')
    search_fields = ('product__name', 'user__email', 'title', 'comment')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('product', 'user', 'rating', 'title', 'comment')
        }),
        ('Verification', {
            'fields': ('is_verified_purchase', 'is_recommended')
        }),
        ('Media', {
            'fields': ('images',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(Attribute)
class AttributeAdmin(ModelAdmin):
    list_display = ('name', 'type', 'is_required')
    list_filter = ('type', 'is_required')
    search_fields = ('name',)

@admin.register(ProductAttribute)
class ProductAttributeAdmin(ModelAdmin):
    list_display = ('product', 'attribute', 'value')
    list_filter = ('attribute',)
    search_fields = ('product__name', 'value')

@admin.register(VariantAttribute)
class VariantAttributeAdmin(ModelAdmin):
    list_display = ('variant', 'attribute', 'value')
    list_filter = ('attribute',)
    search_fields = ('variant__name', 'value') 