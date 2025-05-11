from decimal import Decimal
from django.conf import settings
from products.models import Product

class Cart:
    def __init__(self, request):
        """
        Initialize the cart.
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # save an empty cart in the session
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, update_quantity=False):
        """
        Add a product to the cart or update its quantity.
        """
        product_id = str(product.id)
        
        # Check stock availability
        if product.stock <= 0:
            raise ValueError(f'Product {product.name} is out of stock')
        
        # Ensure quantity doesn't exceed available stock
        if quantity > product.stock:
            quantity = product.stock
        
        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'price': str(product.price),
                'product_id': product.id
            }
        if update_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            new_quantity = self.cart[product_id]['quantity'] + quantity
            if new_quantity > product.stock:
                new_quantity = product.stock
            self.cart[product_id]['quantity'] = new_quantity
        self.save()

    def save(self):
        """
        Mark the session as modified to make sure it gets saved.
        """
        self.session.modified = True

    def remove(self, product):
        """
        Remove a product from the cart.
        """
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        """
        Iterate over the items in the cart and get the products from the database.
        """
        product_ids = [int(id) for id in self.cart.keys()]
        # get the product objects and add them to the cart
        products = {str(p.id): p for p in Product.objects.filter(id__in=product_ids)}
        cart = self.cart.copy()
        
        # Add product objects to cart items
        for item_id, item in cart.items():
            if item_id in products:
                item['product'] = products[item_id]
                item['price'] = Decimal(item['price'])
                item['total_price'] = item['price'] * item['quantity']
                yield item
            else:
                # Remove items with missing products
                del self.cart[item_id]
                self.save()

    def __len__(self):
        """
        Count all items in the cart.
        """
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        """
        Calculate the total cost of the items in the cart.
        """
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        """
        Remove cart from session.
        """
        del self.session[settings.CART_SESSION_ID]
        self.save() 