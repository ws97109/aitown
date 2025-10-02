"""
問卷匯入器
支援從多種來源匯入問卷：Google Forms、JSON格式、URL等
"""

import json
import re
import requests
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse, parse_qs
from .models import Survey


class BaseImporter:
    """基礎匯入器類別"""
    
    def import_survey(self, source: str) -> Optional[Survey]:
        """匯入問卷的抽象方法"""
        raise NotImplementedError


class JSONImporter(BaseImporter):
    """JSON格式問卷匯入器"""
    
    def import_survey(self, json_data: str) -> Optional[Survey]:
        """從JSON字符串匯入問卷"""
        try:
            data = json.loads(json_data) if isinstance(json_data, str) else json_data
            return self._parse_json_survey(data)
        except Exception as e:
            print(f"JSON匯入失敗: {e}")
            return None
    
    def import_from_file(self, file_path: str) -> Optional[Survey]:
        """從JSON文件匯入問卷"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return self._parse_json_survey(data)
        except Exception as e:
            print(f"文件匯入失敗: {e}")
            return None
    
    def _parse_json_survey(self, data: Dict) -> Survey:
        """解析JSON數據為Survey對象"""
        survey = Survey(
            title=data.get("title", "未命名問卷"),
            description=data.get("description", "")
        )
        
        questions = data.get("questions", [])
        for q in questions:
            question_type = q.get("type", "text")
            question_text = q.get("text", q.get("question", ""))
            options = q.get("options", q.get("choices", []))
            required = q.get("required", True)
            
            # 標準化問題類型
            if question_type in ["choice", "radio", "single_choice"]:
                question_type = "single_choice"
            elif question_type in ["checkbox", "multiple_choice"]:
                question_type = "multiple_choice"
            elif question_type in ["scale", "rating"]:
                question_type = "rating"
            elif question_type in ["short_answer", "paragraph", "text"]:
                question_type = "text"
            
            survey.add_question(question_type, question_text, options, required)
        
        return survey


class GoogleFormsImporter(BaseImporter):
    """Google Forms匯入器"""
    
    def import_survey(self, url_or_id: str) -> Optional[Survey]:
        """從Google Forms URL或ID匯入問卷"""
        try:
            # 提取Google Forms ID
            form_id = self._extract_form_id(url_or_id)
            if not form_id:
                print("無法識別Google Forms ID")
                return None
            
            # 嘗試從公開回應頁面提取問卷結構
            return self._import_from_viewform(form_id)
            
        except Exception as e:
            print(f"Google Forms匯入失敗: {e}")
            return None
    
    def _extract_form_id(self, url_or_id: str) -> Optional[str]:
        """提取Google Forms ID"""
        # 如果直接是ID
        if re.match(r'^[a-zA-Z0-9-_]{44}$', url_or_id):
            return url_or_id
        
        # 從URL提取ID
        patterns = [
            r'/forms/d/([a-zA-Z0-9-_]{44})',
            r'forms\.gle/([a-zA-Z0-9-_]{44})',
            r'viewform\?id=([a-zA-Z0-9-_]{44})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url_or_id)
            if match:
                return match.group(1)
        
        return None
    
    def _import_from_viewform(self, form_id: str) -> Optional[Survey]:
        """從viewform頁面解析問卷結構（有限支援）"""
        try:
            # 構建viewform URL
            viewform_url = f"https://docs.google.com/forms/d/{form_id}/viewform"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(viewform_url, headers=headers, timeout=10)
            if response.status_code != 200:
                print(f"無法訪問Google Forms: {response.status_code}")
                return None
            
            html_content = response.text
            return self._parse_html_content(html_content, form_id)
            
        except Exception as e:
            print(f"解析Google Forms失敗: {e}")
            return None
    
    def _parse_html_content(self, html_content: str, form_id: str) -> Survey:
        """解析HTML內容提取問卷信息（簡化版）"""
        survey = Survey(survey_id=f"gf_{form_id}")
        
        # 嘗試提取標題
        title_match = re.search(r'<title>(.*?)</title>', html_content)
        if title_match:
            survey.title = title_match.group(1).replace(' - Google 표單', '').strip()
        else:
            survey.title = "Google Forms 問卷"
        
        # 由於Google Forms的動態載入特性，HTML解析有限
        # 這裡提供一個基本的示例結構
        print("注意：Google Forms自動解析功能有限，建議手動創建問卷")
        
        # 添加示例問題（實際使用時應根據實際需求調整）
        survey.add_question("text", "請提供您的基本信息", [], True)
        survey.add_question("single_choice", "您對此服務的滿意度？", 
                          ["非常滿意", "滿意", "普通", "不滿意", "非常不滿意"], True)
        survey.add_question("multiple_choice", "您希望改進的方面？（可多選）", 
                          ["服務質量", "響應速度", "用戶界面", "功能完整性"], False)
        survey.add_question("rating", "總體評分（1-5分）", [], True)
        
        return survey


class URLImporter(BaseImporter):
    """通用URL匯入器"""
    
    def import_survey(self, url: str) -> Optional[Survey]:
        """從URL匯入問卷"""
        try:
            # 判斷URL類型
            if 'forms.gle' in url or 'docs.google.com/forms' in url:
                return GoogleFormsImporter().import_survey(url)
            
            # 其他URL類型的處理
            return self._import_from_generic_url(url)
            
        except Exception as e:
            print(f"URL匯入失敗: {e}")
            return None
    
    def _import_from_generic_url(self, url: str) -> Optional[Survey]:
        """從通用URL匯入問卷（嘗試獲取JSON數據）"""
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                return None
            
            # 嘗試解析為JSON
            try:
                data = response.json()
                return JSONImporter().import_survey(data)
            except:
                pass
            
            # 如果不是JSON，返回空問卷
            survey = Survey(title="從URL匯入的問卷")
            survey.add_question("text", "這是從URL匯入的示例問題", [], True)
            return survey
            
        except Exception as e:
            print(f"通用URL匯入失敗: {e}")
            return None


class SurveyImportManager:
    """問卷匯入管理器"""
    
    def __init__(self):
        self.importers = {
            'json': JSONImporter(),
            'google_forms': GoogleFormsImporter(), 
            'url': URLImporter()
        }
    
    def import_survey(self, source: str, source_type: str = 'auto') -> Optional[Survey]:
        """統一的問卷匯入接口"""
        if source_type == 'auto':
            source_type = self._detect_source_type(source)
        
        importer = self.importers.get(source_type)
        if not importer:
            print(f"不支援的匯入類型: {source_type}")
            return None
        
        return importer.import_survey(source)
    
    def _detect_source_type(self, source: str) -> str:
        """自動檢測來源類型"""
        if source.startswith(('http://', 'https://')):
            if 'forms.gle' in source or 'docs.google.com/forms' in source:
                return 'google_forms'
            else:
                return 'url'
        
        # 嘗試解析為JSON
        try:
            json.loads(source)
            return 'json'
        except:
            pass
        
        # 檢查是否是文件路徑
        if source.endswith('.json'):
            return 'json'
        
        # 預設為URL
        return 'url'
    
    def create_sample_survey(self) -> Survey:
        """創建示例問卷"""
        survey = Survey(title="AI居民滿意度調查", description="針對虛擬社區AI居民的滿意度調查")
        
        # 基本信息
        survey.add_question("text", "請問您的姓名？", [], True)
        survey.add_question("single_choice", "您的年齡層？", 
                          ["18-25歲", "26-35歲", "36-45歲", "46-55歲", "56歲以上"], True)
        
        # 滿意度評估
        survey.add_question("single_choice", "您對目前的生活環境滿意嗎？", 
                          ["非常滿意", "滿意", "普通", "不滿意", "非常不滿意"], True)
        survey.add_question("rating", "請為社區的整體氛圍評分（1-5分）", [], True)
        
        # 多選題
        survey.add_question("multiple_choice", "您最常參與的活動有？（可多選）", 
                          ["社交聊天", "學習研究", "休閒娛樂", "工作討論", "其他"], False)
        
        # 開放題
        survey.add_question("text", "您對社區有什麼建議或意見？", [], False)
        
        return survey