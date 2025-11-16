class CatalogService:
    def __init__(self, storage_backend):
        self.storage_backend = storage_backend

    def get_all_products(self):
        return self.storage_backend.get_all_products()

    def get_product_by_id(self, product_id):
        return self.storage_backend.get_product_by_id(product_id)

    def filter_products(self, **filters):
        products = self.get_all_products()
        for key, value in filters.items():
            products = [product for product in products if product.get(key) == value]
        return products

    def add_product(self, product):
        self.storage_backend.add_product(product)

    def update_product(self, product_id, updated_product):
        self.storage_backend.update_product(product_id, updated_product)

    def delete_product(self, product_id):
        self.storage_backend.delete_product(product_id)