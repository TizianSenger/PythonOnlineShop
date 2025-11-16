import unittest
from src.services.catalog import CatalogService
from src.models.product import Product

class TestCatalogService(unittest.TestCase):

    def setUp(self):
        self.catalog_service = CatalogService()
        self.sample_products = [
            Product(id=1, name="Product 1", description="Description 1", price=10.0),
            Product(id=2, name="Product 2", description="Description 2", price=20.0),
            Product(id=3, name="Product 3", description="Description 3", price=30.0),
        ]
        self.catalog_service.products = self.sample_products

    def test_get_all_products(self):
        products = self.catalog_service.get_all_products()
        self.assertEqual(len(products), 3)

    def test_filter_products_by_price(self):
        filtered_products = self.catalog_service.filter_products_by_price(15.0)
        self.assertEqual(len(filtered_products), 2)

    def test_get_product_by_id(self):
        product = self.catalog_service.get_product_by_id(1)
        self.assertEqual(product.name, "Product 1")

    def test_get_product_by_nonexistent_id(self):
        product = self.catalog_service.get_product_by_id(999)
        self.assertIsNone(product)

if __name__ == '__main__':
    unittest.main()