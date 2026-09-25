"""Insurance premium service with all validation, underwriting, and premium logic."""

from math import ceil

from .models import ErrorCode, PolicyApplication, PolicyResult, ResultStatus

AGE_MIN, AGE_MAX = 0, 100
BMI_MIN, BMI_MAX = 10.0, 60.0
INSURED_AMOUNT_MIN, INSURED_AMOUNT_MAX = 50, 2000
CLAIMS_MIN, CLAIMS_MAX = 0, 20

ACCEPTED_AGE_MIN, ACCEPTED_AGE_MAX = 1, 65
ACCEPTED_BMI_MIN, ACCEPTED_BMI_MAX = 16.0, 35.0
MAX_ALLOWED_CLAIMS_LAST_YEAR = 5

SENIOR_AGE_THRESHOLD = 56
SENIOR_MAX_INSURED_AMOUNT = 500

BASE_PREMIUM_PER_100M = {
    (1, 17): 900_000,
    (18, 30): 1_200_000,
    (31, 45): 1_800_000,
    (46, 55): 3_000_000,
    (56, 65): 5_500_000,
}

BMI_LOADING_BRACKETS = [
    (16.0, 18.5, 0.10),
    (18.5, 25.0, 0.00),
    (25.0, 30.0, 0.15),
    (30.0, 35.0000001, 0.35),
]

NO_CLAIM_BONUS = -0.05
LOW_CLAIM_LOADING = 0.00
MID_CLAIM_LOADING = 0.25
ROUNDING_UNIT = 1_000
PREMIUM_FLOOR = 500_000
INSURED_AMOUNT_UNIT = 100


def is_valid_domain(application: PolicyApplication) -> bool:
    if not (isinstance(application.age, int) and AGE_MIN <= application.age <= AGE_MAX):
        return False
    if not (isinstance(application.bmi, (int, float)) and BMI_MIN <= float(application.bmi) <= BMI_MAX):
        return False
    if not (
        isinstance(application.insured_amount, int)
        and INSURED_AMOUNT_MIN <= application.insured_amount <= INSURED_AMOUNT_MAX
    ):
        return False
    if not (
        isinstance(application.claims_last_year, int)
        and CLAIMS_MIN <= application.claims_last_year <= CLAIMS_MAX
    ):
        return False
    return True


def is_rejected(application: PolicyApplication) -> bool:
    if application.age < ACCEPTED_AGE_MIN or application.age > ACCEPTED_AGE_MAX:
        return True
    if application.bmi < ACCEPTED_BMI_MIN or application.bmi > ACCEPTED_BMI_MAX:
        return True
    if application.claims_last_year > MAX_ALLOWED_CLAIMS_LAST_YEAR:
        return True
    return False


def exceeds_age_based_amount_limit(application: PolicyApplication) -> bool:
    if application.age >= SENIOR_AGE_THRESHOLD:
        return application.insured_amount > SENIOR_MAX_INSURED_AMOUNT
    return False


def get_base_premium(age: int):
    for (low, high), amount in BASE_PREMIUM_PER_100M.items():
        if low <= age <= high:
            return amount
    return None


def get_bmi_loading(bmi: float):
    for low, high, loading in BMI_LOADING_BRACKETS:
        if low <= bmi < high:
            return loading
    return None


def get_claims_loading(claims_last_year: int):
    if claims_last_year == 0:
        return NO_CLAIM_BONUS
    if 1 <= claims_last_year <= 2:
        return LOW_CLAIM_LOADING
    if 3 <= claims_last_year <= 5:
        return MID_CLAIM_LOADING
    return None


def round_up_to_unit(amount: float, unit: int = ROUNDING_UNIT) -> int:
    return ceil(amount / unit) * unit


def apply_premium_floor(amount: int, floor: int = PREMIUM_FLOOR) -> int:
    return max(amount, floor)


def calculate_final_premium(age: int, bmi: float, insured_amount: int, claims_last_year: int) -> int:
    base_premium = get_base_premium(age)
    factor = 1.0 + get_bmi_loading(bmi) + get_claims_loading(claims_last_year)
    raw_premium = base_premium * (insured_amount / INSURED_AMOUNT_UNIT) * factor
    rounded_premium = round_up_to_unit(raw_premium)
    return apply_premium_floor(rounded_premium)


def calculate_premium(application: PolicyApplication) -> PolicyResult:
    if not is_valid_domain(application):
        return PolicyResult(status=ResultStatus.ERROR, error_code=ErrorCode.E01_INVALID_INPUT.value)

    if is_rejected(application):
        return PolicyResult(status=ResultStatus.REJECTED)

    if exceeds_age_based_amount_limit(application):
        return PolicyResult(
            status=ResultStatus.ERROR,
            error_code=ErrorCode.E02_AMOUNT_EXCEEDS_AGE_LIMIT.value,
        )

    annual_premium = calculate_final_premium(
        age=application.age,
        bmi=application.bmi,
        insured_amount=application.insured_amount,
        claims_last_year=application.claims_last_year,
    )

    return PolicyResult(status=ResultStatus.ACCEPTED, annual_premium=annual_premium)
