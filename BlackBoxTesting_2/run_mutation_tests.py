from typing import Callable

from src.models import ErrorCode, PolicyApplication, PolicyResult, ResultStatus
import src.insurance_service as orig_module

# Import hàm test từ test_insurance_service
from tests.test_bva_single import test_calculate_premium_comprehensive_bva


def mutant_M1_age_min_domain(application: PolicyApplication) -> PolicyResult:
    """M1: Thay đổi AGE_MIN <= age thành AGE_MIN < age (Bỏ qua biên age = 0)."""
    # Clone module & sửa logic
    if isinstance(application.age, bool) or not isinstance(application.age, int) or not (0 < application.age <= 100):
        return PolicyResult(status=ResultStatus.ERROR, error_code=ErrorCode.E01_INVALID_INPUT.value)
    return orig_module.calculate_premium(application)


def mutant_M2_bmi_rejected_bound(application: PolicyApplication) -> PolicyResult:
    """M2: Thay application.bmi < 16.0 thành <= 16.0 (Từ chối nhầm bmi = 16.0)."""
    if not orig_module.is_valid_domain(application):
        return PolicyResult(status=ResultStatus.ERROR, error_code=ErrorCode.E01_INVALID_INPUT.value)
    
    # Mutant logic
    if application.age < 1 or application.age > 65 or application.bmi <= 16.0 or application.bmi > 35.0 or application.claims_last_year > 5:
        return PolicyResult(status=ResultStatus.REJECTED)

    if orig_module.exceeds_age_based_amount_limit(application):
        return PolicyResult(status=ResultStatus.ERROR, error_code=ErrorCode.E02_AMOUNT_EXCEEDS_AGE_LIMIT.value)

    annual_premium = orig_module.calculate_final_premium(application.age, application.bmi, application.insured_amount, application.claims_last_year)
    return PolicyResult(status=ResultStatus.ACCEPTED, annual_premium=annual_premium)


def mutant_M3_senior_threshold(application: PolicyApplication) -> PolicyResult:
    """M3: Thay age >= 56 thành age > 56 (Bỏ sót kiểm tra hạn mức cho người đúng 56 tuổi)."""
    if not orig_module.is_valid_domain(application):
        return PolicyResult(status=ResultStatus.ERROR, error_code=ErrorCode.E01_INVALID_INPUT.value)
    if orig_module.is_rejected(application):
        return PolicyResult(status=ResultStatus.REJECTED)

    # Mutant: Khống chế hạn mức dùng age > 56 thay vì >= 56
    exceeds_limit = (application.age > 56) and (application.insured_amount > 500)
    if exceeds_limit:
        return PolicyResult(status=ResultStatus.ERROR, error_code=ErrorCode.E02_AMOUNT_EXCEEDS_AGE_LIMIT.value)

    annual_premium = orig_module.calculate_final_premium(application.age, application.bmi, application.insured_amount, application.claims_last_year)
    return PolicyResult(status=ResultStatus.ACCEPTED, annual_premium=annual_premium)


def mutant_M4_no_claim_bonus(application: PolicyApplication) -> PolicyResult:
    """M4: Bỏ Bonus cho người không có claim (thay -0.05 thành 0.0)."""
    if not orig_module.is_valid_domain(application):
        return PolicyResult(status=ResultStatus.ERROR, error_code=ErrorCode.E01_INVALID_INPUT.value)
    if orig_module.is_rejected(application):
        return PolicyResult(status=ResultStatus.REJECTED)
    if orig_module.exceeds_age_based_amount_limit(application):
        return PolicyResult(status=ResultStatus.ERROR, error_code=ErrorCode.E02_AMOUNT_EXCEEDS_AGE_LIMIT.value)

    base_premium = orig_module.get_base_premium(application.age)
    # Mutant: claim == 0 thì factor không trừ 0.05
    claims_loading = 0.0 if application.claims_last_year == 0 else orig_module.get_claims_loading(application.claims_last_year)
    factor = 1.0 + orig_module.get_bmi_loading(application.bmi) + claims_loading
    raw_premium = base_premium * (application.insured_amount / 100) * factor
    rounded = orig_module.round_up_to_unit(raw_premium)
    return PolicyResult(status=ResultStatus.ACCEPTED, annual_premium=orig_module.apply_premium_floor(rounded))


