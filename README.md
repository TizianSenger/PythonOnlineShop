# Python Online Shop

A full-featured e-commerce web application built with Python and Flask. This online shop provides a complete shopping experience with user authentication, product management, shopping cart functionality, and integrated payment processing.

## 🚀 Features

### Customer Features
- **Product Browsing**: Browse products with search, category filtering, and price range filters
- **Product Details**: View detailed product information with multiple images
- **User Authentication**: Secure registration and login system with password hashing
- **Shopping Cart**: Add, update, and remove items from cart with real-time updates
- **Order Management**: Place orders and view order history
- **Email Notifications**: Automated registration confirmation emails
- **Payment Integration**: Support for Stripe and PayPal payments

### Admin Features
- **Product Management**: Add, edit, and delete products with multiple image uploads
- **Image Management**: Upload up to 20 images per product with easy deletion
- **Order Overview**: View all customer orders and their status
- **User Management**: Manage users and roles (admin/user)
- **Inventory Control**: Track and update product stock levels

### Technical Features
- **Flexible Storage**: CSV and SQLite database backend options
- **RESTful API**: API endpoints for programmatic access
- **Session Management**: Secure session handling with Flask
- **Responsive Design**: Mobile-friendly user interface
- **Image Upload**: Secure file upload with validation
- **Email Integration**: SMTP configuration for transactional emails

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Virtual environment tool (venv)
- SMTP server credentials (for email functionality)
- Stripe and/or PayPal accounts (for payment processing)

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/TizianSenger/PythonOnlineShop.git
cd PythonOnlineShop
```

### 2. Set Up Virtual Environment

```bash
python -m venv .venv
```

**Activate the virtual environment:**

- On Linux/Mac:
  ```bash
  source .venv/bin/activate
  ```

- On Windows:
  ```bash
  .venv\Scripts\activate
  ```

### 3. Install Dependencies

```bash
cd webshop-python
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root with the following configuration:

```env
# Flask Configuration
SECRET_KEY=your-secret-key-here

# SMTP Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password

# Admin Access
ADMIN_PIN=your-admin-pin

# Stripe Configuration (Optional)
STRIPE_SECRET_KEY=your-stripe-secret-key
STRIPE_PUBLISHABLE_KEY=your-stripe-publishable-key

# PayPal Configuration (Optional)
PAYPAL_CLIENT_ID=your-paypal-client-id
PAYPAL_CLIENT_SECRET=your-paypal-client-secret
PAYPAL_MODE=sandbox

# Application URL
APP_BASE_URL=http://localhost:5000
```

### 5. Initialize Data Directory

The application will automatically create the necessary data directories on first run. CSV files for products, users, and orders will be stored in `webshop-python/data/csv/`.

## 🚀 Running the Application

### Development Mode

```bash
cd webshop-python/src
python app.py
```

The application will start on `http://localhost:5000` by default.

### Production Deployment

