from tkinter import messagebox
from models import Customer, Product, Order, OrderItem
from datetime import datetime
from db import (
    insert_customer, select_customers, delete_customer, update_customer,
    insert_product, select_products, delete_product, update_product,
    insert_order, select_orders, delete_order, delete_order_list, insert_order_item,
    find_customer_by_id, find_product_by_id, find_order_by_id, find_order_list_by_id,
    select_orders_by_customer_id, select_orders_by_product_id, update_order,
    select_data, truncate_table, bulk_insert_data, create_tables, select_all_orders_with_items
)
import re
import csv, json

class DatetimeEncoder(json.JSONEncoder):
    """
    Кастомный JSON-кодировщик, умеющий сериализировать объекты datetime.
    """
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

class AppController:
    def __init__(self, main_app):
        self.main_app = main_app
        self.cart_items = []  # Временное хранилище корзины покупок

    # Создаем таблицы в базе данных при инициализации контроллера
    create_tables()

    def load_customers(self):
        """
        Возвращает список всех клиентов в формате, пригодном для представления.
        """
        return select_customers()

    def load_products(self):
        """
        Возвращает список всех товаров в формате, пригодном для представления.
        """
        return select_products()

    def load_orders(self):
        """
        Возвращает список всех товаров в формате, пригодном для представления.
        """
        return select_orders()

    def load_sort_orders(self, sort_params):
        """
        Возвращает список заказов, отсортированных по параметрам.
        """
        # Получаем полный список заказов
        orders = select_orders()
        # Определяем столбец и направление сортировки
        column = sort_params.get("heading", "id")
        direction = sort_params.get(column, "asc")
        # Производим сортировку
        if column == "id":
            orders.sort(key=lambda x: x.id, reverse=(direction == "desc"))
        elif column == "date":
            orders.sort(key=lambda x: x.date_created, reverse=(direction == "desc"))
        elif column == "amount":
            orders.sort(key=lambda x: x.total_amount, reverse=(direction == "desc"))
        return orders

    def search_customers(self, keyword):
        """
        Осуществляет поиск клиентов по указанным ключевым словам.
        """
        # Получаем список всех клиентов
        customers = select_customers()

        # Нормализуем поисковый запрос (преобразуем в нижний регистр)
        normalized_keyword = keyword.lower()

        # Фильтруем клиентов по ключевым словам
        filtered_customers = []
        for customer in customers:
            # Проверяем все поля клиента на наличие подстроки
            if (
                    normalized_keyword in str(customer.id).lower()  # ID клиента
                    or normalized_keyword in customer.name.lower()  # Имя клиента
                    or normalized_keyword in customer.email.lower()  # Email клиента
                    or normalized_keyword in str(customer.phone).lower()  # Телефон клиента
            ):
                filtered_customers.append(customer)

        return filtered_customers

    def search_products(self, keyword):
        """
        Осуществляет поиск товаров по указанным ключевым словам.
        """
        # Получаем список всех товаров
        products = select_products()

        # Нормализуем поисковый запрос (преобразуем в нижний регистр)
        normalized_keyword = keyword.lower()

        # Фильтруем товары по ключевым словам
        filtered_products = []
        for product in products:
            # Проверяем все поля товара на наличие подстроки
            if (
                    normalized_keyword in str(product.id).lower()  # ID товара
                    or normalized_keyword in product.name.lower()  # Название товара
                    or normalized_keyword in str(product.price).lower()  # Цена товара
                    or normalized_keyword in str(product.quantity).lower()  # Количество товара
            ):
                filtered_products.append(product)
        return filtered_products

    def search_orders(self, keyword):
        """
        Осуществляет поиск заказов по указанным ключевым словам.
        Поиск ведется по всем полям заказа, включая имя покупателя (customer.name).
        """
        orders = select_orders()
        normalized_keyword = keyword.lower()
        filtered_orders = []
        for order in orders:
            # Найти покупателя по идентификатору заказа
            customer = find_customer_by_id(order.customer_id)
            if customer:
                # Проверяем все поля заказа на наличие подстроки
                if (
                        normalized_keyword in str(order.id).lower() or  # ID заказа
                        normalized_keyword in customer.name.lower() or  # Имя покупателя
                        normalized_keyword in str(order.date_created).lower() or  # Дата создания
                        normalized_keyword in order.status.lower() or  # Статус заказа
                        normalized_keyword in str(order.total_amount).lower()  # Итоговая сумма
                ):
                    filtered_orders.append(order)
        return filtered_orders

    def find_customer_by_id(self, customer_id):
        """
        Находит клиента по его идентификатору.
        """
        return find_customer_by_id(customer_id)

    def find_product_by_id(self, product_id):
        """
        Находит товар по его идентификатору.
        """
        return find_product_by_id(product_id)

    def find_order_by_id(self, order_id):
        """
        Находит заказ по его идентификатору.
        """
        return find_order_by_id(order_id)

    def find_order_list_by_id(self, order_id):
        """
        Находит состав заказа по его идентификатору.
        """
        return find_order_list_by_id(order_id)

    # def export_data(self, filename, table_name, format_type):
    #     """
    #     Экспорт данных в выбранный формат (CSV или JSON).
    #     Возвращает True, если экспорт прошел успешно, иначе False.
    #     """
    #     try:
    #         raw_data = select_data(table_name)
    #
    #         if format_type.lower() == 'csv':
    #             with open(filename, mode='w', newline='', encoding='utf-8-sig') as file:
    #                 writer = csv.DictWriter(file, fieldnames=raw_data[0].keys())
    #                 writer.writeheader()
    #                 writer.writerows(raw_data)
    #         elif format_type.lower() == 'json':
    #             with open(filename, mode='w', encoding='utf-8') as file:
    #                 json.dump(raw_data, file, ensure_ascii=False, indent=4)
    #         else:
    #             raise ValueError("Формат экспорта не поддерживается.")
    #         return True, None
    #     except Exception as e:
    #         return False, str(e)
    def export_data(self, filename, entity_name, format_type):
        """
        Универсальный метод экспорта данных. Может экспортировать простую таблицу или объединённые данные (для заказов).
        """
        try:
            if entity_name == 'orders-details':
                # Специальный случай для экспорта заказов с детализацией
                raw_data = select_all_orders_with_items()
            else:
                # Обычные случаи экспорта таблиц (customers, products и др.)
                raw_data = select_data(entity_name)

            if format_type.lower() == 'csv':
                with open(filename, mode='w', newline='', encoding='utf-8-sig') as file:
                    if isinstance(raw_data, list) and raw_data and isinstance(raw_data[0], dict):
                        # Если это таблица (обычное поведение)
                        writer = csv.DictWriter(file, fieldnames=raw_data[0].keys())
                        writer.writeheader()
                        writer.writerows(raw_data)
                    else:
                        # Иначе считаем, что это сложная структура (например, заказы с детализацией)
                        writer = csv.writer(file)
                        writer.writerow(
                            ['order_id', 'customer_id', 'date_created', 'status', 'total_amount', 'product_id',
                             'quantity'])
                        for order in raw_data:
                            for item in order['items']:
                                writer.writerow([
                                    order['id'], order['customer_id'], order['date_created'], order['status'],
                                    order['total_amount'],
                                    item['product_id'], item['quantity']
                                ])
            elif format_type.lower() == 'json':
                with open(filename, mode='w', encoding='utf-8') as file:
                    # Используем кастомный JSON-кодировщик для обработки дат
                    json.dump(raw_data, file, cls=DatetimeEncoder, ensure_ascii=False, indent=4)
            else:
                raise ValueError("Формат экспорта не поддерживается.")
            return True, None
        except Exception as e:
            return False, str(e)

    def import_data(self, filename, entity_name, format_type):
        """
        Импортирует данные из файла (CSV или JSON) в базу данных.
        Возможность массовой вставки данных для tables (orders и order_items).
        """
        try:
            # Очистка таблиц заранее, чтобы избавиться от устаревших данных
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
                        # Специфичная структура для заказов с детализацией
                        all_data = []
                        for row in reader:
                            # Распаковка строки с шестью значениями
                            order_id, customer_id, date_created, status, total_amount, items_json = row
                            parsed_date = datetime.strptime(date_created, '%Y-%m-%d %H:%M:%S')
                            # Замена одинарных кавычек на двойные для корректного JSON
                            fixed_items_json = items_json.replace("'", '"')
                            # Разбираем JSON-представление позиций заказа
                            items = json.loads(fixed_items_json)

                            # Формируем записи для таблиц orders и order_items
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

                            # Добавляем записи для массового импорта
                            all_data.extend(order_data)
                            all_data.extend(item_data)

                        # Массовая вставка данных
                        bulk_insert_data('orders', [d for d in all_data if 'order_id' not in d])
                        bulk_insert_data('order_items', [d for d in all_data if 'order_id' in d])
                    else:
                        # Стандартный случай для простых таблиц
                        data = [{key: val for key, val in zip(header, row)} for row in reader]
                        bulk_insert_data(entity_name, data)
            elif format_type.lower() == 'json':
                with open(filename, mode='r', encoding='utf-8') as file:
                    data = json.load(file)
                    if entity_name == 'orders-details':
                        # Специфичная структура для заказов с детализацией
                        all_data = []
                        for entry in data:
                            # Преобразуем дату в объект datetime
                            parsed_date = datetime.fromisoformat(entry['date_created'])

                            # Формируем записи для таблиц orders и order_items
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

                            # Добавляем записи для массового импорта
                            all_data.extend(order_data)
                            all_data.extend(item_data)

                        # Массовая вставка данных
                        bulk_insert_data('orders', [d for d in all_data if 'order_id' not in d])
                        bulk_insert_data('order_items', [d for d in all_data if 'order_id' in d])
                    else:
                        # Стандартный случай для простых таблиц
                        bulk_insert_data(entity_name, data)
            else:
                raise ValueError("Формат импорта не поддерживается.")

            return True, None

        except Exception as e:
            return False, str(e)

    def export_orders(self, filename, format_type):
        """
        Экспортирует данные заказов с подробностями о позициях (таблица orders и order_items).
        """
        try:
            # Получаем сырые данные обо всех заказах с детализацией
            raw_data = select_all_orders_with_items()

            if format_type.lower() == 'csv':
                with open(filename, mode='w', newline='', encoding='utf-8-sig') as file:
                    writer = csv.writer(file)
                    # Шапка файла CSV
                    writer.writerow(
                        ['order_id', 'customer_id', 'date_created', 'status', 'total_amount', 'product_id', 'quantity'])
                    # Запись строк
                    for order in raw_data:
                        for item in order['items']:
                            writer.writerow([
                                order['id'], order['customer_id'], order['date_created'], order['status'],
                                order['total_amount'],
                                item['product_id'], item['quantity']
                            ])
            elif format_type.lower() == 'json':
                with open(filename, mode='w', encoding='utf-8') as file:
                    # Преобразуем данные в удобный формат JSON
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
        Добавляет нового клиента с предварительной проверкой и обработкой возможных ошибок.
        :param data: словарь с полями ('name', 'email', 'phone')
        """
        errors = []

        # Проверка наличия обязательных полей
        if not data.get('name', '').strip():
            errors.append("Имя обязательно для заполнения.")

        # Валидация адреса электронной почты и телефона
        email = data.get('email').strip()
        phone = data.get('phone').strip()
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

        # Проверка ошибок и вывод сообщений
        if errors:
            return False, "\n".join(errors)

        # Попытка вставки клиента
        try:
            insert_customer(Customer(**data))
            self.load_customers()
            return True, ""
        except Exception as e:
            # Обработка нарушения ограничения уникальности (например, дублирующий email)
            if "UNIQUE constraint failed" in str(e):
                return False, "Данный адрес электронной почты уже занят."
            else:
                return False, f"Возникла непредвиденная ошибка: {str(e)}"

    def edit_customer(self, customer_id, data):
        """
        Редактирует данные клиента с предварительной проверкой и обработкой возможных ошибок.
        :param customer_id: уникальный идентификатор клиента
        :param data: словарь с полями ('name', 'email', 'phone')
        """
        errors = []

        # Проверка наличия обязательных полей
        if not data.get('name', '').strip():
            errors.append("Имя обязательно для заполнения.")

        # Валидация адреса электронной почты и телефона
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

        # Проверка ошибок и вывод сообщений
        if errors:
            return False, "\n".join(errors)

        # Попытка обновить клиента
        try:
            update_customer(Customer(id=customer_id, **data))
            return True, ""
        except Exception as e:
            # Обработка нарушения ограничения уникальности (например, дублирующий email)
            if "UNIQUE constraint failed" in str(e):
                return False, "Данный адрес электронной почты уже занят."
            else:
                return False, f"Возникла непредвиденная ошибка: {str(e)}"

    def delete_customer(self, customer_id):
        """
        Удаляет клиента по его ID.
        """
        delete_customer(customer_id)

    def find_product_id_by_name(name):
        product = next((p for p in select_products() if p.name == name), None)
        return product.id if product else None

    def add_product(self, data):
        """
        Добавляет новый продукт с предварительной проверкой и обработкой возможных ошибок.
        :param data: словарь с полями ('name', 'price', 'quantity')
        """
        errors = []

        # Проверка наличия обязательных полей
        if not data.get('name', '').strip():
            errors.append("Название товара обязательно для заполнения.")

        # Проверка цены
        price = data.get('price')
        try:
            price = float(price)
            if price <= 0:
                errors.append("Цена должна быть положительной.")
        except ValueError:
            errors.append("Цена должна быть числом.")

        # Проверка количества
        quantity = data.get('quantity')
        try:
            quantity = int(quantity)
            if quantity < 0:
                errors.append("Количество не может быть отрицательным.")
        except ValueError:
            errors.append("Количество должно быть целым числом.")

        # Проверка ошибок и вывод сообщений
        if errors:
            return False, "\n".join(errors)

        # Попытка вставки продукта
        try:
            insert_product(Product(**data))
            return True, ""
        except Exception as e:
            return False, f"Возникла непредвиденная ошибка: {str(e)}"

    def edit_product(self, product_id, data):
        """
        Редактирует данные продукта.
        :param product_id: уникальный идентификатор продукта
        :param data: словарь с полями ('name', 'price', 'quantity')
        """
        errors = []

        # Проверка наличия обязательных полей
        if not data.get('name', '').strip():
            errors.append("Название товара обязательно для заполнения.")

        # Проверка цены
        price = data.get('price')
        try:
            price = float(price)
            if price <= 0:
                errors.append("Цена должна быть положительной.")
        except ValueError:
            errors.append("Цена должна быть числом.")

        # Проверка количества
        quantity = data.get('quantity')
        try:
            quantity = int(quantity)
            if quantity < 0:
                errors.append("Количество не может быть отрицательным.")
        except ValueError:
            errors.append("Количество должно быть целым числом.")

        # Проверка ошибок и вывод сообщений
        if errors:
            return False, "\n".join(errors)

        # Попытка обновить продукт
        try:
            update_product(Product(id=product_id, **data))
            return True, ""
        except Exception as e:
            return False, f"Возникла непредвиденная ошибка: {str(e)}"

    def delete_product(self, product_id):
        """
        Удаляет продукт по его ID.
        """
        delete_product(product_id)

    # def add_order(self, order_data):
    #     """
    #     Добавляет новый заказ и его позиции.
    #     """
    #     try:
    #         order = Order(**order_data)
    #         order_id = insert_order(order)
    #         for item in order_data["items"]:
    #             insert_order_item(order_id, OrderItem(**item))
    #     except Exception as e:
    #         messagebox.showerror("Ошибка", f"Возникла непредвиденная ошибка: {str(e)}")
    #
    # def add_to_cart(self, product_id, product_name, product_price):
    #     """Добавляет товар в корзину."""
    #     existing_item = next((item for item in self.cart_items if item["product_id"] == product_id), None)
    #     if existing_item:
    #         existing_item["quantity"] += 1
    #     else:
    #         self.cart_items.append(
    #             {"product_id": product_id, "name": product_name, "price": product_price, "quantity": 1})
    #
    # def change_quantity(self, product_id, new_quantity):
    #     """Меняет количество товара в корзине."""
    #     item = next((item for item in self.cart_items if item["product_id"] == product_id), None)
    #     if item:
    #         item["quantity"] = new_quantity
    #         if new_quantity == 0:
    #             self.cart_items.remove(item)

    def add_order_item(self, order_id, item_dict):
        """
        Добавляет позицию заказа в базу данных.
        :param order_id: идентификатор заказа
        :param item_dict: словарь с полями 'product_id' и 'quantity'
        """
        # Преобразуем словарь в объект OrderItem
        order_item = OrderItem(product_id=item_dict["product_id"], quantity=item_dict["quantity"])
        # Передаём объект в метод базы данных
        insert_order_item(order_id, order_item)

    def calculate_total(self, cart_items):
        """Рассчитывает общую сумму заказа."""
        t_sum = 0
        for i in cart_items:
            price = find_product_by_id(i["product_id"]).price
            t_sum += price * i["quantity"]
        return t_sum

    def process_checkout(self, cart_items, customer_id):
        """Оформляет заказ и уменьшает количество товара на складе."""
        # Проверка наличия товаров в корзине
        if not cart_items:
            return False, "Нет товаров в корзине!"

        # Проверка, что все товары имеют положительное количество
        zero_items = [item for item in cart_items if item["quantity"] == 0]
        if zero_items:
            return False, "Некоторые товары имеют нулевое количество, оформление заказа отменено."

        # Создаем заказ
        order = Order(
            customer_id=customer_id,
            total_amount=self.calculate_total(cart_items),
            status="Новый",
            date_created=datetime.now()
        )
        order_id = insert_order(order)

        # Создаем позиции заказа
        for item in cart_items:
            order_item = OrderItem(
                product_id=item["product_id"],
                quantity=item["quantity"]
            )
            insert_order_item(order_id, order_item)

            # Уменьшаем количество товара на складе
            product = find_product_by_id(item["product_id"])
            if product:
                product.quantity -= item["quantity"]
                update_product(product)

        self.cart_items.clear()  # Очищаем корзину после оформления заказа
        return True, "Заказ успешно оформлен!"

    # def calculate_total(self, cart_items):
    #     """Рассчитывает общую сумму заказа."""
    #     return sum(item["price"] * item["quantity"] for item in cart_items)

    def update_order(self, order_id, updates):
        """
        Обновляет данные заказа, изменяя дату и время только при изменении итоговой суммы.
        """
        # Получаем текущий заказ из базы данных
        original_order = find_order_by_id(order_id)
        if original_order:
            # Автоматически ставим текущую дату и время только при изменении total_amount
            if "total_amount" in updates:
                updates["date_created"] = datetime.now()

            # Сохраняем изменения в базе данных
            success = update_order(order_id, updates)  # Передаём только order_id и словарь обновлений
            return True, ""
        else:
            return False, "Заказ не найден."

    def delete_order(self, order_id):
        """
        Удаляет заказ по его ID.
        """
        delete_order(order_id)
        self.load_orders()

    def delete_order_list(self, order_id):
        """
        Удаляет содержимое заказ по ID заказа.
        """
        delete_order_list(order_id)
        self.load_orders()

    def validate_email(self, email):
        """
        Проверяет корректность email.
        """
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, email):
            raise ValueError(f"Некорректный формат email: {email}")

    def validate_phone(self, phone):
        """
        Проверяет корректность телефона.
        """
        pattern = r"^\+7\d{10}$|^\d{11}$"
        if not re.match(pattern, phone):
            raise ValueError(f"Некорректный формат телефона: {phone}")