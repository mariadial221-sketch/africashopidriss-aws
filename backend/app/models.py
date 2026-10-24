from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


def _uuid() -> str:
    return uuid4().hex


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Vendor(Base):
    __tablename__ = "vendors"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(120))
    country: Mapped[str] = mapped_column(String(2))  # ISO 3166-1 alpha-2 : SN, CI, ML, GH...
    city: Mapped[str] = mapped_column(String(80), default="")
    owner_sub: Mapped[str] = mapped_column(String(64), default="")  # "sub" Cognito du vendeur
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    products: Mapped[list["Product"]] = relationship(back_populates="vendor")


class Product(Base):
    __tablename__ = "products"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uuid)
    vendor_id: Mapped[str] = mapped_column(ForeignKey("vendors.id"), index=True)
    name: Mapped[str] = mapped_column(String(160))
    description: Mapped[str] = mapped_column(Text, default="")
    category: Mapped[str] = mapped_column(String(40), index=True)
    price_xof: Mapped[int] = mapped_column(Integer)  # FCFA en entiers : jamais de float pour l'argent
    stock: Mapped[int] = mapped_column(Integer, default=0)
    image_key: Mapped[str] = mapped_column(String(255), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    vendor: Mapped[Vendor] = relationship(back_populates="products")


class Order(Base):
    __tablename__ = "orders"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uuid)
    customer_email: Mapped[str] = mapped_column(String(160))
    customer_country: Mapped[str] = mapped_column(String(2))
    payment_method: Mapped[str] = mapped_column(String(20))  # card | mobile_money
    status: Mapped[str] = mapped_column(String(20), default="PENDING_PAYMENT", index=True)
    total_xof: Mapped[int] = mapped_column(Integer, default=0)
    psp_reference: Mapped[str] = mapped_column(String(64), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    lines: Mapped[list["OrderLine"]] = relationship(back_populates="order", cascade="all, delete-orphan")


class OrderLine(Base):
    __tablename__ = "order_lines"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[str] = mapped_column(ForeignKey("orders.id"), index=True)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column(Integer)
    unit_price_xof: Mapped[int] = mapped_column(Integer)
    order: Mapped[Order] = relationship(back_populates="lines")
