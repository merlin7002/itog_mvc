from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime

@dataclass
class Customer:
    id: Optional[int] = None
    name: str = ""
    email: str = ""
    phone: str = ""

    @classmethod
    def from_tuple(cls, row):
        return cls(id=row[0], name=row[1], email=row[2], phone=row[3])

@dataclass
class Product:
    id: Optional[int] = None
    name: str = ""
    price: float = 0.0
    quantity: int = 0

    @classmethod
    def from_tuple(cls, row):
        return cls(id=row[0], name=row[1], price=row[2], quantity=row[3])

@dataclass
class OrderItem:
    product_id: int
    quantity: int

@dataclass
class Order:
    id: Optional[int] = None
    customer_id: Optional[int] = None
    items: List[OrderItem] = field(default_factory=list)
    date_created: datetime = datetime.now()
    status: str = "Новый"
    total_amount: float = 0.0

    @classmethod
    def from_tuple(cls, row):
        """
                Конвертирует кортеж из результата запроса в объект Order.
                """
        # Обрезаем строку времени, чтобы убрать микросекунды
        cleaned_time = row[2].split('.')[0]
        dt = datetime.strptime(cleaned_time, '%Y-%m-%d %H:%M:%S')
        return cls(id=row[0], customer_id=row[1], date_created=dt, status=row[3], total_amount=row[4])