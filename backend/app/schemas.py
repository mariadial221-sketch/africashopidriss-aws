from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Category = Literal["vetements", "artisanat", "cosmetiques", "epicerie", "maison"]
CATEGORIES = ["vetements", "artisanat", "cosmetiques", "epicerie", "maison"]


class VendorIn(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    country: str = Field(pattern=r"^[A-Z]{2}$")
    city: str = ""


class VendorOut(VendorIn):
    model_config = ConfigDict(from_attributes=True)
    id: str


class ProductIn(BaseModel):
    vendor_id: str
    name: str = Field(min_length=2, max_length=160)
    description: str = Field(default="", max_length=4000)
    category: Category
    price_xof: int = Field(gt=0, le=50_000_000)
    stock: int = Field(ge=0, le=100_000)
    image_key: str = Field(default="", max_length=255)


class ProductOut(BaseModel):
    id: str
    vendor_id: str
    vendor_name: str
    vendor_country: str
    name: str
    description: str
    category: str
    price_xof: int
    stock: int
    image_url: str


class ProductPage(BaseModel):
    items: list[ProductOut]
    total: int
    page: int
    size: int


class PresignIn(BaseModel):
    filename: str = Field(min_length=1, max_length=120)
    content_type: Literal["image/jpeg", "image/png", "image/webp"]


class PresignOut(BaseModel):
    upload_url: str
    method: str
    headers: dict[str, str]
    key: str
    public_url: str


class OrderLineIn(BaseModel):
    product_id: str
    quantity: int = Field(gt=0, le=50)


class OrderIn(BaseModel):
    customer_email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", max_length=160)
    customer_country: str = Field(pattern=r"^[A-Z]{2}$")
    payment_method: Literal["card", "mobile_money"]
    lines: list[OrderLineIn] = Field(min_length=1, max_length=30)


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    status: str
    total_xof: int
    payment_method: str
    created_at: datetime


class PaymentWebhookIn(BaseModel):
    """Notification d'un PSP (agrégateur Mobile Money / carte).
    AfricaShop ne voit JAMAIS de numéro de carte : périmètre PCI DSS réduit (SAQ A)."""
    order_id: str
    psp_reference: str = Field(max_length=64)
    status: Literal["SUCCEEDED", "FAILED"]
