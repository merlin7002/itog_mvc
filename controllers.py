from models import Customer, Product, Order, OrderItem
from datetime import datetime
from db import (
    insert_customer, select_customers, delete_customer, update_customer,
    insert_product, select_products, delete_product, update_product,
    insert_order, select_orders, delete_order, delete_order_list, insert_order_item,
    find_customer_by_id, find_product_by_id, find_order_by_id, find_order_list_by_id,
    select_orders_by_customer_id, select_orders_by_product_id, update_order,
    select_data, truncate_table, bulk_insert_data, create_tables, select_all_orders_with_items,
    select_analysis_data
)
import re
import csv, json
from analysis import top5, orders_per_day, client_connections

class DatetimeEncoder(json.JSONEncoder):
    """
    Класс, позволяющий сериализовывать объекты datetime в формате JSON.
    """
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

class AppController:
    """
    Контроллер приложения, ответственный за управление данными и координацию взаимодействия различных частей системы.
    """
    def __init__(self, main_app):
        """
        Инициализирует контроллер приложения и создаёт таблицы в базе данных.

        Parameters
        ----------
        main_app : object
            Главное приложение, в котором работает контроллер.
        """
        self.main_app = main_app
        self.cart_items = []  # Временное хранилище корзины покупок
        create_tables()  # Создает таблицы в базе данных при инициализации контроллера

    def load_customers(self):
        """
        Загружает список всех клиентов из базы данных.

        Returns
        -------
        list
            Список объектов Customer.
        """
        return select_customers()

    def load_products(self):
        """
        Загружает список всех товаров из базы данных.

        Returns
        -------
        list
            Список объектов Product.
        """
        return select_products()

    def load_orders(self):
        """
        Загружает список всех заказов из базы данных.

        Returns
        -------
        list
            Список объектов Order.
        """
        return select_orders()

    def load_sort_orders(self, sort_params):
        """
        Загружает список заказов, отсортированный по заданным параметрам.

        Parameters
        ----------
        sort_params : dict
            Словарь с параметрами сортировки (ключ 'heading' определяет столбец сортировки, ключ '<column>' —
            направление сортировки ('asc' или 'desc')).

        Returns
        -------
        list
            Список объектов Order, отсортированный по заданным критериям.
        """
        orders = select_orders()
        column = sort_params.get("heading", "id")
        direction = sort_params.get(column, "asc")
        if column == "id":
            orders.sort(key=lambda x: x.id, reverse=(direction == "desc"))
        elif column == "date":
            orders.sort(key=lambda x: x.date_created, reverse=(direction == "desc"))
        elif column == "amount":
            orders.sort(key=lambda x: x.total_amount, reverse=(direction == "desc"))
        return orders

    def search_customers(self, keyword):
        """
        Выполняет поиск клиентов по указанному ключевому слову.

        Parameters
        ----------
        keyword : str
            Ключевое слово для поиска (может соответствовать имени, email или телефону клиента).

        Returns
        -------
        list
            Список объектов Customer, удовлетворяющих условиям поиска.
        """
        customers = select_customers()
        normalized_keyword = keyword.lower()
        filtered_customers = []
        for customer in customers:
            if (
                normalized_keyword in str(customer.id).lower() or
                normalized_keyword in customer.name.lower() or
                normalized_keyword in customer.email.lower() or
                normalized_keyword in str(customer.phone).lower()
            ):
                filtered_customers.append(customer)
        return filtered_customers

    def search_products(self, keyword):
        """
        Выполняет поиск товаров по указанному ключевому слову.

        Parameters
        ----------
        keyword : str
            Ключевое слово для поиска (может соответствовать названию, цене или количеству товара).

        Returns
        -------
        list
            Список объектов Product, удовлетворяющих условиям поиска.
        """
        products = select_products()
        normalized_keyword = keyword.lower()
        filtered_products = []
        for product in products:
            if (
                normalized_keyword in str(product.id).lower() or
                normalized_keyword in product.name.lower() or
                normalized_keyword in str(product.price).lower() or
                normalized_keyword in str(product.quantity).lower()
            ):
                filtered_products.append(product)
        return filtered_products

    def search_orders(self, keyword):
        """
        Выполняет поиск заказов по указанному ключевому слову.

        Parameters
        ----------
        keyword : str
            Ключевое слово для поиска (может соответствовать номеру заказа, покупателю, дате создания, статусу или итоговой сумме).

        Returns
        -------
        list
            Список объектов Order, удовлетворяющих условиям поиска.
        """
        orders = select_orders()
        normalized_keyword = keyword.lower()
        filtered_orders = []
        for order in orders:
            customer = find_customer_by_id(order.customer_id)
            if customer:
                if (
                    normalized_keyword in str(order.id).lower() or
                    normalized_keyword in customer.name.lower() or
                    normalized_keyword in str(order.date_created).lower() or
                    normalized_keyword in order.status.lower() or
                    normalized_keyword in str(order.total_amount).lower()
                ):
                    filtered_orders.append(order)
        return filtered_orders

    def find_customer_by_id(self, customer_id):
        """
        Находит клиента по его идентификатору.

        Parameters
        ----------
        customer_id : int
            Идентификатор клиента.

        Returns
        -------
        Customer
            Объект Customer, соответствующий данному идентификатору.
        """
        return find_customer_by_id(customer_id)

    def find_product_by_id(self, product_id):
        """
        Находит товар по его идентификатору.

        Parameters
        ----------
        product_id : int
            Идентификатор товара.

        Returns
        -------
        Product
            Объект Product, соответствующий данному идентификатору.
        """
        return find_product_by_id(product_id)

    def find_order_by_id(self, order_id):
        """
        Находит заказ по его идентификатору.

        Parameters
        ----------
        order_id : int
            Идентификатор заказа.

        Returns
        -------
        Order
            Объект Order, соответствующий данному идентификатору.
        """
        return find_order_by_id(order_id)

    def find_order_list_by_id(self, order_id):
        """
        Находит состав заказа по его идентификатору.

        Parameters
        ----------
        order_id : int
            Идентификатор заказа.

        Returns
        -------
        list
            Список объектов OrderItem, составляющих указанный заказ.
        """
        return find_order_list_by_id(order_id)

    def export_data(self, filename, entity_name, format_type):
        """
        Экспорт данных в выбранный формат (CSV или JSON).

        Parameters
        ----------
        filename : str
            Имя файла для экспорта.
        entity_name : str
            Название сущности (таблицы), данные которой экспортируются.
        format_type : str
            Тип формата экспорта ('csv' или 'json').

        Returns
        -------
        bool
            Результат операции (успех или ошибка).
        str
            Сообщение об ошибке (при неуспешном выполнении).
        """
        try:
            if entity_name == 'orders-details':
                raw_data = select_all_orders_with_items()
            else:
                raw_data = select_data(entity_name)

            if format_type.lower() == 'csv':
                with open(filename, mode='w', newline='', encoding='utf-8-sig') as file:
                    if isinstance(raw_data, list) and raw_data and isinstance(raw_data[0], dict):
                        writer = csv.DictWriter(file, fieldnames=raw_data[0].keys())
                        writer.writeheader()
                        writer.writerows(raw_data)
                    else:
                        writer = csv.writer(file)
                        writer.writerow([
                            'order_id', 'customer_id', 'date_created', 'status', 'total_amount', 'product_id', 'quantity'
                        ])
                        for order in raw_data:
                            for item in order['items']:
                                writer.writerow([
                                    order['id'], order['customer_id'], order['date_created'], order['status'],
                                    order['total_amount'], item['product_id'], item['quantity']
                                ])
            elif format_type.lower() == 'json':
                with open(filename, mode='w', encoding='utf-8') as file:
                    json.dump(raw_data, file, cls=DatetimeEncoder, ensure_ascii=False, indent=4)
            else:
                raise ValueError("Формат экспорта не поддерживается.")
            return True, None
        except Exception as e:
            return False, str(e)

    def import_data(self, filename, entity_name, format_type):
        """
        Импортирует данные из файла (CSV или JSON) в базу данных.

        Parameters
        ----------
        filename : str
            Имя файла для импорта.
        entity_name : str
            Название сущности (таблицы), в которую импортируются данные.
        format_type : str
            Тип формата импорта ('csv' или 'json').

        Returns
        -------
        bool
            Результат операции (успех или ошибка).
        str
            Сообщение об ошибке (при неуспешном выполнении).
        """
        try:
            if entity_name == 'orders-details':
                truncate_table('orders')
                truncate_table('order_items')
            else:
                truncate_table(entity_name)

            if format_type.lower() == 'csv':
                with open(filename, mode='r', newline='', encoding='utf-8-sig') as file:
                    reader = csv.reader(file)
                    header = next(reader)  # Пропускаем заголовочную строку
                    if entity_name == 'orders-details':
                        all_data = []
                        for row in reader:
                            order_id, customer_id, date_created, status, total_amount, items_json = row
                            parsed_date = datetime.strptime(date_created, '%Y-%m-%d %H:%M:%S')
                            fixed_items_json = items_json.replace("'", '"')
                            items = json.loads(fixed_items_json)
                            order_data = [{
                                'id': order_id,
                                'customer_id': customer_id,
                                'date_created': parsed_date,
                                'status': status,
                                'total_amount': total_amount
                            }]
                            item_data = [{
                                'order_id': order_id,
                                'product_id': item['product_id'],
                                'quantity': item['quantity']
                            } for item in items]
                            all_data.extend(order_data)
                            all_data.extend(item_data)
                        bulk_insert_data('orders', [d for d in all_data if 'order_id' not in d])
                        bulk_insert_data('order_items', [d for d in all_data if 'order_id' in d])
                    else:
                        data = [{key: val for key, val in zip(header, row)} for row in reader]
                        bulk_insert_data(entity_name, data)
            elif format_type.lower() == 'json':
                with open(filename, mode='r', encoding='utf-8') as file:
                    data = json.load(file)
                    if entity_name == 'orders-details':
                        all_data = []
                        for entry in data:
                            parsed_date = datetime.fromisoformat(entry['date_created'])
                            order_data = [{
                                'id': entry['id'],
                                'customer_id': entry['customer_id'],
                                'date_created': parsed_date,
                                'status': entry['status'],
                                'total_amount': entry['total_amount']
                            }]
                            item_data = [{
                                'order_id': entry['id'],
                                'product_id': item['product_id'],
                                'quantity': item['quantity']
                            } for item in entry['items']]
                            all_data.extend(order_data)
                            all_data.extend(item_data)
                        bulk_insert_data('orders', [d for d in all_data if 'order_id' not in d])
                        bulk_insert_data('order_items', [d for d in all_data if 'order_id' in d])
                    else:
                        bulk_insert_data(entity_name, data)
            else:
                raise ValueError("Формат импорта не поддерживается.")
            return True, None
        except Exception as e:
            return False, str(e)

    def export_orders(self, filename, format_type):
        """
        Экспортирует данные заказов с детальным списком товаров в указанный формат.

        Parameters
        ----------
        filename : str
            Имя файла для экспорта.
        format_type : str
            Тип формата экспорта ('csv' или 'json').

        Returns
        -------
        bool
            Результат операции (успех или ошибка).
        str
            Сообщение об ошибке (при неуспешном выполнении).
        """
        try:
            raw_data = select_all_orders_with_items()
            if format_type.lower() == 'csv':
                with open(filename, mode='w', newline='', encoding='utf-8-sig') as file:
                    writer = csv.writer(file)
                    writer.writerow([
                        'order_id', 'customer_id', 'date_created', 'status', 'total_amount', 'product_id', 'quantity'
                    ])
                    for order in raw_data:
                        for item in order['items']:
                            writer.writerow([
                                order['id'], order['customer_id'], order['date_created'], order['status'],
                                order['total_amount'], item['product_id'], item['quantity']
                            ])
            elif format_type.lower() == 'json':
                with open(filename, mode='w', encoding='utf-8') as file:
                    processed_data = []
                    for order in raw_data:
                        processed_data.append({
                            'order_id': order['id'],
                            'customer_id': order['customer_id'],
                            'date_created': order['date_created'].strftime('%Y-%m-%d %H:%M:%S'),
                            'status': order['status'],
                            'total_amount': order['total_amount'],
                            'items': [
                                {'product_id': item['product_id'], 'quantity': item['quantity']} for item in
                                order['items']
                            ]
                        })
                    json.dump(processed_data, file, ensure_ascii=False, indent=4)
            else:
                raise ValueError("Формат экспорта не поддерживается.")
            return True, None
        except Exception as e:
            return False, str(e)

    def add_customer(self, data):
        """
        Добавляет нового клиента в систему с предварительной проверкой данных.

        Parameters
        ----------
        data : dict
            Словарь с полями ('name', 'email', 'phone').

        Returns
        -------
        tuple
            (bool, str) - True, если операция прошла успешно, иначе False и соответствующее сообщение об ошибке.
        """
        errors = []
        if not data.get('name', '').strip():
            errors.append("Имя обязательно для заполнения.")
        email = data.get('email')
        phone = data.get('phone')
        if email:
            try:
                self.validate_email(email)
            except ValueError as ve:
                errors.append(str(ve))
        if phone:
            try:
                self.validate_phone(phone)
            except ValueError as vp:
                errors.append(str(vp))
        if errors:
            return False, "\n".join(errors)
        try:
            insert_customer(Customer(**data))
            return True, ""
        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                return False, "Данный адрес электронной почты уже занят."
            else:
                return False, f"Возникла непредвиденная ошибка: {str(e)}"

    def edit_customer(self, customer_id, data):
        """
        Редактирует данные клиента с предварительной проверкой данных.

        Parameters
        ----------
        customer_id : int
            Уникальный идентификатор клиента.
        data : dict
            Словарь с полями ('name', 'email', 'phone').

        Returns
        -------
        tuple
            (bool, str) - True, если операция прошла успешно, иначе False и соответствующее сообщение об ошибке.
        """
        errors = []
        if not data.get('name', '').strip():
            errors.append("Имя обязательно для заполнения.")
        email = data.get('email')
        phone = data.get('phone')
        if email:
            try:
                self.validate_email(email)
            except ValueError as ve:
                errors.append(str(ve))
        if phone:
            try:
                self.validate_phone(phone)
            except ValueError as vp:
                errors.append(str(vp))
        if errors:
            return False, "\n".join(errors)
        try:
            update_customer(Customer(id=customer_id, **data))
            return True, ""
        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                return False, "Данный адрес электронной почты уже занят."
            else:
                return False, f"Возникла непредвиденная ошибка: {str(e)}"

    def delete_customer(self, customer_id):
        """
        Удаляет клиента по его идентификатору, предварительно проверяя наличие заказов.

        Parameters
        ----------
        customer_id : int
            Уникальный идентификатор клиента.

        Returns
        -------
        tuple
            (bool, str) - True, если операция прошла успешно, иначе False и соответствующее сообщение об ошибке.
        """
        related_orders = select_orders_by_customer_id(customer_id)
        if related_orders:
            customer = find_customer_by_id(customer_id)
            error_message = f"У покупателя {customer.name} есть оформленные заказы. Удаление запрещено."
            return False, error_message
        else:
            delete_customer(customer_id)
            return True, None

    def find_product_id_by_name(self, name):
        """
                Ищет товар по его наименованию

                Parameters
                ----------
                name : str
                    Наименование товара

                Returns
                -------
                id : int
                    id товара с наименованием name
                """
        product = next((p for p in select_products() if p.name == name), None)
        return product.id if product else None

    def add_product(self, data):
        """
        Добавляет новый товар в систему с предварительной проверкой данных.

        Parameters
        ----------
        data : dict
            Словарь с полями ('name', 'price', 'quantity').

        Returns
        -------
        tuple
            (bool, str) - True, если операция прошла успешно, иначе False и соответствующее сообщение об ошибке.
        """
        errors = []
        if not data.get('name', '').strip():
            errors.append("Название товара обязательно для заполнения.")
        price = data.get('price')
        quantity = data.get('quantity')
        try:
            price = float(price)
            if price <= 0:
                errors.append("Цена должна быть положительной.")
        except ValueError:
            errors.append("Цена должна быть числом.")
        try:
            quantity = int(quantity)
            if quantity < 0:
                errors.append("Количество не может быть отрицательным.")
        except ValueError:
            errors.append("Количество должно быть целым числом.")
        if errors:
            return False, "\n".join(errors)
        try:
            insert_product(Product(**data))
            return True, ""
        except Exception as e:
            return False, f"Возникла непредвиденная ошибка: {str(e)}"

    def edit_product(self, product_id, data):
        """
        Редактирует данные товара с предварительной проверкой данных.

        Parameters
        ----------
        product_id : int
            Уникальный идентификатор товара.
        data : dict
            Словарь с полями ('name', 'price', 'quantity').

        Returns
        -------
        tuple
            (bool, str) - True, если операция прошла успешно, иначе False и соответствующее сообщение об ошибке.
        """
        errors = []
        if not data.get('name', '').strip():
            errors.append("Название товара обязательно для заполнения.")
        price = data.get('price')
        quantity = data.get('quantity')
        try:
            price = float(price)
            if price <= 0:
                errors.append("Цена должна быть положительной.")
        except ValueError:
            errors.append("Цена должна быть числом.")
        try:
            quantity = int(quantity)
            if quantity < 0:
                errors.append("Количество не может быть отрицательным.")
        except ValueError:
            errors.append("Количество должно быть целым числом.")
        if errors:
            return False, "\n".join(errors)
        try:
            update_product(Product(id=product_id, **data))
            return True, ""
        except Exception as e:
            return False, f"Возникла непредвиденная ошибка: {str(e)}"

    def delete_product(self, product_id):
        """
        Удаляет товар по его идентификатору, предварительно проверяя наличие заказов.

        Parameters
        ----------
        product_id : int
            Уникальный идентификатор товара.

        Returns
        -------
        tuple
            (bool, str) - True, если операция прошла успешно, иначе False и соответствующее сообщение об ошибке.
        """
        related_items = select_orders_by_product_id(product_id)
        if related_items:
            product = find_product_by_id(product_id)
            error_message = f"Товар {product.name} состоит в оформленном заказе. Удаление запрещено."
            return False, error_message
        else:
            delete_product(product_id)
            return True, None

    def add_order_item(self, order_id, item_dict):
        """
        Добавляет позицию заказа в базу данных.

        Parameters
        ----------
        order_id : int
            Идентификатор заказа.
        item_dict : dict
            Словарь с полями 'product_id' и 'quantity'.
        """
        order_item = OrderItem(product_id=item_dict["product_id"], quantity=item_dict["quantity"])
        insert_order_item(order_id, order_item)

    def calculate_total(self, cart_items):
        """
        Рассчитывает общую сумму заказа.

        Parameters
        ----------
        cart_items : list
            Список товаров в корзине с указанием количества.

        Returns
        -------
        float
            Общая сумма заказа.
        """
        t_sum = 0
        for i in cart_items:
            price = find_product_by_id(i["product_id"]).price
            t_sum += price * i["quantity"]
        return t_sum

    def process_checkout(self, cart_items, customer_id):
        """
        Оформляет заказ и уменьшает количество товара на складе.

        Parameters
        ----------
        cart_items : list
            Список товаров в корзине с указанием количества.
        customer_id : int
            Идентификатор покупателя.

        Returns
        -------
        tuple
            (bool, str) - True, если заказ успешно оформлен, иначе False и соответствующее сообщение об ошибке.
        """
        if not cart_items:
            return False, "Нет товаров в корзине!"
        zero_items = [item for item in cart_items if item["quantity"] == 0]
        if zero_items:
            return False, "Некоторые товары имеют нулевое количество, оформление заказа отменено."
        order = Order(
            customer_id=customer_id,
            total_amount=self.calculate_total(cart_items),
            status="Новый",
            date_created=datetime.now()
        )
        order_id = insert_order(order)
        for item in cart_items:
            order_item = OrderItem(
                product_id=item["product_id"],
                quantity=item["quantity"]
            )
            insert_order_item(order_id, order_item)
            product = find_product_by_id(item["product_id"])
            if product:
                product.quantity -= item["quantity"]
                update_product(product)
        self.cart_items.clear()  # Очищаем корзину после оформления заказа
        return True, "Заказ успешно оформлен!"

    def update_order(self, order_id, updates):
        """
        Обновляет данные заказа.

        Parameters
        ----------
        order_id : int
            Идентификатор заказа.
        updates : dict
            Словарь с новыми значениями полей заказа.

        Returns
        -------
        tuple
            (bool, str) - True, если обновление прошло успешно, иначе False и соответствующее сообщение об ошибке.
        """
        original_order = find_order_by_id(order_id)
        if original_order:
            if "total_amount" in updates:
                updates["date_created"] = datetime.now()
            success = update_order(order_id, updates)
            return True, ""
        else:
            return False, "Заказ не найден."

    def delete_order(self, order_id):
        """
        Удаляет заказ по его идентификатору.

        Parameters
        ----------
        order_id : int
            Идентификатор заказа.
        """
        delete_order(order_id)
        self.load_orders()

    def delete_order_list(self, order_id):
        """
        Удаляет содержимое заказа по его идентификатору.

        Parameters
        ----------
        order_id : int
            Идентификатор заказа.
        """
        delete_order_list(order_id)
        self.load_orders()

    def validate_email(self, email):
        """
        Проверяет корректность email.

        Raises
        ------
        ValueError
            Если email некорректен.
        """
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, email):
            raise ValueError(f"Некорректный формат email: {email}")

    def validate_phone(self, phone):
        """
        Проверяет корректность номера телефона.

        Raises
        ------
        ValueError
            Если номер телефона некорректен.
        """
        pattern = r"^\+7\d{10}$|^\d{11}$"
        if not re.match(pattern, phone):
            raise ValueError(f"Некорректный формат телефона: {phone}")

    def fetch_top5_customers(self):
        """
        Получает данные для построения графика "Топ-5 клиентов по заказам".

        Returns
        -------
        list
            Список кортежей с данными для построения графика.
        """
        res_ord, col_ord = select_analysis_data('orders')
        res_cust, col_cust = select_analysis_data('customers')
        res = [(res_cust, col_cust), (res_ord, col_ord)]
        return res

    def fetch_orders_per_day(self):
        """
        Получает данные для построения графика "Динамика количества заказов по датам".

        Returns
        -------
        tuple
            Кортеж с данными для построения графика.
        """
        res_ord, col_ord = select_analysis_data('orders')
        res = (res_ord, col_ord)
        return res

    def fetch_client_connections(self):
        """
        Получает данные для построения графа "Связь покупателей по общим товарам".

        Returns
        -------
        list
            Список кортежей с данными для построения графа.
        """
        res_cust, col_cust = select_analysis_data('customers')
        res_prod, col_prod = select_analysis_data('products')
        res_ord, col_ord = select_analysis_data('orders')
        res_ord_it, col_ord_it = select_analysis_data('order_items')
        res = [(res_cust, col_cust), (res_prod, col_prod), (res_ord, col_ord), (res_ord_it, col_ord_it)]
        return res

    def c_top5(self, res):
        """
        Передаёт данные в анализатор для построения графика "Топ-5 клиентов по заказам".

        Parameters
        ----------
        res : list
            Список кортежей с данными для анализа.

        Returns
        -------
        pd.DataFrame
            Датафрейм с результатом анализа.
        """
        return top5(res)

    def c_orders_per_day(self, res):
        """
        Передаёт данные в анализатор для построения графика "Динамика количества заказов по датам".

        Parameters
        ----------
        res : tuple
            Кортеж с данными для анализа.

        Returns
        -------
        pd.DataFrame
            Датафрейм с результатом анализа.
        """
        return orders_per_day(res)

    def c_client_connections(self, res):
        """
        Передаёт данные в анализатор для построения графа "Связь покупателей по общим товарам".

        Parameters
        ----------
        res : list
            Список кортежей с данными для анализа.

        Returns
        -------
        list
            Список рёбер графа с результатами анализа.
        """
        return client_connections(res)