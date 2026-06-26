"""Example extraction targets.

These double as documentation: a schema *is* the contract for what gets pulled out of
the text. Constraints (enums, types, descriptions) steer the model — descriptions become
part of the structured-output schema the provider enforces, so write them for the model,
not just for humans.

Bring your own schema by defining any `pydantic.BaseModel` and passing it to `Extractor`.
The registry below just wires a few up for the CLI's `--schema` flag.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class Sentiment(StrEnum):
    positive = "positive"
    neutral = "neutral"
    negative = "negative"


class ContactInfo(BaseModel):
    """A person's contact details extracted from an email, signature, or bio."""

    name: str = Field(description="Full name of the person.")
    email: str | None = Field(default=None, description="Email address, if present.")
    phone: str | None = Field(default=None, description="Phone number, if present.")
    company: str | None = Field(default=None, description="Employer or organization.")
    title: str | None = Field(default=None, description="Job title or role.")


class LineItem(BaseModel):
    description: str = Field(description="What the line item is for.")
    quantity: float = Field(description="Quantity billed.")
    unit_price: float = Field(description="Price per unit, in the invoice currency.")


class Invoice(BaseModel):
    """Structured view of a free-text or scanned invoice."""

    invoice_number: str | None = Field(default=None, description="Invoice identifier.")
    vendor: str | None = Field(default=None, description="Who issued the invoice.")
    currency: str | None = Field(default=None, description="ISO currency code, e.g. USD.")
    total: float | None = Field(default=None, description="Grand total amount due.")
    line_items: list[LineItem] = Field(default_factory=list, description="Itemized charges.")


class Feedback(BaseModel):
    """Customer feedback distilled into structured, analyzable fields."""

    summary: str = Field(description="One-sentence summary of the feedback.")
    sentiment: Sentiment = Field(description="Overall sentiment.")
    topics: list[str] = Field(default_factory=list, description="Themes mentioned.")
    action_required: bool = Field(description="Whether the feedback needs follow-up.")


# Wires schema names (used by the CLI / API) to their classes.
SCHEMA_REGISTRY: dict[str, type[BaseModel]] = {
    "contact": ContactInfo,
    "invoice": Invoice,
    "feedback": Feedback,
}
