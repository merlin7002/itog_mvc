import unittest
from models import Customer, Product, OrderItem, Order
from datetime import datetime

class TestModels(unittest.TestCase):

    def test_customer_class(self):
        # Тестируем создание объекта Customer
        customer = Customer(id=1, name="John Doe", email="john@example.com", phone="+1234567890")
        self.assertEqual(customer.id, 1)
        self.assertEqual(customer.name, "John Doe")
        self.assertEqual(customer.email, "john@example.com")
        self.assertEqual(customer.phone, "+1234567890")

        # Тестируем класс-метод from_tuple
        tuple_data = (1, "Jane Smith", "jane@example.com", "+0987654321")
        customer_from_tuple = Customer.from_tuple(tuple_data)
        self.assertIsInstance(customer_from_tuple, Customer)
        self.assertEqual(customer_from_tuple.id, 1)
        self.assertEqual(customer_from_tuple.name, "Jane Smith")
        self.assertEqual(customer_from_tuple.email, "jane@example.com")
        self.assertEqual(customer_from_tuple.phone, "+0987654321")

    def test_product_class(self):
        # Тестируем создание объекта Product
        product = Product(id=1, name="Phone", price=500.0, quantity=10)
        self.assertEqual(product.id, 1)
        self.assertEqual(product.name, "Phone")
        self.assertEqual(product.price, 500.0)
        self.assertEqual(product.quantity, 10)

        # Тестируем класс-метод from_tuple
        tuple_data = (1, "Laptop", 1000.0, 5)
        product_from_tuple = Product.from_tuple(tuple_data)
        self.assertIsInstance(product_from_tuple, Product)
        self.assertEqual(product_from_tuple.id, 1)
        self.assertEqual(product_from_tuple.name, "Laptop")
        self.assertEqual(product_from_tuple.price, 1000.0)
        self.assertEqual(product_from_tuple.quantity, 5)

    def test_order_item_class(self):
        # Тестируем создание объекта OrderItem
        order_item = OrderItem(product_id=1, quantity=2)
        self.assertEqual(order_item.product_id, 1)
        self.assertEqual(order_item.quantity, 2)

    def test_order_class(self):
        # Тестируем создание объекта Order
        now = datetime.now()
        order = Order(
            id=1,
            customer_id=1,
            items=[
                OrderItem(product_id=1, quantity=2),
                OrderItem(product_id=2, quantity=3)
            ],
            date_created=now,
            status="Выполнен",
            total_amount=1500.0
        )
        self.assertEqual(order.id, 1)
        self.assertEqual(order.customer_id, 1)
        self.assertEqual(len(order.items), 2)
        self.assertEqual(order.date_created, now)
        self.assertEqual(order.status, "Выполнен")
        self.assertEqual(order.total_amount, 1500.0)

        # Тестируем класс-метод from_tuple
        tuple_data = (1, 1, "2023-10-01 12:00:00", "Оплачен", 1000.0)
        order_from_tuple = Order.from_tuple(tuple_data)
        self.assertIsInstance(order_from_tuple, Order)
        self.assertEqual(order_from_tuple.id, 1)
        self.assertEqual(order_from_tuple.customer_id, 1)
        self.assertEqual(order_from_tuple.date_created.year, 2023)
        self.assertEqual(order_from_tuple.date_created.month, 10)
        self.assertEqual(order_from_tuple.date_created.day, 1)
        self.assertEqual(order_from_tuple.status, "Оплачен")
        self.assertEqual(order_from_tuple.total_amount, 1000.0)

if __name__ == '__main__':
    unittest.main()