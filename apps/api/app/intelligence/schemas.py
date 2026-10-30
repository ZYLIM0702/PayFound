from __future__ import annotations

from typing import Any

from pydantic import Field, model_validator

from ..llm import StrictModel


class AgentInput(StrictModel):
    message: str = Field(min_length=2, max_length=1000)
    latitude: float | None = Field(default=None, ge=-90, le=90, allow_inf_nan=False)
    longitude: float | None = Field(default=None, ge=-180, le=180, allow_inf_nan=False)
    radius_km: float | None = Field(default=None, gt=0, le=200, allow_inf_nan=False)
    merchant_id: str | None = Field(default=None, min_length=1, max_length=48)

    @model_validator(mode='after')
    def coordinates(self):
        if (self.latitude is None) != (self.longitude is None):
            raise ValueError('latitude and longitude must be supplied together')
        if self.radius_km is not None and self.latitude is None:
            raise ValueError('radius_km requires coordinates')
        return self


class SearchInput(StrictModel):
    terms: list[str] = Field(max_length=20)
    merchant_id: str | None = Field(default=None, max_length=48)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    radius_km: float | None = Field(default=None, gt=0, le=200)
    min_price_cents: int | None = Field(default=None, ge=0)
    max_price_cents: int | None = Field(default=None, ge=0)
    currency: str | None = Field(default=None, pattern=r'^[A-Z]{3}$')
    open_now: bool = False
    requested_quantity: int = Field(default=1, ge=1, le=100)
    limit: int = Field(default=5, ge=1, le=12)


class ProductDTO(StrictModel):
    id: str
    merchant_id: str
    name: str
    description: str
    category: str
    sku: str
    price_cents: int
    currency: str
    quantity: int | None
    available_quantity: int | None
    stock_updated_at: str | None
    image_emoji: str
    in_stock: bool
    active: bool
    freshness: str
    merchant_name: str
    merchant_slug: str
    merchant_address: str
    is_open: bool | None
    hours: str
    distance_km: float | None
    location_id: str | None
    source: str
    source_timestamps: dict[str, str | None]
    stock_status: str
    verified_local_stock: bool = False


class ProductList(StrictModel):
    products: list[ProductDTO] = Field(max_length=12)
    truncated: bool = False


class ProductReferences(StrictModel):
    product_ids: list[str] = Field(max_length=12)


class HoursFact(StrictModel):
    product_id: str
    merchant_id: str
    hours: str
    is_open: bool | None
    basis: str


class HoursOutput(StrictModel):
    stores: list[HoursFact] = Field(max_length=12)


class FreshnessFact(StrictModel):
    product_id: str
    freshness: str
    stock_updated_at: str | None
    verified_local_stock: bool = False


class FreshnessOutput(StrictModel):
    inventory: list[FreshnessFact] = Field(max_length=12)


class PickupOutput(StrictModel):
    product_ids: list[str] = Field(max_length=12)
    stock_confirmation_required: bool = True
    payment_confirmation_required: bool = True


class MerchantToolInput(StrictModel):
    merchant_id: str = Field(min_length=1, max_length=48)


class InventoryOutput(StrictModel):
    products: list[ProductDTO] = Field(max_length=12)
    count: int = Field(ge=0)


class NumericOutput(StrictModel):
    numeric_facts: dict[str, int]
    as_of: str


class ReportCreate(StrictModel):
    merchant_id: str = Field(min_length=1, max_length=48)
    name: str = Field(min_length=1, max_length=160)
    state: dict[str, Any]


class ReportUpdate(StrictModel):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    state: dict[str, Any] | None = None
    version: int | None = Field(default=None, ge=1)

    @model_validator(mode='after')
    def fields_present(self):
        if self.name is None and self.state is None:
            raise ValueError('name or state is required')
        return self


class ConsentInput(StrictModel):
    granted: bool