def mutant_M5_rounding_floor_logic(application: PolicyApplication) -> PolicyResult:
    """M5: Quên áp dụng Sàn phí tối thiểu (Premium Floor = 500k)."""
    if not orig_module.is_valid_domain(application):
        return PolicyResult(status=ResultStatus.ERROR, error_code=ErrorCode.E01_INVALID_INPUT.value)
    if orig_module.is_rejected(application):
        return PolicyResult(status=ResultStatus.REJECTED)
    if orig_module.exceeds_age_based_amount_limit(application):
        return PolicyResult(status=ResultStatus.ERROR, error_code=ErrorCode.E02_AMOUNT_EXCEEDS_AGE_LIMIT.value)

    base_premium = orig_module.get_base_premium(application.age)
    factor = 1.0 + orig_module.get_bmi_loading(application.bmi) + orig_module.get_claims_loading(application.claims_last_year)
    raw_premium = base_premium * (application.insured_amount / 100) * factor
    rounded_premium = orig_module.round_up_to_unit(raw_premium)
    # Mutant: Trả về rounded_premium trực tiếp mà không qua apply_premium_floor
    return PolicyResult(status=ResultStatus.ACCEPTED, annual_premium=rounded_premium)



# HÀM CHẠY TEST ĐỂ KIỂM TRA MUTANT BỊ DIỆT HAY SỐNG


MUTANTS = [
    ("M1_AGE_MIN_DOMAIN", mutant_M1_age_min_domain, "Change AGE_MIN <= age to AGE_MIN < age (Skip age = 0)."),
    ("M2_BMI_REJECTED_BOUND", mutant_M2_bmi_rejected_bound, "Change bmi < 16.0 to bmi <= 16.0 (Reject bmi = 16.0)."),
    ("M3_SENIOR_THRESHOLD", mutant_M3_senior_threshold, "Change age >= 56 to age > 56 (Skip senior check at age = 56)."),
    ("M4_NO_CLAIM_BONUS", mutant_M4_no_claim_bonus, "Remove 5% bonus for 0 claim"),
    ("M5_PREMIUM_FLOOR_OMITTED", mutant_M5_rounding_floor_logic, "Skip applying 500,000 VND floor"),
]



def run_tests_against_mutant(mutant_func: Callable) -> tuple[bool, str]:
    """Chạy toàn bộ test cases đối với Mutant. Trả về (is_killed, killing_test_id)."""
    # Lấy dữ liệu từ decorator @pytest.mark.parametrize của test function
    decorator = test_calculate_premium_comprehensive_bva.pytestmark[0]
    argvalues = decorator.args[1]
    ids = decorator.kwargs['ids']

    for idx, (app, expected) in enumerate(argvalues):
        test_id = ids[idx]
        try:
            actual = mutant_func(app)
            if actual != expected:
                # Test phát hiện sự khác biệt -> MUTANT KILLED!
                return True, test_id
        except Exception:
            # Mutant gây ra crash/exception -> MUTANT KILLED!
            return True, test_id

    # Nếu tất cả test cases đều PASSED -> MUTANT SURVIVED!
    return False, "None"


def main():
    print("=" * 80)
    print("      MUTATION TESTING REPORT - INSURANCE SERVICE")
    print("=" * 80)
    print(f"{'STT':<6}{'Mutant code':<25}{'Status':<15}{'Killing Test Case':<35}")
    print("-" * 80)

    killed_count = 0
    total_mutants = len(MUTANTS)

    for idx, (code, func, desc) in enumerate(MUTANTS, 1):
        is_killed, killer_tc = run_tests_against_mutant(func)
        if is_killed:
            status = "KILLED"
            killed_count += 1
            info = f"killed by: {killer_tc}"
        else:
            status = "SURVIVED"
            info = "No test found"

        print(f"{idx:<6}{code:<25}{status:<15}{info:<35}")

    score = (killed_count / total_mutants) * 100
    print("-" * 80)
    print(f"Total Mutants: {total_mutants}")
    print(f"Killed Mutants: {killed_count}")
    print(f"Mutation Score: {score:.1f}%")
    print("=" * 80)


if __name__ == "__main__":
    main()