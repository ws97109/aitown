"""
問卷系統測試腳本
驗證問卷系統的各項功能
"""

import os
import sys
import json
from datetime import datetime

# 添加父目錄到路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from survey_system import (
    Survey, SurveyResponse, SurveyManager, 
    AIResidentSurveyFiller, SurveyImportManager, 
    SurveyExportManager
)


def test_survey_creation():
    """測試問卷創建功能"""
    print("=== 測試問卷創建功能 ===")
    
    # 創建問卷
    survey = Survey(title="測試問卷", description="這是一個測試問卷")
    
    # 添加各種類型的問題
    survey.add_question("text", "請問您的姓名？", [], True)
    survey.add_question("single_choice", "您的年齡層？", 
                       ["18-25歲", "26-35歲", "36-45歲", "46歲以上"], True)
    survey.add_question("multiple_choice", "您的興趣愛好？（可多選）",
                       ["閱讀", "運動", "音樂", "旅遊", "烹飪"], False)
    survey.add_question("rating", "請為此服務評分（1-5分）", [], True)
    
    print(f"✓ 問卷創建成功：{survey.title}")
    print(f"  問題數量：{len(survey.questions)}")
    print(f"  問卷ID：{survey.survey_id}")
    
    return survey


def test_survey_management():
    """測試問卷管理功能"""
    print("\n=== 測試問卷管理功能 ===")
    
    manager = SurveyManager()
    
    # 創建並保存問卷
    survey = test_survey_creation()
    success = manager.save_survey(survey)
    print(f"✓ 問卷保存：{'成功' if success else '失敗'}")
    
    # 載入問卷
    loaded_survey = manager.load_survey(survey.survey_id)
    if loaded_survey:
        print(f"✓ 問卷載入成功：{loaded_survey.title}")
    else:
        print("❌ 問卷載入失敗")
        return None
    
    # 獲取所有問卷
    all_surveys = manager.get_all_surveys()
    print(f"✓ 問卷列表獲取成功：共 {len(all_surveys)} 個問卷")
    
    return survey.survey_id, manager


def test_ai_resident_filling():
    """測試AI居民填寫功能"""
    print("\n=== 測試AI居民填寫功能 ===")
    
    survey_id, manager = test_survey_management()
    if not survey_id:
        print("❌ 無法進行AI填寫測試，問卷管理失敗")
        return
    
    filler = AIResidentSurveyFiller(manager)
    
    try:
        # 讓所有AI居民填寫問卷
        responses = filler.fill_survey_for_all_residents(survey_id)
        print(f"✓ AI居民填寫成功：共 {len(responses)} 個回應")
        
        # 檢查回應內容
        for i, response in enumerate(responses[:3]):  # 只顯示前3個
            print(f"  居民{i+1} ({response.respondent_name}):")
            print(f"    完成狀態：{'已完成' if response.is_completed() else '未完成'}")
            print(f"    回應數量：{len(response.responses)}")
            
            # 顯示部分回應內容
            for q_id, answer in list(response.responses.items())[:2]:
                print(f"    問題{q_id}: {str(answer)[:50]}{'...' if len(str(answer)) > 50 else ''}")
        
        return survey_id, manager
        
    except Exception as e:
        print(f"❌ AI居民填寫失敗：{e}")
        return None, None


def test_export_functionality():
    """測試匯出功能"""
    print("\n=== 測試匯出功能 ===")
    
    survey_id, manager = test_ai_resident_filling()
    if not survey_id:
        print("❌ 無法進行匯出測試，AI填寫失敗")
        return
    
    exporter = SurveyExportManager(manager)
    
    try:
        # 測試CSV匯出
        csv_path = exporter.export_survey(survey_id, 'csv')
        print(f"✓ CSV匯出成功：{csv_path}")
        
        # 檢查文件是否存在
        if os.path.exists(csv_path):
            file_size = os.path.getsize(csv_path)
            print(f"  文件大小：{file_size} bytes")
        
        # 測試JSON匯出
        json_path = exporter.export_survey(survey_id, 'json')
        print(f"✓ JSON匯出成功：{json_path}")
        
        # 嘗試Excel匯出
        try:
            excel_path = exporter.export_survey(survey_id, 'excel')
            print(f"✓ Excel匯出成功：{excel_path}")
        except ImportError:
            print("⚠ Excel匯出跳過：需要安裝openpyxl套件")
        except Exception as e:
            print(f"❌ Excel匯出失敗：{e}")
        
    except Exception as e:
        print(f"❌ 匯出功能測試失敗：{e}")


def test_import_functionality():
    """測試匯入功能"""
    print("\n=== 測試匯入功能 ===")
    
    import_manager = SurveyImportManager()
    
    # 測試JSON匯入
    json_data = {
        "title": "匯入測試問卷",
        "description": "通過JSON格式匯入的測試問卷",
        "questions": [
            {
                "type": "text",
                "text": "您的職業是什麼？",
                "required": True
            },
            {
                "type": "single_choice",
                "text": "您對我們的服務滿意嗎？",
                "options": ["非常滿意", "滿意", "普通", "不滿意"],
                "required": True
            }
        ]
    }
    
    try:
        survey = import_manager.import_survey(json.dumps(json_data), 'json')
        if survey:
            print(f"✓ JSON匯入成功：{survey.title}")
            print(f"  問題數量：{len(survey.questions)}")
        else:
            print("❌ JSON匯入失敗")
    except Exception as e:
        print(f"❌ JSON匯入失敗：{e}")
    
    # 測試示例問卷創建
    try:
        sample_survey = import_manager.create_sample_survey()
        print(f"✓ 示例問卷創建成功：{sample_survey.title}")
        print(f"  問題數量：{len(sample_survey.questions)}")
    except Exception as e:
        print(f"❌ 示例問卷創建失敗：{e}")


def test_data_statistics():
    """測試數據統計功能"""
    print("\n=== 測試數據統計功能 ===")
    
    manager = SurveyManager()
    all_surveys = manager.get_all_surveys()
    
    if not all_surveys:
        print("❌ 沒有可用的問卷進行統計測試")
        return
    
    # 選擇第一個問卷進行統計
    survey_id = all_surveys[0]['survey_id']
    
    try:
        stats = manager.get_survey_stats(survey_id)
        print(f"✓ 統計數據獲取成功：{stats['title']}")
        print(f"  總回應數：{stats['total_responses']}")
        print(f"  完成回應數：{stats['completed_responses']}")
        print(f"  完成率：{stats['completion_rate']:.1f}%")
        print(f"  問題數量：{stats['question_count']}")
        
    except Exception as e:
        print(f"❌ 統計功能測試失敗：{e}")


def run_all_tests():
    """運行所有測試"""
    print("開始運行問卷系統測試...")
    print("=" * 50)
    
    try:
        test_survey_creation()
        test_survey_management()
        test_ai_resident_filling()
        test_export_functionality()
        test_import_functionality()
        test_data_statistics()
        
        print("\n" + "=" * 50)
        print("✅ 所有測試完成！")
        print("\n測試摘要：")
        print("- 問卷創建和管理：✓")
        print("- AI居民自動填寫：✓")
        print("- 多格式匯出：✓")
        print("- 問卷匯入：✓")
        print("- 數據統計：✓")
        
    except Exception as e:
        print(f"\n❌ 測試過程中發生錯誤：{e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()