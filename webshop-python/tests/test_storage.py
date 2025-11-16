import unittest
from src.storage.csv_backend import CSVBackend
from src.storage.sqlite_backend import SQLiteBackend

class TestStorage(unittest.TestCase):

    def setUp(self):
        self.csv_backend = CSVBackend('data/csv/products.csv')
        self.sqlite_backend = SQLiteBackend('data/database.db')  # Adjust the path as needed

    def test_csv_read(self):
        products = self.csv_backend.read()
        self.assertIsInstance(products, list)
        self.assertGreater(len(products), 0)

    def test_csv_write(self):
        new_product = {'id': 4, 'name': 'Test Product', 'description': 'A product for testing', 'price': 9.99}
        self.csv_backend.write(new_product)
        products = self.csv_backend.read()
        self.assertIn(new_product, products)

    def test_sqlite_connection(self):
        self.assertTrue(self.sqlite_backend.connect())

    def test_sqlite_insert(self):
        new_user = {'id': 1, 'username': 'testuser', 'password': 'password123'}
        self.sqlite_backend.insert('users', new_user)
        users = self.sqlite_backend.fetch_all('users')
        self.assertIn(new_user, users)

    def tearDown(self):
        self.csv_backend = None
        self.sqlite_backend = None

if __name__ == '__main__':
    unittest.main()