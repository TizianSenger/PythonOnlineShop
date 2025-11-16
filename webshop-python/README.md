# Webshop Python Project

This project is a simple webshop application built with Python. It provides functionalities for managing products, users, and orders, with data stored either in CSV files or an SQLite database.

## Project Structure

```
webshop-python
├── src
│   ├── app.py                # Main entry point of the application
│   ├── config.py             # Configuration settings
│   ├── models                 # Contains data models
│   │   ├── __init__.py
│   │   ├── product.py         # Product model
│   │   ├── user.py            # User model
│   │   └── order.py           # Order model
│   ├── storage                # Data storage backends
│   │   ├── __init__.py
│   │   ├── csv_backend.py      # CSV data storage
│   │   └── sqlite_backend.py    # SQLite data storage
│   ├── api                   # API routes
│   │   ├── __init__.py
│   │   └── routes.py          # API route definitions
│   ├── services              # Business logic services
│   │   ├── catalog.py         # Product catalog management
│   │   └── checkout.py        # Checkout process management
│   └── utils                 # Utility functions
│       └── helpers.py         # Helper functions
├── data
│   └── csv                   # CSV data files
│       ├── products.csv       # Product data
│       ├── users.csv          # User data
│       └── orders.csv         # Order data
├── tests                     # Unit tests
│   ├── test_catalog.py        # Tests for catalog service
│   └── test_storage.py        # Tests for storage backends
├── requirements.txt           # Project dependencies
├── pyproject.toml            # Project configuration
├── .gitignore                # Files to ignore in version control
└── README.md                 # Project documentation
```

## Setup Instructions

1. **Clone the repository**:
   ```
   git clone <repository-url>
   cd webshop-python
   ```

2. **Install dependencies**:
   It is recommended to use a virtual environment. You can create one using:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
   Then install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. **Run the application**:
   Start the application by running:
   ```
   python src/app.py
   ```

## Usage

- Access the webshop through the provided API endpoints.
- Use the CSV files in the `data/csv` directory for initial data or switch to the SQLite backend for a more robust solution.

## Testing

Run the tests using:
```
pytest tests/
```

## License

This project is licensed under the MIT License.