import pytest
from src.insurance_service import calculate_premium
from src.models import ErrorCode, PolicyApplication, PolicyResult, ResultStatus


def make_app(age=30, bmi=22.0, insured_amount=500, claims_last_year=0):
    return PolicyApplication(
        age=age,
        bmi=bmi,
        insured_amount=insured_amount,
        claims_last_year=claims_last_year,
    )


@pytest.mark.parametrize(
    "app, expected",
    [
        # BASELINE (Hợp lệ chuẩn)
        (make_app(), PolicyResult(status=ResultStatus.ACCEPTED, annual_premium=5_700_000)),

        # 1. AGE BVA (Domain [0, 100] & Accepted [1, 65] & Internal Brackets)
        # 7 Biên Domain & Accepted
        (make_app(age=-1), PolicyResult(status=ResultStatus.ERROR, error_code=ErrorCode.E01_INVALID_INPUT.value)),
        (make_app(age=0), PolicyResult(status=ResultStatus.REJECTED)),
        (make_app(age=1), PolicyResult(status=ResultStatus.ACCEPTED, annual_premium=4_275_000)),
        (make_app(age=2), PolicyResult(status=ResultStatus.ACCEPTED, annual_premium=4_275_000)),
        (make_app(age=64), PolicyResult(status=ResultStatus.ACCEPTED, annual_premium=26_125_000)),
        (make_app(age=65), PolicyResult(status=ResultStatus.ACCEPTED, annual_premium=26_125_000)),
        (make_app(age=66), PolicyResult(status=ResultStatus.REJECTED)),
        (make_app(age=99), PolicyResult(status=ResultStatus.REJECTED)),
        (make_app(age=100), PolicyResult(status=ResultStatus.REJECTED)),
        (make_app(age=101), PolicyResult(status=ResultStatus.ERROR, error_code=ErrorCode.E01_INVALID_INPUT.value)),
        # Biên nội Tuổi (Khung phí cơ bản: 1-17, 18-30, 31-45, 46-55, 56-65)
        (make_app(age=17), PolicyResult(status=ResultStatus.ACCEPTED, annual_premium=4_275_000)),
        (make_app(age=18), PolicyResult(status=ResultStatus.ACCEPTED, annual_premium=5_700_000)),
        (make_app(age=30), PolicyResult(status=ResultStatus.ACCEPTED, annual_premium=5_700_000)),
        (make_app(age=31), PolicyResult(status=ResultStatus.ACCEPTED, annual_premium=8_550_000)),
        (make_app(age=45), PolicyResult(status=ResultStatus.ACCEPTED, annual_premium=8_550_000)),
        (make_app(age=46), PolicyResult(status=ResultStatus.ACCEPTED, annual_premium=14_250_000)),
        (make_app(age=55), PolicyResult(status=ResultStatus.ACCEPTED, annual_premium=14_250_000)),
        (make_app(age=56, insured_amount=500), PolicyResult(status=ResultStatus.ACCEPTED, annual_premium=26_125_000)),

        # 2. BMI BVA (Domain [10.0, 60.0] & Accepted [16.0, 35.0] & Internal Brackets)
        # 7 Biên Domain & Accepted
        (make_app(bmi=9.9), PolicyResult(status=ResultStatus.ERROR, error_code=ErrorCode.E01_INVALID_INPUT.value)),
        (make_app(bmi=10.0), PolicyResult(status=ResultStatus.REJECTED)),
        (make_app(bmi=16.0), PolicyResult(status=ResultStatus.ACCEPTED, annual_premium=6_300_000)),
        (make_app(bmi=16.1), PolicyResult(status=ResultStatus.ACCEPTED, annual_premium=6_300_000)),
        (make_app(bmi=34.9), PolicyResult(status=ResultStatus.ACCEPTED, annual_premium=7_800_000)),
        (make_app(bmi=35.0), PolicyResult(status=ResultStatus.ACCEPTED, annual_premium=7_800_000)),
        (make_app(bmi=35.1), PolicyResult(status=ResultStatus.REJECTED)),
        (make_app(bmi=59.9), PolicyResult(status=ResultStatus.REJECTED)),
        (make_app(bmi=60.0), PolicyResult(status=ResultStatus.REJECTED)),
        (make_app(bmi=60.1), PolicyResult(status=ResultStatus.ERROR, error_code=ErrorCode.E01_INVALID_INPUT.value)),
        # Biên nội BMI (Khung phụ phí: [16.0-18.5: 10%], [18.5-25.0: 0%], [25.0-30.0: 15%], [30.0-35.0: 35%])
        (make_app(bmi=18.4), PolicyResult(status=ResultStatus.ACCEPTED, annual_premium=6_300_000)),
        (make_app(bmi=18.5), PolicyResult(status=ResultStatus.ACCEPTED, annual_premium=5_700_000)),
        (make_app(bmi=24.9), PolicyResult(status=ResultStatus.ACCEPTED, annual_premium=5_700_000)),
        (make_app(bmi=25.0), PolicyResult(status=ResultStatus.ACCEPTED, annual_premium=6_600_000)),
        (make_app(bmi=29.9), PolicyResult(status=ResultStatus.ACCEPTED, annual_premium=6_600_000)),
        (make_app(bmi=30.0), PolicyResult(status=ResultStatus.ACCEPTED, annual_premium=7_800_000)),

        # 3. INSURED AMOUNT BVA (Domain [50, 2000] & Senior Cap)
        # 7 Biên Domain
        (make_app(insured_amount=49), PolicyResult(status=ResultStatus.ERROR, error_code=ErrorCode.E01_INVALID_INPUT.value)),
        (make_app(insured_amount=50), PolicyResult(status=ResultStatus.ACCEPTED, annual_premium=570_000)),
        (make_app(insured_amount=51), PolicyResult(status=ResultStatus.ACCEPTED, annual_premium=582_000)),
        (make_app(insured_amount=1999), PolicyResult(status=ResultStatus.ACCEPTED, annual_premium=22_789_000)),
        (make_app(insured_amount=2000), PolicyResult(status=ResultStatus.ACCEPTED, annual_premium=22_800_000)),
        (make_app(insured_amount=2001), PolicyResult(status=ResultStatus.ERROR, error_code=ErrorCode.E01_INVALID_INPUT.value)),
        # Senior Cap Boundary (Age >= 56, Max Amount = 500)
        (make_app(age=56, insured_amount=500), PolicyResult(status=ResultStatus.ACCEPTED, annual_premium=26_125_000)),
        (make_app(age=56, insured_amount=501), PolicyResult(status=ResultStatus.ERROR, error_code=ErrorCode.E02_AMOUNT_EXCEEDS_AGE_LIMIT.value)),

        # 4. CLAIMS BVA (Domain [0, 20] & Accepted [0, 5] & Internal Brackets)
        # 7 Biên Domain & Accepted
        (make_app(claims_last_year=-1), PolicyResult(status=ResultStatus.ERROR, error_code=ErrorCode.E01_INVALID_INPUT.value)),
        (make_app(claims_last_year=0), PolicyResult(status=ResultStatus.ACCEPTED, annual_premium=5_700_000)),
        (make_app(claims_last_year=5), PolicyResult(status=ResultStatus.ACCEPTED, annual_premium=7_500_000)),
        (make_app(claims_last_year=6), PolicyResult(status=ResultStatus.REJECTED)),
        (make_app(claims_last_year=19), PolicyResult(status=ResultStatus.REJECTED)),
        (make_app(claims_last_year=20), PolicyResult(status=ResultStatus.REJECTED)),
        (make_app(claims_last_year=21), PolicyResult(status=ResultStatus.ERROR, error_code=ErrorCode.E01_INVALID_INPUT.value)),
        # Biên nội Claims (0: -5% bonus, 1-2: 0% loading, 3-5: +25% loading)
        (make_app(claims_last_year=1), PolicyResult(status=ResultStatus.ACCEPTED, annual_premium=6_000_000)),
        (make_app(claims_last_year=2), PolicyResult(status=ResultStatus.ACCEPTED, annual_premium=6_000_000)),
        (make_app(claims_last_year=3), PolicyResult(status=ResultStatus.ACCEPTED, annual_premium=7_500_000)),

        # 5. SPECIAL BUSINESS LOGIC (Sàn phí, Làm tròn & Kiểu dữ liệu)
        # Chạm sàn phí tối thiểu (Kèo tính ra 472.500 VND -> Làm tròn 473.000 VND -> Ép lên Sàn 500.000 VND)
        (make_app(age=1, bmi=16.0, insured_amount=50, claims_last_year=0), PolicyResult(status=ResultStatus.ACCEPTED, annual_premium=500_000)),
        
        # Kiểm thử Kiểu dữ liệu không hợp lệ (Type Checking)
        (make_app(age="30"), PolicyResult(status=ResultStatus.ERROR, error_code=ErrorCode.E01_INVALID_INPUT.value)),
        (make_app(bmi="22.0"), PolicyResult(status=ResultStatus.ERROR, error_code=ErrorCode.E01_INVALID_INPUT.value)),
        (make_app(insured_amount=500.5), PolicyResult(status=ResultStatus.ERROR, error_code=ErrorCode.E01_INVALID_INPUT.value)),
        (make_app(claims_last_year=None), PolicyResult(status=ResultStatus.ERROR, error_code=ErrorCode.E01_INVALID_INPUT.value)),
        (make_app(bmi=float("nan")), PolicyResult(status=ResultStatus.ERROR, error_code=ErrorCode.E01_INVALID_INPUT.value)),

        # 6. ĐỘ ƯU TIÊN GIỮA CÁC LỖI (E01 > REJECTED > E02)
        (make_app(age=-1, bmi=9.9), PolicyResult(status=ResultStatus.ERROR, error_code=ErrorCode.E01_INVALID_INPUT.value)),
        (make_app(age=66, insured_amount=600), PolicyResult(status=ResultStatus.REJECTED)),
        (make_app(age=56, insured_amount=501, claims_last_year=6), PolicyResult(status=ResultStatus.REJECTED)),
        (make_app(age=56, insured_amount=2001), PolicyResult(status=ResultStatus.ERROR, error_code=ErrorCode.E01_INVALID_INPUT.value)),

        # 7. TỔ HỢP NHIỀU BIÊN CÙNG LÚC
        # 5.5M * 5 * (1 + 0.35 + 0.25) = 44,000,000
        (make_app(age=65, bmi=35.0, insured_amount=500, claims_last_year=5), PolicyResult(status=ResultStatus.ACCEPTED, annual_premium=44_000_000)),
        # 0.9M * 0.5 * (1 + 0.10 + 0.25) = 607,500 -> 608,000
        (make_app(age=1, bmi=16.0, insured_amount=50, claims_last_year=5), PolicyResult(status=ResultStatus.ACCEPTED, annual_premium=608_000)),
    ],
    ids=[
        "BASELINE",
        # AGE
        "AGE_Dom_Min-", "AGE_Dom_Min", "AGE_Acc_Min", "AGE_Acc_Min+", "AGE_Acc_Max-", "AGE_Acc_Max", "AGE_Acc_Max+", "AGE_Dom_Max-", "AGE_Dom_Max", "AGE_Dom_Max+",
        "AGE_Int_17_Youth", "AGE_Int_18_Adult", "AGE_Int_30_Adult_Max", "AGE_Int_31_Mid", "AGE_Int_45_Mid_Max", "AGE_Int_46_Older", "AGE_Int_55_Older_Max", "AGE_Int_56_Senior",
        # BMI
        "BMI_Dom_Min-", "BMI_Dom_Min", "BMI_Acc_Min", "BMI_Acc_Min+", "BMI_Acc_Max-", "BMI_Acc_Max", "BMI_Acc_Max+", "BMI_Dom_Max-", "BMI_Dom_Max", "BMI_Dom_Max+",
        "BMI_Int_18.4_Under", "BMI_Int_18.5_Normal", "BMI_Int_24.9_Normal_Max", "BMI_Int_25.0_Over", "BMI_Int_29.9_Over_Max", "BMI_Int_30.0_Obese",
        # INSURED AMOUNT
        "AMT_Dom_Min-", "AMT_Dom_Min", "AMT_Dom_Min+", "AMT_Dom_Max-", "AMT_Dom_Max", "AMT_Dom_Max+",
        "SENIOR_Cap_Border_OK", "SENIOR_Cap_Exceeded",
        # CLAIMS
        "CLM_Dom_Min-", "CLM_Acc_Min", "CLM_Acc_Max", "CLM_Acc_Max+", "CLM_Dom_Max-", "CLM_Dom_Max", "CLM_Dom_Max+",
        "CLM_Int_1_Low", "CLM_Int_2_Low_Max", "CLM_Int_3_Mid",
        # SPECIAL
        "SPECIAL_Premium_Floor",
        "TYPE_Age_Str", "TYPE_BMI_Str", "TYPE_Amount_Float", "TYPE_Claims_None", "TYPE_BMI_NaN",
        # PRIORITY
        "PRIO_E01_Over_Reject", "PRIO_Reject_Over_E02_Age", "PRIO_Reject_Over_E02_Claims", "PRIO_E01_Over_E02",
        # COMBO
        "COMBO_Max_Loading_Senior", "COMBO_Min_Age_Min_Amt_Mid_Claims",
    ]
)
def test_calculate_premium_comprehensive_bva(app, expected):
    assert calculate_premium(app) == expected