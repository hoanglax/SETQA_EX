from logic import calculate_credit_limit


# 1. Định nghĩa danh sách các Mutant (các phiên bản cấy lỗi)
def mutant_m1_boundary_age(age: int, monthly_salary: float) -> dict:
    """M1: Đột biến toán tử tuổi (age < 20 -> age <= 20)"""
    if not isinstance(age, int) or isinstance(age, bool):
        return {"status": "REJECTED", "reason": "Invalid Age"}
    if not isinstance(monthly_salary, (int, float)) or isinstance(
        monthly_salary, bool
    ):
        return {"status": "REJECTED", "reason": "Invalid Salary"}

    # LỖI CẤY Ở ĐÂY: < thành <=
    if age <= 20 or age > 60:
        return {"status": "REJECTED", "reason": "Invalid Age"}
    if monthly_salary < 10.0:
        return {"status": "REJECTED", "reason": "Invalid Salary"}

    effective_salary = min(float(monthly_salary), 200.0)
    tier = (
        "Silver Tier"
        if effective_salary < 30.0
        else "Gold Tier"
        if effective_salary < 80.0
        else "Platinum Tier"
    )
    multiplier = 3 if effective_salary < 30.0 else 5 if effective_salary < 80.0 else 7
    age_risk = 0.9 if (20 <= age <= 25) else 1.0
    return {
        "status": "APPROVED",
        "tier": tier,
        "credit_limit": round(effective_salary * multiplier * age_risk, 2),
    }


def mutant_m2_tier_boundary(age: int, monthly_salary: float) -> dict:
    """M2: Đột biến ranh giới Gold (< 30.0 -> <= 30.0)"""
    if not isinstance(age, int) or isinstance(age, bool):
        return {"status": "REJECTED", "reason": "Invalid Age"}
    if not isinstance(monthly_salary, (int, float)) or isinstance(
        monthly_salary, bool
    ):
        return {"status": "REJECTED", "reason": "Invalid Salary"}

    if age < 20 or age > 60:
        return {"status": "REJECTED", "reason": "Invalid Age"}
    if monthly_salary < 10.0:
        return {"status": "REJECTED", "reason": "Invalid Salary"}

    effective_salary = min(float(monthly_salary), 200.0)

    # LỖI CẤY Ở ĐÂY: < thành <= ở phân hạng Silver
    if effective_salary <= 30.0:
        tier, multiplier = "Silver Tier", 3
    elif effective_salary < 80.0:
        tier, multiplier = "Gold Tier", 5
    else:
        tier, multiplier = "Platinum Tier", 7

    age_risk = 0.9 if (20 <= age <= 25) else 1.0
    return {
        "status": "APPROVED",
        "tier": tier,
        "credit_limit": round(effective_salary * multiplier * age_risk, 2),
    }


def mutant_m3_missing_bool_check(age: int, monthly_salary: float) -> dict:
    """M3: Đột biến bỏ check isinstance(..., bool)"""
    # LỖI CẤY Ở ĐÂY: Bỏ isinstance(age, bool)
    if not isinstance(age, int):
        return {"status": "REJECTED", "reason": "Invalid Age"}
    if not isinstance(monthly_salary, (int, float)) or isinstance(
        monthly_salary, bool
    ):
        return {"status": "REJECTED", "reason": "Invalid Salary"}

    if age < 20 or age > 60:
        return {"status": "REJECTED", "reason": "Invalid Age"}
    if monthly_salary < 10.0:
        return {"status": "REJECTED", "reason": "Invalid Salary"}

    effective_salary = min(float(monthly_salary), 200.0)
    tier = (
        "Silver Tier"
        if effective_salary < 30.0
        else "Gold Tier"
        if effective_salary < 80.0
        else "Platinum Tier"
    )
    multiplier = 3 if effective_salary < 30.0 else 5 if effective_salary < 80.0 else 7
    age_risk = 0.9 if (20 <= age <= 25) else 1.0
    return {
        "status": "APPROVED",
        "tier": tier,
        "credit_limit": round(effective_salary * multiplier * age_risk, 2),
    }


