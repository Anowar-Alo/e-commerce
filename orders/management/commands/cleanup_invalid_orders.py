from django.core.management.base import BaseCommand
from orders.models import Order
from django.db import transaction
from django.utils import timezone

class Command(BaseCommand):
    help = 'Clean up invalid orders (orders without items)'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting cleanup of invalid orders...')
        
        # Get all delivered and paid orders
        orders = Order.objects.filter(status='delivered', payment_status='paid')
        order_count = orders.count()
        self.stdout.write(f'Found {order_count} delivered and paid orders')
        
        if order_count == 0:
            self.stdout.write(self.style.WARNING('No delivered and paid orders found'))
            return
        
        # Find orders without items
        invalid_orders = []
        for order in orders:
            if order.items.count() == 0:
                invalid_orders.append(order)
        
        if not invalid_orders:
            self.stdout.write(self.style.SUCCESS('No invalid orders found'))
            return
        
        self.stdout.write(f'Found {len(invalid_orders)} invalid orders')
        
        # Update invalid orders
        with transaction.atomic():
            for order in invalid_orders:
                old_status = order.status
                order.status = 'processing'
                order.save()
                self.stdout.write(
                    self.style.WARNING(
                        f'Order {order.order_number} marked as processing (was {old_status})'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully cleaned up {len(invalid_orders)} invalid orders'
            )
        ) 