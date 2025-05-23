# Generated by Django 4.2.10 on 2025-05-04 16:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Dashboard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_orders', models.IntegerField(default=0)),
                ('total_revenue', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('total_products', models.IntegerField(default=0)),
                ('total_customers', models.IntegerField(default=0)),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Dashboard',
                'verbose_name_plural': 'Dashboard',
            },
        ),
        migrations.CreateModel(
            name='EmailTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='name')),
                ('subject', models.CharField(max_length=255, verbose_name='subject')),
                ('html_content', models.TextField(verbose_name='HTML content')),
                ('text_content', models.TextField(verbose_name='text content')),
                ('is_active', models.BooleanField(default=True, verbose_name='active')),
                ('variables', models.JSONField(help_text='Variables that can be used in the template', verbose_name='variables')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated at')),
            ],
            options={
                'verbose_name': 'email template',
                'verbose_name_plural': 'email templates',
            },
        ),
        migrations.CreateModel(
            name='PushNotificationTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='name')),
                ('title', models.CharField(max_length=255, verbose_name='title')),
                ('body', models.TextField(verbose_name='body')),
                ('image_url', models.URLField(blank=True, verbose_name='image URL')),
                ('action_url', models.URLField(blank=True, verbose_name='action URL')),
                ('is_active', models.BooleanField(default=True, verbose_name='active')),
                ('variables', models.JSONField(help_text='Variables that can be used in the template', verbose_name='variables')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated at')),
            ],
            options={
                'verbose_name': 'push notification template',
                'verbose_name_plural': 'push notification templates',
            },
        ),
        migrations.CreateModel(
            name='SiteSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('site_name', models.CharField(max_length=100)),
                ('site_description', models.TextField(blank=True)),
                ('contact_email', models.EmailField(max_length=254)),
                ('contact_phone', models.CharField(max_length=20)),
                ('address', models.TextField(blank=True, verbose_name='address')),
                ('facebook_url', models.URLField(blank=True, verbose_name='Facebook URL')),
                ('twitter_url', models.URLField(blank=True, verbose_name='Twitter URL')),
                ('instagram_url', models.URLField(blank=True, verbose_name='Instagram URL')),
                ('linkedin_url', models.URLField(blank=True, verbose_name='LinkedIn URL')),
                ('meta_title', models.CharField(blank=True, max_length=100, verbose_name='meta title')),
                ('meta_description', models.TextField(blank=True, verbose_name='meta description')),
                ('meta_keywords', models.CharField(blank=True, max_length=255, verbose_name='meta keywords')),
                ('maintenance_mode', models.BooleanField(default=False, verbose_name='maintenance mode')),
                ('maintenance_message', models.TextField(blank=True, verbose_name='maintenance message')),
                ('google_analytics_id', models.CharField(blank=True, max_length=50, verbose_name='Google Analytics ID')),
                ('facebook_pixel_id', models.CharField(blank=True, max_length=50, verbose_name='Facebook Pixel ID')),
                ('currency', models.CharField(default='USD', max_length=3, verbose_name='currency')),
                ('currency_symbol', models.CharField(default='$', max_length=5, verbose_name='currency symbol')),
                ('tax_rate', models.DecimalField(decimal_places=2, default=0, max_digits=5, verbose_name='tax rate')),
                ('free_shipping_threshold', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='free shipping threshold')),
                ('shipping_cost', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='shipping cost')),
                ('primary_color', models.CharField(default='#4CAF50', max_length=7, verbose_name='primary color')),
                ('secondary_color', models.CharField(default='#2196F3', max_length=7, verbose_name='secondary color')),
                ('accent_color', models.CharField(default='#FF9800', max_length=7, verbose_name='accent color')),
                ('logo', models.ImageField(blank=True, null=True, upload_to='settings/', verbose_name='logo')),
                ('favicon', models.ImageField(blank=True, null=True, upload_to='settings/', verbose_name='favicon')),
                ('cache_timeout', models.IntegerField(default=3600, verbose_name='cache timeout')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Site Setting',
                'verbose_name_plural': 'Site Settings',
            },
        ),
        migrations.CreateModel(
            name='SMSTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='name')),
                ('content', models.TextField(verbose_name='content')),
                ('is_active', models.BooleanField(default=True, verbose_name='active')),
                ('variables', models.JSONField(help_text='Variables that can be used in the template', verbose_name='variables')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated at')),
            ],
            options={
                'verbose_name': 'SMS template',
                'verbose_name_plural': 'SMS templates',
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bio', models.TextField(blank=True, max_length=500)),
                ('avatar', models.ImageField(blank=True, null=True, upload_to='avatars/')),
                ('phone_number', models.CharField(blank=True, max_length=20)),
                ('address', models.CharField(blank=True, max_length=255)),
                ('city', models.CharField(blank=True, max_length=100)),
                ('state', models.CharField(blank=True, max_length=100)),
                ('country', models.CharField(blank=True, max_length=100)),
                ('postal_code', models.CharField(blank=True, max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='core_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('order', 'Order'), ('payment', 'Payment'), ('shipping', 'Shipping'), ('account', 'Account'), ('product', 'Product'), ('system', 'System')], max_length=20, verbose_name='type')),
                ('level', models.CharField(choices=[('info', 'Information'), ('success', 'Success'), ('warning', 'Warning'), ('error', 'Error')], default='info', max_length=20, verbose_name='level')),
                ('title', models.CharField(max_length=255, verbose_name='title')),
                ('message', models.TextField(verbose_name='message')),
                ('object_id', models.PositiveIntegerField(blank=True, null=True)),
                ('is_read', models.BooleanField(default=False, verbose_name='read')),
                ('is_sent', models.BooleanField(default=False, verbose_name='sent')),
                ('metadata', models.JSONField(blank=True, null=True, verbose_name='metadata')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated at')),
                ('content_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'notification',
                'verbose_name_plural': 'notifications',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Audit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(choices=[('create', 'Create'), ('update', 'Update'), ('delete', 'Delete'), ('view', 'View'), ('login', 'Login'), ('logout', 'Logout'), ('other', 'Other')], max_length=20, verbose_name='action')),
                ('object_id', models.PositiveIntegerField()),
                ('ip_address', models.GenericIPAddressField(verbose_name='IP address')),
                ('user_agent', models.CharField(max_length=255, verbose_name='user agent')),
                ('changes', models.JSONField(blank=True, null=True, verbose_name='changes')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'audit log',
                'verbose_name_plural': 'audit logs',
                'ordering': ['-created_at'],
            },
        ),
    ]
