import datetime
from typing import Optional, List
from sqlalchemy import (
    String, Float, Integer, DateTime, Text, ForeignKey, JSON, Enum
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

def utc_now():
    return datetime.datetime.now(datetime.timezone.utc)

class Base(DeclarativeBase):
    pass

class Customer(Base):
    __tablename__ = "customers"

    customer_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    full_name: Mapped[str] = mapped_column(String(128), nullable=False)
    email: Mapped[str] = mapped_column(String(128), nullable=False)
    normal_avg_amount: Mapped[float] = mapped_column(Float, default=1000.0)
    normal_std_amount: Mapped[float] = mapped_column(Float, default=300.0)
    normal_merchants: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)
    normal_payment_hours: Mapped[Optional[List[int]]] = mapped_column(JSON, default=list) # e.g. [8, 22]
    account_age_days: Mapped[int] = mapped_column(Integer, default=365)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=utc_now)

    transactions: Mapped[List["Transaction"]] = relationship("Transaction", back_populates="customer")

class Merchant(Base):
    __tablename__ = "merchants"

    merchant_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    legal_name: Mapped[str] = mapped_column(String(128), nullable=False)
    brand_name: Mapped[str] = mapped_column(String(128), nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False) # e.g. Utility, E-Commerce, Logistics
    verified_domain: Mapped[str] = mapped_column(String(128), nullable=False)
    verified_payment_identifier: Mapped[str] = mapped_column(String(128), nullable=False)
    account_age_days: Mapped[int] = mapped_column(Integer, default=730)
    status: Mapped[str] = mapped_column(String(32), default="VERIFIED") # VERIFIED, SUSPENDED, UNDER_REVIEW

    recipients: Mapped[List["Recipient"]] = relationship("Recipient", back_populates="linked_merchant")

class Recipient(Base):
    __tablename__ = "recipients"

    recipient_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    display_name: Mapped[str] = mapped_column(String(128), nullable=False)
    verified_identity: Mapped[str] = mapped_column(String(128), nullable=False)
    linked_merchant_id: Mapped[Optional[str]] = mapped_column(String(64), ForeignKey("merchants.merchant_id"), nullable=True)
    account_age_days: Mapped[int] = mapped_column(Integer, default=30)
    status: Mapped[str] = mapped_column(String(32), default="ACTIVE") # ACTIVE, FLAGGED, NEW

    linked_merchant: Mapped[Optional["Merchant"]] = relationship("Merchant", back_populates="recipients")
    transactions: Mapped[List["Transaction"]] = relationship("Transaction", back_populates="recipient")

class Scenario(Base):
    __tablename__ = "scenarios"

    scenario_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    scenario_name: Mapped[str] = mapped_column(String(128), nullable=False)
    scenario_type: Mapped[str] = mapped_column(String(64), nullable=False) # e.g. ELECTRICITY_SCAM, LEGITIMATE_UNUSUAL
    legitimate_or_attack: Mapped[str] = mapped_column(String(32), nullable=False) # LEGITIMATE or ATTACK
    expected_action: Mapped[str] = mapped_column(String(32), nullable=False) # ALLOW, VERIFY, HOLD, BLOCK

    transactions: Mapped[List["Transaction"]] = relationship("Transaction", back_populates="scenario")

class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    customer_id: Mapped[str] = mapped_column(String(64), ForeignKey("customers.customer_id"), nullable=False)
    merchant_id: Mapped[Optional[str]] = mapped_column(String(64), ForeignKey("merchants.merchant_id"), nullable=True)
    recipient_id: Mapped[str] = mapped_column(String(64), ForeignKey("recipients.recipient_id"), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(8), default="INR")
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime, default=utc_now)
    channel: Mapped[str] = mapped_column(String(32), default="UPI") # UPI, NET_BANKING, CARD
    status: Mapped[str] = mapped_column(String(32), default="SUCCESS") # SUCCESS, VERIFY_REQUIRED, HELD, BLOCKED
    scenario_id: Mapped[Optional[str]] = mapped_column(String(64), ForeignKey("scenarios.scenario_id"), nullable=True)

    customer: Mapped["Customer"] = relationship("Customer", back_populates="transactions")
    recipient: Mapped["Recipient"] = relationship("Recipient", back_populates="transactions")
    scenario: Mapped[Optional["Scenario"]] = relationship("Scenario", back_populates="transactions")
    payment_request: Mapped[Optional["PaymentRequest"]] = relationship("PaymentRequest", back_populates="transaction", uselist=False)
    protection_events: Mapped[List["ProtectionEvent"]] = relationship("ProtectionEvent", back_populates="transaction")

class PaymentRequest(Base):
    __tablename__ = "payment_requests"

    request_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    transaction_id: Mapped[str] = mapped_column(String(64), ForeignKey("transactions.transaction_id"), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    claimed_merchant: Mapped[str] = mapped_column(String(128), nullable=False)
    url: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    source_channel: Mapped[str] = mapped_column(String(32), default="SMS") # SMS, WHATSAPP, IN_APP
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime, default=utc_now)

    transaction: Mapped["Transaction"] = relationship("Transaction", back_populates="payment_request")

class ProtectionEvent(Base):
    __tablename__ = "protection_events"

    event_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    transaction_id: Mapped[str] = mapped_column(String(64), ForeignKey("transactions.transaction_id"), nullable=False)
    action: Mapped[str] = mapped_column(String(32), nullable=False) # ALLOW, VERIFY, HOLD, BLOCK
    evidence: Mapped[dict] = mapped_column(JSON, nullable=False) # Feature scores, mismatch details
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime, default=utc_now)

    transaction: Mapped["Transaction"] = relationship("Transaction", back_populates="protection_events")

