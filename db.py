import sqlite3
from typing import List, Optional
from models import Customer, Product, Order, OrderItem
from datetime import datetime

# Устанавливаем путь к базе данных
DB_PATH = 'data/products.sqlite'


def create_tables():
    """
    Создает таблицы в базе данных, если они еще не созданы.

    Creates database tables if they do not exist yet.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE CHECK(email IS NOT NULL),
            phone TEXT
        );

        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL CHECK(price >= 0),
            quantity INTEGER NOT NULL CHECK(quantity >= 0)
        );

        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER REFERENCES customers(id),
            date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'Новый',
            total_amount REAL NOT NULL CHECK(total_amount >= 0)
        );

        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER REFERENCES orders(id),
            product_id INTEGER REFERENCES products(id),
            quantity INTEGER NOT NULL CHECK(quantity > 0)
        );
    """)
    conn.commit()
    conn.close()


def insert_customer(customer: Customer) -> None:
    """
    Добавляет нового клиента в базу данных.

    Parameters
    ----------
    customer : Customer
        Объект класса Customer, содержащий данные нового клиента.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO customers (name, email, phone) VALUES (?, ?, ?)",
            (customer.name, customer.email, customer.phone)
        )
        conn.commit()


def select_customers(filter_by: str = '') -> List[Customer]:
    """
    Возвращает список всех клиентов с возможностью фильтрации по имени или email.

    Parameters
    ----------
    filter_by : str, optional
        Строка для фильтрации по имени или email клиента.

    Returns
    -------
    List[Customer]
        Список объектов Customer, удовлетворяющих критерию фильтрации.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM customers WHERE name LIKE ? OR email LIKE ?"
        filter_pattern = f'%{filter_by}%'
        results = cursor.execute(query, (filter_pattern, filter_pattern)).fetchall()
        return [Customer.from_tuple(row) for row in results]


def find_customer_by_id(customer_id: int) -> Optional[Customer]:
    """
    Находит клиента по его идентификатору.

    Parameters
    ----------
    customer_id : int
        Идентификатор клиента.

    Returns
    -------
    Optional[Customer]
        Объект Customer, если клиент найден, иначе None.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM customers WHERE id=?"
        result = cursor.execute(query, (customer_id,)).fetchone()
        if result:
            return Customer.from_tuple(result)
        return None


def update_customer(customer: Customer) -> None:
    """
    Обновляет данные клиента в базе данных.

    Parameters
    ----------
    customer : Customer
        Объект класса Customer с обновленными данными.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE customers SET name=?, email=?, phone=? WHERE id=?",
            (customer.name, customer.email, customer.phone, customer.id)
        )
        conn.commit()


def delete_customer(customer_id: int) -> None:
    """
    Удаляет клиента по его идентификатору.

    Parameters
    ----------
    customer_id : int
        Идентификатор клиента.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM customers WHERE id=?", (customer_id,))
        conn.commit()


def insert_product(product: Product) -> None:
    """
    Добавляет новый продукт в базу данных.

    Parameters
    ----------
    product : Product
        Объект класса Product, содержащий данные нового продукта.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO products (name, price, quantity) VALUES (?, ?, ?)",
            (product.name, product.price, product.quantity)
        )
        conn.commit()


def select_products(filter_by: str = '') -> List[Product]:
    """
    Возвращает список всех продуктов с возможностью фильтрации по названию.

    Parameters
    ----------
    filter_by : str, optional
        Строка для фильтрации по названию продукта.

    Returns
    -------
    List[Product]
        Список объектов Product, удовлетворяющих критерию фильтрации.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM products WHERE name LIKE ?"
        filter_pattern = f'%{filter_by}%'
        results = cursor.execute(query, (filter_pattern,)).fetchall()
        return [Product.from_tuple(row) for row in results]


def find_product_by_id(product_id: int) -> Optional[Product]:
    """
    Находит продукт по его идентификатору.

    Parameters
    ----------
    product_id : int
        Идентификатор продукта.

    Returns
    -------
    Optional[Product]
        Объект Product, если продукт найден, иначе None.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM products WHERE id=?"
        result = cursor.execute(query, (product_id,)).fetchone()
        if result:
            return Product.from_tuple(result)
        return None