For production deployment, use a WSGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 src.app:app
```

## 📁 Project Structure

```
PythonOnlineShop/
├── webshop-python/           # Main application directory
│   ├── src/                  # Source code
│   │   ├── app.py            # Flask application entry point
│   │   ├── config.py         # Configuration settings
│   │   ├── models/           # Data models
│   │   │   ├── product.py    # Product model
│   │   │   ├── user.py       # User model
│   │   │   └── order.py      # Order model
│   │   ├── storage/          # Data storage backends
│   │   │   ├── csv_backend.py    # CSV storage implementation
│   │   │   └── sqlite_backend.py # SQLite storage implementation
│   │   ├── api/              # API routes
│   │   │   ├── routes.py     # General API endpoints
│   │   │   └── checkout_routes.py # Checkout endpoints
│   │   ├── services/         # Business logic
│   │   │   ├── catalog.py    # Product catalog service
│   │   │   └── checkout.py   # Checkout service
│   │   ├── templates/        # HTML templates
│   │   ├── static/           # Static files (CSS, JS, images)
│   │   └── utils/            # Utility functions
│   ├── data/                 # Data storage
│   │   ├── csv/              # CSV data files
│   │   └── webshop.db        # SQLite database
│   ├── tests/                # Test suite
│   ├── requirements.txt      # Python dependencies
│   └── pyproject.toml        # Project configuration
├── .venv/                    # Virtual environment
├── .gitignore                # Git ignore rules
└── README.md                 # This file
```

## 🎯 Usage

### For Customers

1. **Browse Products**: Visit the home page to see all available products
2. **Search & Filter**: Use search bar and category/price filters to find products
3. **Register/Login**: Create an account or log in to shop
4. **Add to Cart**: Click on products and add them to your cart
5. **Checkout**: Review your cart and proceed to checkout
6. **Payment**: Choose Stripe or PayPal to complete your purchase
7. **View Orders**: Check your order history from the orders page

### For Administrators

1. **Admin Registration**: Register with an admin role using the admin PIN
2. **Product Management**: Access `/admin/products` to manage products
3. **Add Products**: Fill in product details and upload images
4. **Edit/Delete**: Modify existing products or remove them
5. **View Orders**: See all customer orders and their status
6. **Manage Inventory**: Update stock levels for products

## 🔌 API Endpoints

The application provides RESTful API endpoints under `/api/`:

### Products
- `GET /api/products` - List all products

### Users
- `POST /api/register` - Register new user

### Orders
- `POST /api/order` - Create new order

**Note**: Product management, order viewing, and other administrative functions are available through the web interface at `/admin/products` and `/orders`.

## 🧪 Testing

Run the test suite using pytest:

```bash
cd webshop-python
pytest tests/
```

Run tests with coverage:

```bash
pytest tests/ --cov=src --cov-report=html
```

## 🔧 Configuration Options

### Storage Backend

The application supports two storage backends:

1. **CSV Backend** (default): Stores data in CSV files
   - Good for development and small-scale deployments
   - Files located in `data/csv/`

2. **SQLite Backend**: Uses SQLite database
   - Better performance for larger datasets
   - Database file: `data/app.db`

To switch backends, modify the storage initialization in `app.py`.

### Email Configuration

For email functionality to work:

1. Use Gmail SMTP or another email provider
2. For Gmail, create an [App Password](https://support.google.com/accounts/answer/185833)
3. Update SMTP credentials in `.env` file

### Payment Gateways

#### Stripe Setup
1. Sign up at [Stripe](https://stripe.com)
2. Get your API keys from the dashboard
3. Add keys to `.env` file

#### PayPal Setup
1. Sign up at [PayPal Developer](https://developer.paypal.com)
2. Create a sandbox application
3. Add client ID and secret to `.env` file
4. Use sandbox accounts for testing

## 🛡️ Security Considerations

- Passwords are hashed using Werkzeug's security functions
- Session data is encrypted using Flask's secret key
- File uploads are validated and sanitized
- Admin access requires a PIN for registration
- CSRF protection should be implemented for production
- Use HTTPS in production environments

## 🐛 Troubleshooting

### Common Issues

**Port already in use:**
```bash
# Modify the port in app.py (last line) or set environment variable:
export FLASK_RUN_PORT=5001
flask run
```

**Module not found errors:**
```bash
# Ensure virtual environment is activated and dependencies installed
pip install -r requirements.txt
```

**Email not sending:**
- Check SMTP credentials in `.env`
- For Gmail, ensure less secure apps or app passwords are configured
- Check firewall settings for port 587

**Payment integration issues:**
- Verify API keys are correct
- Ensure you're using test/sandbox mode for development
- Check payment provider dashboard for errors

## 📝 Development

### Adding New Features

1. Create feature branch: `git checkout -b feature/your-feature`
2. Implement changes following the existing code structure
3. Add tests for new functionality
4. Update documentation
5. Submit pull request

### Code Style

- Follow PEP 8 style guide for Python code
- Use meaningful variable and function names
- Add docstrings for functions and classes
- Keep functions small and focused

## 📄 License

This project is licensed under the MIT License. See the LICENSE file for details.

## 👥 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📧 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Contact the maintainers

## 🙏 Acknowledgments

- Flask framework and its extensions
- Python community for excellent libraries
- All contributors to this project

---

**Note**: This is a learning project. For production use, additional security hardening, scalability improvements, and comprehensive testing are recommended.
