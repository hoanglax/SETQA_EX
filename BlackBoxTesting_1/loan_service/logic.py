AGE_MIN, AGE_MAX = 20, 60
SALARY_MIN, SALARY_MAX = 10.0, 200.0


def format_result(result: dict) -> str:
    if not isinstance(result, dict):
        return str(result)

    if result.get("status") == "APPROVED":
        return f"{result.get('status')} - {result.get('tier')} - {result.get('credit_limit')}"

    return f"{result.get('status')} - {result.get('reason')}"


def calculate_credit_limit(age: int, monthly_salary: float) -> dict:
    # 1. Kiểm tra kiểu dữ liệu
    if not isinstance(age, int) or isinstance(age, bool):
        return {"status": "REJECTED", "reason": "Invalid Age"}
    if not isinstance(monthly_salary, (int, float)) or isinstance(monthly_salary, bool):
        return {"status": "REJECTED", "reason": "Invalid Salary"}

    # 2. Kiểm tra biên ngoại (Outside Boundaries)
    if age < AGE_MIN or age > AGE_MAX:
        return {"status": "REJECTED", "reason": "Invalid Age"}
    if monthly_salary < SALARY_MIN or monthly_salary > SALARY_MAX:
        return {"status": "REJECTED", "reason": "Invalid Salary"}

    # 3. Áp dụng trần thu nhập (Capping limit)
    effective_salary = min(float(monthly_salary), SALARY_MAX)

    # 4. Phân hạng 3 Tier theo Thu nhập
    if effective_salary < 30.0:
        tier = "Silver Tier"
        base_multiplier = 3
    elif effective_salary < 80.0:
        tier = "Gold Tier"
        base_multiplier = 5
    else:
        tier = "Platinum Tier"
        base_multiplier = 7

    # 5. Hệ số rủi ro theo độ tuổi
    age_risk_factor = 0.9 if (20 <= age <= 25) else 1.0

    # 6. Tính hạn mức cuối cùng
    credit_limit = effective_salary * base_multiplier * age_risk_factor

    return {
        "status": "APPROVED",
        "tier": tier,
        "credit_limit": round(credit_limit, 2)
    }