def update_product(product: Product) -> None:
    """
    Обновляет данные продукта в базе данных.

    Parameters
    ----------
    product : Product
        Объект класса Product с обновленными данными.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE products SET name=?, price=?, quantity=? WHERE id=?",
            (product.name, product.price, product.quantity, product.id)
        )
        conn.commit()


def delete_product(product_id: int) -> None:
    """
    Удаляет продукт по его идентификатору.

    Parameters
    ----------
    product_id : int
        Идентификатор продукта.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE id=?", (product_id,))
        conn.commit()


def insert_order(order: Order) -> int:
    """
    Добавляет новый заказ в базу данных и возвращает его идентификатор.

    Parameters
    ----------
    order : Order
        Объект класса Order, содержащий данные нового заказа.

    Returns
    -------
    int
        Идентификатор вновь созданного заказа.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO orders (customer_id, total_amount, status) VALUES (?, ?, ?)",
            (order.customer_id, order.total_amount, order.status)
        )
        order_id = cursor.lastrowid
        conn.commit()
        return order_id


def insert_order_item(order_id: int, item: OrderItem) -> None:
    """
    Добавляет новую позицию в заказ.

    Parameters
    ----------
    order_id : int
        Идентификатор заказа.
    item : OrderItem
        Объект класса OrderItem, содержащий данные новой позиции.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO order_items (order_id, product_id, quantity) VALUES (?,?,?)",
                       (order_id, item.product_id, item.quantity))
        conn.commit()


def select_orders() -> List[Order]:
    """
    Возвращает список всех заказов.

    Returns
    -------
    List[Order]
        Список объектов Order.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM orders")
        results = cursor.fetchall()
        return [Order.from_tuple(row) for row in results]


def find_order_by_id(order_id: int) -> Optional[Order]:
    """
    Находит заказ по его идентификатору.

    Parameters
    ----------
    order_id : int
        Идентификатор заказа.

    Returns
    -------
    Optional[Order]
        Объект Order, если заказ найден, иначе None.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM orders WHERE id=?"
        result = cursor.execute(query, (order_id,)).fetchone()
        if result:
            return Order.from_tuple(result)
        return None


def update_order(order_id: int, updates: dict) -> bool:
    """
    Обновляет данные заказа в базе данных только для указанных полей.

    Parameters
    ----------
    order_id : int
        Идентификатор заказа.
    updates : dict
        Словарь с изменениями полей заказа.

    Returns
    -------
    bool
        True, если запись была обновлена, иначе False.
    """
    fields_and_values = []
    for field, value in updates.items():
        fields_and_values.append(f"{field}=?")
    sql_query = f"UPDATE orders SET {','.join(fields_and_values)} WHERE id=?"
    params = tuple(updates.values()) + (order_id,)

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(sql_query, params)
        conn.commit()
        return cursor.rowcount > 0


def delete_order(order_id: int) -> None:
    """
    Удаляет заказ по его идентификатору.

    Parameters
    ----------
    order_id : int
        Идентификатор заказа.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM orders WHERE id=?", (order_id,))
        conn.commit()


def delete_order_list(order_id: int) -> None:
    """
    Удаляет все позиции заказа (order_items), связанные с указанным заказом.

    Parameters
    ----------
    order_id : int
        Идентификатор заказа.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM order_items WHERE order_id=?", (order_id,))
        conn.commit()


def find_order_list_by_id(order_id: int) -> List[OrderItem]:
    """
    Возвращает позиции заказа по его идентификатору.

    Parameters
    ----------
    order_id : int
        Идентификатор заказа.

    Returns
    -------
    List[OrderItem]
        Список объектов OrderItem, принадлежащих заказу.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        query = """
            SELECT product_id, quantity 
            FROM order_items 
            WHERE order_id=?
        """
        results = cursor.execute(query, (order_id,)).fetchall()
        return [OrderItem(product_id=row[0], quantity=row[1]) for row in results]


def select_orders_by_customer_id(customer_id: int) -> List[Order]:
    """
    Возвращает все заказы конкретного клиента.

    Parameters
    ----------
    customer_id : int
        Идентификатор клиента.

    Returns
    -------
    List[Order]
        Список объектов Order, относящихся к клиенту.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        query = """
            SELECT *
            FROM orders
            WHERE customer_id=?
        """
        results = cursor.execute(query, (customer_id,)).fetchall()
        return [Order.from_tuple(row) for row in results]


