import pytest
from loan_service.logic import calculate_credit_limit, format_result


@pytest.mark.parametrize(
    "age, salary, expected",
    [
        # 21 BVA CORE CASES
        (19, 105.0, {"status": "REJECTED", "reason": "Invalid Age"}),
        (20, 105.0, {"status": "APPROVED", "tier": "Platinum Tier", "credit_limit": 661.5}),
        (21, 105.0, {"status": "APPROVED", "tier": "Platinum Tier", "credit_limit": 661.5}),
        (25, 105.0, {"status": "APPROVED", "tier": "Platinum Tier", "credit_limit": 661.5}),
        (26, 105.0, {"status": "APPROVED", "tier": "Platinum Tier", "credit_limit": 735.0}),
        (59, 105.0, {"status": "APPROVED", "tier": "Platinum Tier", "credit_limit": 735.0}),
        (60, 105.0, {"status": "APPROVED", "tier": "Platinum Tier", "credit_limit": 735.0}),
        (61, 105.0, {"status": "REJECTED", "reason": "Invalid Age"}),
        (40, 9.9, {"status": "REJECTED", "reason": "Invalid Salary"}),
        (40, 10.0, {"status": "APPROVED", "tier": "Silver Tier", "credit_limit": 30.0}),
        (40, 10.1, {"status": "APPROVED", "tier": "Silver Tier", "credit_limit": 30.3}),
        (40, 29.9, {"status": "APPROVED", "tier": "Silver Tier", "credit_limit": 89.7}),
        (40, 30.0, {"status": "APPROVED", "tier": "Gold Tier", "credit_limit": 150.0}),
        (40, 30.1, {"status": "APPROVED", "tier": "Gold Tier", "credit_limit": 150.5}),
        (40, 79.9, {"status": "APPROVED", "tier": "Gold Tier", "credit_limit": 399.5}),
        (40, 80.0, {"status": "APPROVED", "tier": "Platinum Tier", "credit_limit": 560.0}),
        (40, 80.1, {"status": "APPROVED", "tier": "Platinum Tier", "credit_limit": 560.7}),
        (40, 199.9, {"status": "APPROVED", "tier": "Platinum Tier", "credit_limit": 1399.3}),
        (40, 200.0, {"status": "APPROVED", "tier": "Platinum Tier", "credit_limit": 1400.0}),
        (40, 200.1, {"status": "APPROVED", "tier": "Platinum Tier", "credit_limit": 1400.0}),
        (40, 105.0, {"status": "APPROVED", "tier": "Platinum Tier", "credit_limit": 735.0}),
        
        #　TYPE CHECKING CASES
        (True, 105.0, {"status": "REJECTED", "reason": "Invalid Age"}),
        (40, True, {"status": "REJECTED", "reason": "Invalid Salary"}),
    ],
    ids=[
        "AGE_19_Invalid", "AGE_20_Min", "AGE_21_Min+", "AGE_25_Risk0.9", "AGE_26_Risk1.0",
        "AGE_59_Max-", "AGE_60_Max", "AGE_61_Invalid",
        "SAL_9.9_Invalid", "SAL_10.0_Min", "SAL_10.1_Min+", "SAL_29.9_Silver_Max",
        "SAL_30.0_Gold_Min", "SAL_30.1_Gold_Min+", "SAL_79.9_Gold_Max", "SAL_80.0_Plat_Min",
        "SAL_80.1_Plat_Min+", "SAL_199.9_Max-", "SAL_200.0_Max", "SAL_200.1_Capped",
        "BASELINE_Nom_Nom",
        "TYPE_Bool_Age", "TYPE_Bool_Salary"
    ]
)
def test_bva_suite(age, salary, expected):
    assert calculate_credit_limit(age, salary) == expected


# FORMAT RESULT TESTS 
def test_format_result_approved():
    result = {"status": "APPROVED", "tier": "Gold Tier", "credit_limit": 225.0}
    assert format_result(result) == "APPROVED - Gold Tier - 225.0"


def test_format_result_rejected():
    result = {"status": "REJECTED", "reason": "Invalid Age"}
    assert format_result(result) == "REJECTED - Invalid Age"


def test_format_result_non_dict():
    assert format_result("ERROR_STRING") == "ERROR_STRING"