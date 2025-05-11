from django.core.management.base import BaseCommand
from orders.models import Order, OrderItem
from products.models import Product, ProductVariant
from django.db.models import Sum
from django.db import transaction

class Command(BaseCommand):
    help = 'Updates product stock for all existing delivered and paid orders'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting stock update for existing orders...')
        
        # Get all delivered and paid orders
        orders = Order.objects.filter(status='delivered', payment_status='paid')
        order_count = orders.count()
        self.stdout.write(f'Found {order_count} delivered and paid orders')
        
        if order_count == 0:
            self.stdout.write(self.style.WARNING('No delivered and paid orders found'))
            return
        
        # Get all order items for these orders
        order_items = OrderItem.objects.filter(order__in=orders).select_related('product', 'variant')
        
        # Dictionary to track total quantities per product
        product_quantities = {}
        variant_quantities = {}
        
        # Calculate total quantities for each product and variant
        for item in order_items:
            if item.product_id:
                if item.product_id not in product_quantities:
                    product_quantities[item.product_id] = 0
                product_quantities[item.product_id] += item.quantity
                
                if item.variant_id:
                    if item.variant_id not in variant_quantities:
                        variant_quantities[item.variant_id] = 0
                    variant_quantities[item.variant_id] += item.quantity
        
        self.stdout.write(f'Processing {len(product_quantities)} products and {len(variant_quantities)} variants')
        
        # Update product stock within a transaction
        with transaction.atomic():
            # Update product stock
            updated_products = 0
            for product_id, total_quantity in product_quantities.items():
                try:
                    product = Product.objects.get(id=product_id)
                    product.stock -= total_quantity
                    product.save()
                    updated_products += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Updated stock for product {product.name} (ID: {product.id}): -{total_quantity} units'
                        )
                    )
                except Product.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(
                            f'Product with ID {product_id} not found'
                        )
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f'Error updating stock for product ID {product_id}: {str(e)}'
                        )
                    )
            
            # Update variant stock
            updated_variants = 0
            for variant_id, total_quantity in variant_quantities.items():
                try:
                    variant = ProductVariant.objects.get(id=variant_id)
                    variant.stock -= total_quantity
                    variant.save()
                    updated_variants += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Updated stock for variant {variant.name} (ID: {variant.id}): -{total_quantity} units'
                        )
                    )
                except ProductVariant.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(
                            f'Variant with ID {variant_id} not found'
                        )
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f'Error updating stock for variant ID {variant_id}: {str(e)}'
                        )
                    )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully updated stock for {updated_products} products and {updated_variants} variants'
            )
        ) 