from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model, login, logout, authenticate
from products.models import Product, Category
from orders.models import Order, OrderItem
from django.db.models import Sum, Count, Avg, F, ExpressionWrapper, FloatField
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import UserProfile, SiteSettings
from .forms import UserProfileForm, UserUpdateForm, PaymentMethodForm, CustomUserCreationForm, ProfileUpdateForm, ContactForm
from django.contrib import messages
from payments.models import PaymentMethod, Transaction
from django.db.models.functions import TruncDate, TruncMonth, TruncYear, ExtractHour
from products.views import get_ai_recommendations
from django.conf import settings
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import HttpResponseForbidden, JsonResponse
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator
from accounts.models import CustomUser
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.mail import send_mail

User = CustomUser

@staff_member_required
def admin_dashboard(request):
    # Stats
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    total_users = get_user_model().objects.count()
    total_customers = get_user_model().objects.filter(is_staff=False).count()
    low_stock_products = Product.objects.filter(stock__lt=10).count()

    # Revenue - only count completed and paid orders
    total_revenue = Order.objects.filter(status='completed', payment_status='paid').aggregate(total=Sum('total'))['total'] or 0
    week_ago = timezone.now() - timedelta(days=7)
    weekly_revenue = Order.objects.filter(status='completed', payment_status='paid', created_at__gte=week_ago).aggregate(total=Sum('total'))['total'] or 0

    # Recent orders
    recent_orders = Order.objects.filter(created_at__gte=week_ago).count()
    recent_orders_list = Order.objects.order_by('-created_at')[:5]

    # Daily sales for the last 7 days
    daily_sales = []
    for i in range(7):
        day = timezone.now().date() - timedelta(days=6-i)
        total = Order.objects.filter(status='completed', payment_status='paid', created_at__date=day).aggregate(total=Sum('total'))['total'] or 0
        daily_sales.append({'day': day.strftime('%a'), 'total': float(total)})

    context = {
        'total_products': total_products,
        'total_orders': total_orders,
        'total_users': total_users,
        'total_customers': total_customers,
        'low_stock_products': low_stock_products,
        'total_revenue': total_revenue,
        'weekly_revenue': weekly_revenue,
        'recent_orders': recent_orders,
        'recent_orders_list': recent_orders_list,
        'daily_sales': daily_sales,
    }
    return render(request, 'admin/dashboard.html', context)

@login_required
def user_dashboard(request):
    """User dashboard view."""
    return render(request, 'core/user_dashboard.html')

@login_required
def profile(request):
    # Get or create user profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        payment_form = PaymentMethodForm(request.POST)
        
        if 'payment_submit' in request.POST:
            if payment_form.is_valid():
                payment_method = payment_form.save(commit=False)
                payment_method.user = request.user
                payment_method.save()
                messages.success(request, 'Payment method added successfully.')
                return redirect('core:profile')
        elif user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('core:profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=profile)
        payment_form = PaymentMethodForm()
    
    payment_methods = request.user.payment_methods.all()
    context = {
        'user': request.user,
        'profile': profile,
        'user_form': user_form,
        'profile_form': profile_form,
        'payment_form': payment_form,
        'payment_methods': payment_methods,
    }
    return render(request, 'core/profile.html', context)

@login_required
def delete_payment_method(request, payment_method_id):
    payment_method = get_object_or_404(PaymentMethod, id=payment_method_id, user=request.user)
    if request.method == 'POST':
        payment_method.delete()
        messages.success(request, 'Payment method deleted successfully.')
    return redirect('core:profile')

@login_required
def set_default_payment_method(request, payment_method_id):
    payment_method = get_object_or_404(PaymentMethod, id=payment_method_id, user=request.user)
    if request.method == 'POST':
        payment_method.is_default = True
        payment_method.save()
        messages.success(request, 'Default payment method updated successfully.')
    return redirect('core:profile')

@staff_member_required
def admin_analytics(request):
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
    }
    return render(request, 'admin/analytics.html', context)

def home(request):
    # Get featured products with pagination (most recent products)
    featured_products = Product.objects.filter(is_active=True).order_by('-created_at')
    paginator = Paginator(featured_products, 10)  # Show 10 products per page
    page_number = request.GET.get('page')
    featured_products_page = paginator.get_page(page_number)

    # Only show AI recommendations for authenticated users
    ai_recommendations = []
    if request.user.is_authenticated:
        ai_recommendations = get_ai_recommendations(request.user)

    # Get featured categories
    featured_categories = Category.objects.filter(is_active=True)[:6]

    context = {
        'featured_products': featured_products_page,
        'ai_recommendations': ai_recommendations,
        'featured_categories': featured_categories,
    }
    return render(request, 'home.html', context)

def contact(request):
    """Contact page view."""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Save the message
            contact_message = form.save()
            
            # Get site settings for email
            site_settings = SiteSettings.get_settings()
            
            # Send email notification
            try:
                send_mail(
                    subject=f'New Contact Form Submission: {contact_message.subject}',
                    message=f'''
                    Name: {contact_message.name}
                    Email: {contact_message.email}
                    Subject: {contact_message.subject}
                    
                    Message:
                    {contact_message.message}
                    ''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[site_settings.contact_email],
                    fail_silently=False,
                )
                
                # Send confirmation email to user
                send_mail(
                    subject='Thank you for contacting us',
                    message=f'''
                    Dear {contact_message.name},
                    
                    Thank you for contacting us. We have received your message and will get back to you as soon as possible.
                    
                    Your message:
                    {contact_message.message}
                    
                    Best regards,
                    {site_settings.site_name} Team
                    ''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[contact_message.email],
                    fail_silently=False,
                )
                
                messages.success(request, 'Your message has been sent successfully! We will get back to you soon.')
                return redirect('core:contact')
            except Exception as e:
                messages.error(request, 'There was an error sending your message. Please try again later.')
    else:
        form = ContactForm()
    
    # Get site settings for contact information
    site_settings = SiteSettings.get_settings()
    
    context = {
        'form': form,
        'site_settings': site_settings,
    }
    return render(request, 'core/contact.html', context)

@ensure_csrf_cookie
def debug_csrf(request):
    """Debug CSRF token view."""
    return render(request, 'core/debug_csrf.html')

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('core:home')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Account created for {user.username}!')
            return redirect('core:home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'core/register.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('core:home')

@login_required
def profile_update(request):
    # Get or create user profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('core:profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=profile)
    
    context = {
        'user': request.user,
        'profile': profile,
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'core/profile_update.html', context)