def select_orders_by_product_id(product_id: int) -> List[Order]:
    """
    Возвращает все заказы, содержащие указанный продукт.

    Parameters
    ----------
    product_id : int
        Идентификатор продукта.

    Returns
    -------
    List[Order]
        Список объектов Order, содержащих указанный продукт.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        query = """
            SELECT DISTINCT o.*
            FROM orders AS o
            JOIN order_items AS oi ON o.id = oi.order_id
            WHERE oi.product_id=?
        """
        results = cursor.execute(query, (product_id,)).fetchall()
        return [Order.from_tuple(row) for row in results]


def select_data(table_name):
    """
    Чтение данных из указанной таблицы и возвращение их в виде списка словарей.

    Используется для экспорта данных.

    Parameters
    ----------
    table_name : str
        Название таблицы для чтения данных.

    Returns
    -------
    list
        Список словарей, где ключи — это имена столбцов, а значения — данные из таблицы.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(f'SELECT * FROM {table_name}')
        headers = [desc[0] for desc in cursor.description]
        return [dict(zip(headers, row)) for row in cursor.fetchall()]


def select_analysis_data(table_name):
    """
    Чтение данных из указанной таблицы и возвращение их в сыром виде.

    Используется для нужд анализа данных.

    Parameters
    ----------
    table_name : str
        Название таблицы для чтения данных.

    Returns
    -------
    tuple
        Кортеж, состоящий из данных (list) и наименований столбцов (list).
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        query = f"SELECT * FROM {table_name}"
        res = cursor.execute(query).fetchall()
        cols = list(map(lambda x: x[0], cursor.description))
        return res, cols


def truncate_table(table_name):
    """
    Очищает таблицу перед импортом данных.

    Parameters
    ----------
    table_name : str
        Название таблицы для очистки.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(f'DELETE FROM {table_name}')
        conn.commit()


def bulk_insert_data(table_name, data):
    """
    Массивный импорт данных в таблицу.

    Parameters
    ----------
    table_name : str
        Название таблицы, в которую вносятся данные.
    data : list
        Список словарей, где каждое значение соответствует одному элементу данных.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        first_record = data[0]
        columns = ", ".join(first_record.keys())
        placeholders = ", ".join(["?"] * len(first_record))
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        cursor.executemany(query, [tuple(d.values()) for d in data])
        conn.commit()

def select_all_orders_with_items():
    """
    Извлекает данные из таблиц `orders` и `order_items`, объединяя их в удобную структуру.

    Returns
    -------
    list
        Список заказов, где каждый заказ представлен объектом с полем `items`,
        которое содержит список позиций заказа (продукт и количество).
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT o.id, o.customer_id, o.date_created, o.status, o.total_amount, oi.product_id, oi.quantity
            FROM orders o
            LEFT JOIN order_items oi ON o.id = oi.order_id
        ''')
        results = cursor.fetchall()
        # Обработка данных и группировка по заказам
        grouped_results = {}
        for row in results:
            order_id, customer_id, date_created, status, total_amount, product_id, quantity = row
            # Парсим дату создания
            date_created = datetime.strptime(date_created.split('.')[0], "%Y-%m-%d %H:%M:%S")
            # Создание или обновление структуры заказа
            if order_id not in grouped_results:
                grouped_results[order_id] = {
                    'id': order_id,
                    'customer_id': customer_id,
                    'date_created': date_created,
                    'status': status,
                    'total_amount': total_amount,
                    'items': []
                }
            # Добавляем позицию заказа
            if product_id is not None:
                grouped_results[order_id]['items'].append({'product_id': product_id, 'quantity': quantity})
        return list(grouped_results.values())