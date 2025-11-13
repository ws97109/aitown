#!/usr/bin/env python3
"""
創建收入與財務狀況調查問卷
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from survey_system import Survey, SurveyManager, AIResidentSurveyFiller


def create_income_survey():
    """創建關於收入的問卷"""
    print("正在創建收入調查問卷...")

    survey = Survey(
        title="社區居民收入與財務狀況調查",
        description="這份問卷旨在了解社區居民的收入來源、支出狀況與財務規劃。所有資料將保密處理，僅供社區發展參考。"
    )

    # === 基本收入資訊 ===

    # 1. 月收入範圍（單選）
    survey.add_question(
        question_type="single_choice",
        question_text="您目前的平均月收入大約是多少？",
        options=[
            "20,000元以下",
            "20,000-40,000元",
            "40,000-60,000元",
            "60,000-80,000元",
            "80,000-100,000元",
            "100,000元以上"
        ],
        required=True
    )

    # 2. 收入來源（多選）
    survey.add_question(
        question_type="multiple_choice",
        question_text="您的收入主要來自哪些方面？（可複選）",
        options=[
            "固定薪資",
            "兼職工作",
            "自營事業",
            "投資收益",
            "獎學金或助學金",
            "家庭支持",
            "租金收入",
            "其他收入"
        ],
        required=True
    )

    # 3. 收入穩定性（單選）
    survey.add_question(
        question_type="single_choice",
        question_text="您認為自己的收入狀況如何？",
        options=[
            "非常穩定，每月固定",
            "較為穩定，略有波動",
            "不太穩定，波動較大",
            "很不穩定，收入不確定"
        ],
        required=True
    )

    # === 支出狀況 ===

    # 4. 月支出範圍（單選）
    survey.add_question(
        question_type="single_choice",
        question_text="您平均每月的總支出大約是多少？",
        options=[
            "10,000元以下",
            "10,000-20,000元",
            "20,000-30,000元",
            "30,000-40,000元",
            "40,000-50,000元",
            "50,000元以上"
        ],
        required=True
    )

    # 5. 主要支出項目（多選）
    survey.add_question(
        question_type="multiple_choice",
        question_text="您每月的主要支出項目有哪些？（可複選）",
        options=[
            "房租或房貸",
            "飲食開銷",
            "交通費用",
            "學習進修",
            "休閒娛樂",
            "醫療保健",
            "家庭開銷",
            "儲蓄投資"
        ],
        required=True
    )

    # 6. 最大支出項目（開放式）
    survey.add_question(
        question_type="text",
        question_text="您每月最大的支出項目是什麼？為什麼？",
        options=None,
        required=False
    )

    # === 儲蓄與投資 ===

    # 7. 儲蓄習慣（單選）
    survey.add_question(
        question_type="single_choice",
        question_text="您每月大約能存下收入的多少比例？",
        options=[
            "幾乎無法儲蓄",
            "10%以下",
            "10%-20%",
            "20%-30%",
            "30%-40%",
            "40%以上"
        ],
        required=True
    )

    # 8. 投資方式（多選）
    survey.add_question(
        question_type="multiple_choice",
        question_text="您目前有進行哪些投資或理財？（可複選）",
        options=[
            "銀行定存",
            "股票",
            "基金",
            "債券",
            "房地產",
            "保險",
            "加密貨幣",
            "目前沒有投資"
        ],
        required=True
    )

    # === 財務壓力與滿意度 ===

    # 9. 財務壓力（評分）
    survey.add_question(
        question_type="rating",
        question_text="您目前的財務壓力有多大？（1分=無壓力，5分=壓力非常大）",
        options=None,
        required=True
    )

    # 10. 收入滿意度（評分）
    survey.add_question(
        question_type="rating",
        question_text="您對目前的收入水平滿意嗎？（1分=非常不滿意，5分=非常滿意）",
        options=None,
        required=True
    )

    # 11. 財務安全感（單選）
    survey.add_question(
        question_type="single_choice",
        question_text="您覺得自己的財務狀況是否足以應付突發開銷？",
        options=[
            "完全足夠，有充足緊急預備金",
            "基本足夠，有一些存款",
            "勉強足夠，存款不多",
            "不太足夠，擔心突發狀況",
            "完全不足，經常入不敷出"
        ],
        required=True
    )

    # === 未來規劃 ===

    # 12. 財務目標（多選）
    survey.add_question(
        question_type="multiple_choice",
        question_text="您未來1-3年的主要財務目標是什麼？（可複選）",
        options=[
            "增加收入",
            "累積存款",
            "購買房產",
            "投資理財",
            "創業",
            "進修學習",
            "出國旅遊",
            "退休規劃"
        ],
        required=True
    )

    # 13. 期望收入（開放式）
    survey.add_question(
        question_type="text",
        question_text="您希望未來的月收入達到多少？為什麼？",
        options=None,
        required=False
    )

    # 14. 理財困擾（開放式）
    survey.add_question(
        question_type="text",
        question_text="在收入和理財方面，您目前遇到最大的困擾或挑戰是什麼？",
        options=None,
        required=False
    )

    # 15. 建議與期待（開放式）
    survey.add_question(
        question_type="text",
        question_text="您希望社區能提供哪些財務相關的服務或協助？",
        options=None,
        required=False
    )

    print(f"✓ 問卷創建完成：{survey.title}")
    print(f"  問卷ID: {survey.survey_id}")
    print(f"  問題數量: {len(survey.questions)}")

    return survey


def main():
    """主函數"""
    print("=" * 70)
    print("創建收入調查問卷並讓AI居民填寫")
    print("=" * 70)
    print()

    # 創建問卷管理器
    manager = SurveyManager()

    # 創建收入問卷
    survey = create_income_survey()

    # 儲存問卷
    if manager.save_survey(survey):
        print("✓ 問卷已成功儲存")
    else:
        print("✗ 問卷儲存失敗")
        return

    print()
    print("-" * 70)
    print("開始讓AI居民填寫問卷...")
    print("-" * 70)
    print()

    # 創建AI填寫器（純 Ollama LLM 模式）
    simulation_md_path = "results/compressed/test_0513/simulation.md"
    filler = AIResidentSurveyFiller(
        survey_manager=manager,
        simulation_md_path=simulation_md_path
    )

    # 讓所有AI居民填寫問卷（使用 Ollama LLM 生成所有回答）
    try:
        responses = filler.fill_survey_for_all_residents(survey.survey_id)

        print()
        print("=" * 70)
        print("問卷填寫完成！")
        print("=" * 70)
        print()
        print(f"✓ 總共收集到 {len(responses)} 份回應")
        print()
        print("查看結果：")
        print(f"1. 問卷詳情：http://localhost:5001/surveys/{survey.survey_id}")
        print(f"2. 數據分析：http://localhost:5001/surveys/{survey.survey_id}/analytics")
        print()
        print("=" * 70)

    except Exception as e:
        print(f"✗ 填寫過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
