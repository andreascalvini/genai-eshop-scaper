"""Product data models."""

from pydantic import BaseModel, Field
from typing import Optional, List
from decimal import Decimal


class ProductVariant(BaseModel):
    """Product variant with size and price information."""

    size: str
    color: Optional[str] = None
    sku: Optional[str] = None
    price: Decimal
    original_price: Optional[Decimal] = None
    in_stock: bool = True
    quantity_available: Optional[int] = None


class Product(BaseModel):
    """Complete product information."""

    product_code: str = Field(..., description="Unique product identifier/SKU")
    name: str = Field(..., description="Product name/title")
    description: Optional[str] = Field(None, description="Product description")
    brand: Optional[str] = None
    category: Optional[str] = None
    variants: List[ProductVariant] = Field(default_factory=list)
    base_price: Decimal
    images: List[str] = Field(default_factory=list)
    url: str = Field(..., description="Product page URL")
    source_domain: str = Field(..., description="Domain where product was found")
    metadata: dict = Field(default_factory=dict)

    class Config:
        """Config for model."""

        json_schema_extra = {
            "example": {
                "product_code": "SHIRT-001",
                "name": "Blue Cotton T-Shirt",
                "description": "High quality cotton t-shirt",
                "brand": "FashionBrand",
                "category": "Shirts",
                "variants": [
                    {
                        "size": "M",
                        "color": "Blue",
                        "sku": "SHIRT-001-M-BLU",
                        "price": "29.99",
                    }
                ],
                "base_price": "29.99",
                "url": "https://example.com/products/shirt-001",
                "source_domain": "example.com",
            }
        }
