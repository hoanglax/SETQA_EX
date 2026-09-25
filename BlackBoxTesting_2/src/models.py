"""Data models used across the insurance premium calculation service."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ResultStatus(str, Enum):
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    ERROR = "ERROR"


class ErrorCode(str, Enum):
    E01_INVALID_INPUT = "E01: Invalid input data"
    E02_AMOUNT_EXCEEDS_AGE_LIMIT = "E02: Insured amount exceeds age-based limit"


@dataclass(frozen=True)
class PolicyApplication:
    """Raw input submitted by the customer.

    Attributes:
        age: Age of the insured person. Valid range [0, 100].
        bmi: Body Mass Index, 1 decimal place. Valid range [10.0, 60.0].
        insured_amount: Requested sum insured, in million VND. Valid range [50, 2000].
        claims_last_year: Number of claims filed in the last 12 months. Valid range [0, 20].
    """

    age: int
    bmi: float
    insured_amount: int
    claims_last_year: int


@dataclass(frozen=True)
class PolicyResult:
    """Outcome of processing a PolicyApplication."""

    status: ResultStatus
    annual_premium: Optional[int] = None
    error_code: Optional[str] = None
