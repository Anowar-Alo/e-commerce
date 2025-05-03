from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from .models import Product, Category, ProductReview, Brand
from .forms import ReviewForm
from orders.models import Order, OrderItem
from django.utils import timezone

def get_ai_recommendations(user):
    recommendations = []
    
    # Get user's purchase history
    if user.is_authenticated:
        # Get products from user's order history
        purchased_products = Product.objects.filter(
            orderitem__order__user=user,
            orderitem__order__status__in=['delivered', 'completed']
        ).distinct()
        
        # Get categories of purchased products
        purchased_categories = Category.objects.filter(
            products__in=purchased_products
        ).distinct()
        
        # Get similar products from same categories
        similar_products = Product.objects.filter(
            category__in=purchased_categories,
            is_active=True
        ).exclude(
            id__in=purchased_products
        ).distinct()
        
        # Get popular products from same categories
        popular_products = Product.objects.filter(
            category__in=purchased_categories,
            is_active=True
        ).annotate(
            order_count=Count('orderitem')
        ).order_by('-order_count')
        
        # Get trending products (based on recent orders)
        trending_products = Product.objects.filter(
            is_active=True
        ).annotate(
            recent_orders=Count('orderitem', filter=Q(orderitem__order__created_at__gte=timezone.now() - timezone.timedelta(days=30)))
        ).order_by('-recent_orders')
        
        # Combine recommendations with priority
        recommendations.extend(list(similar_products[:3]))
        recommendations.extend(list(popular_products[:3]))
        recommendations.extend(list(trending_products[:2]))
    
    # If no recommendations or user not authenticated, show popular and trending products
    if not recommendations:
        # Get popular products
        popular_products = Product.objects.filter(
            is_active=True
        ).annotate(
            order_count=Count('orderitem')
        ).order_by('-order_count')[:4]
        
        # Get trending products
        trending_products = Product.objects.filter(
            is_active=True
        ).annotate(
            recent_orders=Count('orderitem', filter=Q(orderitem__order__created_at__gte=timezone.now() - timezone.timedelta(days=30)))
        ).order_by('-recent_orders')[:4]
        
        recommendations.extend(list(popular_products))
        recommendations.extend(list(trending_products))
    
    # Remove duplicates while preserving order
    seen = set()
    unique_recommendations = []
    for product in recommendations:
        if product.id not in seen:
            seen.add(product.id)
            unique_recommendations.append(product)
    
    return unique_recommendations[:8]  # Return at most 8 unique recommendations

def home(request):
    featured_categories = Category.objects.filter(is_active=True)[:6]
    ai_recommendations = get_ai_recommendations(request.user)
    
    context = {
        'featured_categories': featured_categories,
        'ai_recommendations': ai_recommendations,
    }
    return render(request, 'home.html', context)

def product_list(request, slug=None):
    products = Product.objects.filter(is_active=True)
    
    # Get filter parameters
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    category_id = request.GET.get('category')
    brand_id = request.GET.get('brand')
    sort = request.GET.get('sort', 'name')
    
    # Filter by category if slug is provided
    if slug:
        category = get_object_or_404(Category, slug=slug, is_active=True)
        products = products.filter(category=category)
    elif category_id:
        products = products.filter(category_id=category_id)
    
    # Apply brand filter
    if brand_id:
        products = products.filter(brand_id=brand_id)
    
    # Apply price range filters
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    
    # Apply sorting
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'name':
        products = products.order_by('name')
    elif sort == 'newest':
        products = products.order_by('-created_at')
    
    # Get all categories and brands for filter dropdowns
    categories = Category.objects.filter(is_active=True)
    brands = Brand.objects.filter(is_active=True)
    
    context = {
        'products': products,
        'category': category if slug else None,
        'categories': categories,
        'brands': brands,
        'selected_category': category_id,
        'selected_brand': brand_id,
        'min_price': min_price,
        'max_price': max_price,
        'sort': sort,
    }
    return render(request, 'products/product_list.html', context)

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    reviews = product.reviews.all()
    review_form = None
    can_review = False

    if request.user.is_authenticated:
        # Check if user has purchased the product
        has_purchased = OrderItem.objects.filter(
            order__user=request.user,
            product=product,
            order__status__in=['delivered', 'completed']
        ).exists()
        
        if has_purchased:
            can_review = True
            # Check if user has already reviewed
            has_reviewed = ProductReview.objects.filter(product=product, user=request.user).exists()
            if not has_reviewed:
                review_form = ReviewForm()

    if request.method == 'POST' and can_review:
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.product = product
            review.user = request.user
            review.is_verified_purchase = True
            review.save()
            messages.success(request, 'Your review has been submitted!')
            return redirect('products:product_detail', slug=slug)

    context = {
        'product': product,
        'reviews': reviews,
        'review_form': review_form,
        'can_review': can_review,
    }
    return render(request, 'products/product_detail.html', context)

def search(request):
    query = request.GET.get('q', '')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    category_id = request.GET.get('category')
    sort = request.GET.get('sort', 'name')
    
    # Base queryset
    products = Product.objects.filter(is_active=True)
    
    # Apply search query
    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(category__name__icontains=query)  # Add category name search
        )
    
    # Apply category filter
    if category_id:
        products = products.filter(category_id=category_id)
    
    # Apply price filters
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    
    # Apply sorting
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'name':
        products = products.order_by('name')
    elif sort == 'newest':
        products = products.order_by('-created_at')
    
    # Get all active categories for the filter dropdown
    categories = Category.objects.filter(is_active=True)
    
    # Pagination
    paginator = Paginator(products, 12)  # Show 12 products per page
    page = request.GET.get('page')
    products = paginator.get_page(page)
    
    context = {
        'products': products,
        'query': query,
        'min_price': min_price,
        'max_price': max_price,
        'category_id': category_id,
        'categories': categories,
        'sort': sort,
    }
    
    return render(request, 'products/search_results.html', context)

def category_list(request):
    categories = Category.objects.filter(is_active=True)
    return render(request, 'products/category_list.html', {'categories': categories})

# Create your views here 