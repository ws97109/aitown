#!/usr/bin/env python3
"""
測試新的AI填寫功能 - 驗證回答更人性化
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from survey_system import Survey, SurveyManager, AIResidentSurveyFiller


def create_test_survey():
    """創建測試問卷 - 包含各種問題類型"""
    print("正在創建測試問卷...")

    survey = Survey(
        title="社區居民基本資料與生活調查",
        description="這是一份簡單的問卷，用來了解社區居民的基本資料和生活狀況。請誠實回答每個問題。"
    )

    # 簡單個人信息問題
    survey.add_question(
        question_type="text",
        question_text="請問您的姓名是？",
        options=None,
        required=True
    )

    survey.add_question(
        question_type="text",
        question_text="您今年幾歲？",
        options=None,
        required=True
    )

    survey.add_question(
        question_type="text",
        question_text="請問您的職業是什麼？",
        options=None,
        required=True
    )

    # 選擇題
    survey.add_question(
        question_type="single_choice",
        question_text="您平常最喜歡的休閒活動是？",
        options=[
            "運動健身",
            "閱讀學習",
            "看電影追劇",
            "與朋友聚會",
            "藝術創作",
            "其他"
        ],
        required=True
    )

    # 多選題
    survey.add_question(
        question_type="multiple_choice",
        question_text="您希望社區能提供哪些設施或服務？（可複選）",
        options=[
            "健身房",
            "圖書室",
            "咖啡廳",
            "會議室",
            "藝術工作坊",
            "休閒娛樂區",
            "學習進修課程"
        ],
        required=True
    )

    # 評分題
    survey.add_question(
        question_type="rating",
        question_text="您對目前的生活環境滿意嗎？（1分=非常不滿意，5分=非常滿意）",
        options=None,
        required=True
    )

    # 開放性問題 - 經驗分享
    survey.add_question(
        question_type="text",
        question_text="請分享一下您在工作或學習上的經驗與心得。",
        options=None,
        required=False
    )

    # 開放性問題 - 感受
    survey.add_question(
        question_type="text",
        question_text="您對社區生活有什麼感受或看法？",
        options=None,
        required=False
    )

    # 開放性問題 - 未來
    survey.add_question(
        question_type="text",
        question_text="談談您對未來的規劃和期待。",
        options=None,
        required=False
    )

    # 開放性問題 - 建議
    survey.add_question(
        question_type="text",
        question_text="您對社區發展有什麼建議嗎？",
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
    print("測試新的AI填寫功能 - 驗證回答更人性化")
    print("=" * 70)
    print()

    # 創建問卷管理器
    manager = SurveyManager()

    # 創建測試問卷
    survey = create_test_survey()

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

    # 創建AI填寫器
    filler = AIResidentSurveyFiller(manager)

    # 讓所有AI居民填寫問卷
    try:
        responses = filler.fill_survey_for_all_residents(survey.survey_id)

        print()
        print("=" * 70)
        print("問卷填寫完成！讓我們查看一些回答示例")
        print("=" * 70)
        print()

        # 顯示前3位居民的回答示例
        for i, response in enumerate(responses[:3], 1):
            print(f"\n【居民 {i}: {response.respondent_name}】")
            print("-" * 50)

            # 顯示姓名問題的回答
            if "1" in response.responses:
                print(f"Q1 (姓名): {response.responses['1']}")

            # 顯示年齡問題的回答
            if "2" in response.responses:
                print(f"Q2 (年齡): {response.responses['2']}")

            # 顯示職業問題的回答
            if "3" in response.responses:
                print(f"Q3 (職業): {response.responses['3']}")

            # 顯示經驗分享的回答
            if "7" in response.responses:
                print(f"Q7 (經驗): {response.responses['7']}")

            # 顯示感受的回答
            if "8" in response.responses:
                print(f"Q8 (感受): {response.responses['8']}")

        print()
        print("=" * 70)
        print("測試完成！")
        print("=" * 70)
        print(f"✓ 總共收集到 {len(responses)} 份回應")
        print()
        print("查看完整結果：")
        print(f"1. 訪問 http://localhost:5001/surveys/{survey.survey_id}")
        print(f"2. 訪問 http://localhost:5001/surveys/{survey.survey_id}/analytics")
        print()
        print("注意觀察：")
        print("- 姓名問題：直接回答姓名，不再有多餘的前綴")
        print("- 年齡問題：直接回答年齡，格式簡潔")
        print("- 職業問題：根據背景回答職業")
        print("- 開放問題：回答更自然、更口語化、更具體")
        print("=" * 70)

    except Exception as e:
        print(f"✗ 填寫過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
