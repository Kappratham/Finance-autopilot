from pydantic import BaseModel
from typing import Optional
from enum import Enum


class Currency(str, Enum):
    INR = "INR"
    USD = "USD"


class Category(str, Enum):
    FOOD = "Food"
    TRANSPORT = "Transport"
    UTILITIES = "Utilities"
    ENTERTAINMENT = "Entertainment"
    SHOPPING = "Shopping"
    HEALTHCARE = "Healthcare"
    TRANSFERS = "Transfers"
    INCOME = "Income"
    OTHER = "Other"


class Transaction(BaseModel):
    id: str
    date: str
    description: str
    amount: float
    type: str  # "debit" or "credit"
    currency: Currency
    category: Optional[Category] = None
    balance: Optional[float] = None


class ParsedStatement(BaseModel):
    bank_name: str
    account_holder: Optional[str] = None
    statement_period: Optional[str] = None
    currency: Currency
    total_credits: float
    total_debits: float
    transactions: list[Transaction]


class UploadResponse(BaseModel):
    success: bool
    message: str
    statement: Optional[ParsedStatement] = None
    error: Optional[str] = None


class TransactionResponse(BaseModel):
    transactions: list[Transaction]
    total: int
    currency: Currency
    total_credits: float
    total_debits: float
    net: float
