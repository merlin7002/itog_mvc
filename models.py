from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime

@dataclass
class Customer:
    """
    Модель данных для представления клиента.

    Attributes
    ----------
    id : Optional[int]
        Уникальный идентификатор клиента.
    name : str
        Имя клиента.
    email : str
        Электронная почта клиента.
    phone : str
        Номер телефона клиента.
    """
    id: Optional[int] = None
    name: str = ""
    email: str = ""
    phone: str = ""

    @classmethod
    def from_tuple(cls, row):
        """
        Создает экземпляр класса `Customer` из кортежа данных.

        Parameters
        ----------
        row : tuple
            Кортеж данных из базы данных, содержащий информацию о клиенте.

        Returns
        -------
        Customer
            Экземпляр класса `Customer`, созданный на основе предоставленных данных.
        """
        return cls(id=row[0], name=row[1], email=row[2], phone=row[3])

@dataclass
class Product:
    """
    Модель данных для представления товара.

    Attributes
    ----------
    id : Optional[int]
        Уникальный идентификатор товара.
    name : str
        Название товара.
    price : float
        Цена товара.
    quantity : int
        Доступное количество товара.
    """
    id: Optional[int] = None
    name: str = ""
    price: float = 0.0
    quantity: int = 0

    @classmethod
    def from_tuple(cls, row):
        """
        Создает экземпляр класса `Product` из кортежа данных.

        Parameters
        ----------
        row : tuple
            Кортеж данных из базы данных, содержащий информацию о товаре.

        Returns
        -------
        Product
            Экземпляр класса `Product`, созданный на основе предоставленных данных.
        """
        return cls(id=row[0], name=row[1], price=row[2], quantity=row[3])

@dataclass
class OrderItem:
    """
    Представляет позицию в заказе (продукт и его количество).

    Attributes
    ----------
    product_id : int
        Идентификатор товара.
    quantity : int
        Количество товара в позиции заказа.
    """
    product_id: int
    quantity: int

@dataclass
class Order:
    """
    Модель данных для представления заказа.

    Attributes
    ----------
    id : Optional[int]
        Уникальный идентификатор заказа.
    customer_id : Optional[int]
        Идентификатор клиента, сделавшего заказ.
    items : List[OrderItem]
        Список позиций заказа (товаров и их количества).
    date_created : datetime
        Дата создания заказа.
    status : str
        Текущий статус заказа.
    total_amount : float
        Общая сумма заказа.
    """
    id: Optional[int] = None
    customer_id: Optional[int] = None
    items: List[OrderItem] = field(default_factory=list)
    date_created: datetime = datetime.now()
    status: str = "Новый"
    total_amount: float = 0.0

    @classmethod
    def from_tuple(cls, row):
        """
        Создает экземпляр класса `Order` из кортежа данных.

        Parameters
        ----------
        row : tuple
            Кортеж данных из базы данных, содержащий информацию о заказе.

        Returns
        -------
        Order
            Экземпляр класса `Order`, созданный на основе предоставленных данных.
        """
        # Обрезаем строку времени, чтобы убрать микросекунды
        cleaned_time = row[2].split('.')[0]
        dt = datetime.strptime(cleaned_time, '%Y-%m-%d %H:%M:%S')
        return cls(id=row[0], customer_id=row[1], date_created=dt, status=row[3], total_amount=row[4])