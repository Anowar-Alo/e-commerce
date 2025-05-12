# EzyZip: Modern E-commerce Platform

A robust, scalable, and feature-rich e-commerce web application built with Django. EzyZip offers a seamless shopping experience, modern UI/UX, and a powerful admin dashboard for business management.

---

## 🚀 Features

- **User Management:** Registration, authentication, profile, and preferences
- **Product Catalog:** Categories, brands, variants, images, reviews, and search
- **Shopping Cart:** Add, update, remove, and checkout
- **Order Management:** Order placement, tracking, and history
- **Payment Integration:** Stripe, digital wallets, UPI, and more
- **Admin Dashboard:** Analytics, reporting, and product management
- **Notifications:** Email, SMS, and push notifications
- **Personalized Recommendations:** AI-driven product suggestions
- **Customer Support:** Contact forms and support tools
- **Responsive Design:** Mobile-first, Bootstrap 5 UI

---

## 🛠️ Tech Stack

- **Backend:** Django 5.x
- **Frontend:** Bootstrap 5,
- **Database:** PostgreSQL (default: SQLite for dev)
- **Async Tasks:** Celery, Redis
- **Payments:** Stripe
- **Real-time:** Django Channels
- **Admin:** Custom admin site, Unfold, Import/Export, SimpleHistory

---

## 📦 Project Structure

```
ecommerce/
├── core/         # Core logic, settings, admin, analytics
├── accounts/     # User management
├── products/     # Product catalog, brands, reviews
├── orders/       # Order processing
├── cart/         # Shopping cart
├── payments/     # Payment processing
├── static/       # Static files (CSS, JS, images)
├── templates/    # HTML templates
├── media/        # User uploads
├── manage.py     # Django entry point
└── ...
```

---

## ⚡ Quickstart

1. **Clone the repository:**
   ```sh
   git clone <repository-url>
   cd ecommerce
   ```
2. **Create and activate a virtual environment:**
   ```sh
   python -m venv venv
   venv\Scripts\activate  # On Windows
   # source venv/bin/activate  # On Linux/Mac
   ```
3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
4. **Configure environment variables:**
   - Copy `.env.example` to `.env` and update values as needed.
5. **Apply migrations:**
   ```sh
   python manage.py migrate
   ```
6. **Create a superuser:**
   ```sh
   python manage.py createsuperuser
   ```
7. **Run the development server:**
   ```sh
   python manage.py runserver
   ```
8. **Access the app:**
   - Frontend: [http://localhost:8000/](http://localhost:8000/)
   - Admin: [http://localhost:8000/admin/](http://localhost:8000/admin/)

---

## 🧑‍💻 Development & Testing

- **Run tests:**
  ```sh
  python manage.py test
  ```
- **Code style:**
  ```sh
  flake8
  ```
- **Update requirements:**
  ```sh
  pip freeze > requirements.txt
  ```

---

## 🚚 Deployment

1. Set production environment variables
2. Configure static/media file hosting
3. Set up Redis
4. Run migrations and collectstatic
5. Use a WSGI/ASGI server (e.g., Gunicorn, Daphne)
6. Set up a reverse proxy (e.g., Nginx)

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to your branch
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License. See the LICENSE file for details.

---

## 📞 Contact & Support

- Email: ahalo1164@gmail.com
- Phone: +8801610172044

For issues, suggestions, or contributions, please open an issue or pull request on GitHub.
