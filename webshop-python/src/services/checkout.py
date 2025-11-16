class CheckoutService:
    def __init__(self, storage_backend):
        self.storage_backend = storage_backend

    def process_order(self, user_id, product_id, quantity):
        order = {
            'user_id': user_id,
            'product_id': product_id,
            'quantity': quantity
        }
        self.storage_backend.save_order(order)
        return order

    def calculate_total(self, product_id, quantity):
        product = self.storage_backend.get_product(product_id)
        if product:
            return product['price'] * quantity
        return None

    def handle_payment(self, order, payment_info):
        # Here you would integrate with a payment gateway
        # For now, we'll just simulate a successful payment
        return True if payment_info.get('valid') else False

    def complete_checkout(self, user_id, product_id, quantity, payment_info):
        order = self.process_order(user_id, product_id, quantity)
        total = self.calculate_total(product_id, quantity)
        if self.handle_payment(order, payment_info):
            return {
                'status': 'success',
                'order': order,
                'total': total
            }
        return {
            'status': 'failed',
            'order': order,
            'total': total
        }