def mutant_m4_precision_round(age: int, monthly_salary: float) -> dict:
    """M4: Đột biến độ chính xác làm tròn (2 decimal -> 3 decimal)"""
    if not isinstance(age, int) or isinstance(age, bool):
        return {"status": "REJECTED", "reason": "Invalid Age"}
    if not isinstance(monthly_salary, (int, float)) or isinstance(
        monthly_salary, bool
    ):
        return {"status": "REJECTED", "reason": "Invalid Salary"}

    if age < 20 or age > 60:
        return {"status": "REJECTED", "reason": "Invalid Age"}
    if monthly_salary < 10.0:
        return {"status": "REJECTED", "reason": "Invalid Salary"}

    effective_salary = min(float(monthly_salary), 200.0)
    tier = (
        "Silver Tier"
        if effective_salary < 30.0
        else "Gold Tier"
        if effective_salary < 80.0
        else "Platinum Tier"
    )
    multiplier = 3 if effective_salary < 30.0 else 5 if effective_salary < 80.0 else 7
    age_risk = 0.9 if (20 <= age <= 25) else 1.0

    # LỖI CẤY Ở ĐÂY: round 3 chữ số thập phân
    return {
        "status": "APPROVED",
        "tier": tier,
        "credit_limit": round(effective_salary * multiplier * age_risk, 3),
    }


# 2. Bộ dữ liệu Test Suite hiện tại (lấy từ test_loan_service.py)
TEST_SUITE = [
    (19, 105.0, {"status": "REJECTED", "reason": "Invalid Age"}, "AGE_19_Invalid"),
    (
        20,
        105.0,
        {"status": "APPROVED", "tier": "Platinum Tier", "credit_limit": 661.5},
        "AGE_20_Min",
    ),
    (
        21,
        105.0,
        {"status": "APPROVED", "tier": "Platinum Tier", "credit_limit": 661.5},
        "AGE_21_Min+",
    ),
    (
        26,
        105.0,
        {"status": "APPROVED", "tier": "Platinum Tier", "credit_limit": 735.0},
        "AGE_26_Risk1.0",
    ),
    (
        40,
        30.0,
        {"status": "APPROVED", "tier": "Gold Tier", "credit_limit": 150.0},
        "SAL_30.0_Gold_Min",
    ),
    (
        True,
        105.0,
        {"status": "REJECTED", "reason": "Invalid Age"},
        "TYPE_Bool_Age",
    ),
]


# 3. Kịch bản chạy đánh giá Đột biến
def run_mutation_analysis():
    mutants = [
        ("M1 (Boundary Age)", mutant_m1_boundary_age, "Sửa age < 20 thành age <= 20"),
        (
            "M2 (Tier Ranh Giới)",
            mutant_m2_tier_boundary,
            "Sửa effective_salary < 30.0 thành <= 30.0",
        ),
        (
            "M3 (Check Bool)",
            mutant_m3_missing_bool_check,
            "Bỏ điều kiện check isinstance(age, bool)",
        ),
        (
            "M4 (Làm tròn 3 số)",
            mutant_m4_precision_round,
            "Sửa round(..., 2) thành round(..., 3)",
        ),
    ]

    print("\n=== BÁO CÁO KẾT QUẢ KIỂM THỬ ĐỘT BIẾN (MUTATION TEST REPORT) ===\n")
    print(
        "| Mã Mutant | Mô tả lỗi cấy | Trạng thái | Test Case phát hiện / Nguyên nhân |"
    )
    print(
        "| :--- | :--- | :---: | :--- |"
    )

    killed_count = 0

    for name, mutant_func, desc in mutants:
        killed_by = None
        for age, salary, expected, test_id in TEST_SUITE:
            try:
                actual = mutant_func(age, salary)
                if actual != expected:
                    killed_by = test_id
                    break
            except Exception:
                killed_by = test_id
                break

        if killed_by:
            killed_count += 1
            status = "**KILLED**"
            reason = f"Phát hiện bởi `{killed_by}`"
        else:
            status = "**SURVIVED**"
            reason = "Bộ test chưa có trường hợp phân biệt số dư 3 chữ số thập phân"

        print(f"| {name} | {desc} | {status} | {reason} |")

    score = (killed_count / len(mutants)) * 100
    print(
        f"\n**Chỉ số Mutation Score:** {killed_count}/{len(mutants)} ({score:.1f}%)\n"
    )


if __name__ == "__main__":
    run_mutation_analysis()