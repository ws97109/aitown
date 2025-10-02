"""
AI居民問卷填寫器
根據AI居民的特性和背景自動填寫問卷
"""

import sys
import os
import json
import random
from typing import Dict, List, Any, Optional

# 添加父目錄到路徑，以便導入遊戲模組
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .models import Survey, SurveyResponse, SurveyManager


class AIResidentSurveyFiller:
    """AI居民問卷填寫器"""
    
    def __init__(self, survey_manager: SurveyManager):
        self.survey_manager = survey_manager
        self.game = None
        
        # 動態載入AI居民基本信息
        self.residents_info = self._load_residents_info()
    
    def _load_residents_info(self) -> Dict[str, Dict]:
        """動態載入AI居民信息"""
        try:
            # 嘗試從agent配置文件載入
            agents_path = "../frontend/static/assets/village/agents"
            if not os.path.exists(agents_path):
                agents_path = "frontend/static/assets/village/agents"
            
            residents_info = {}
            
            if os.path.exists(agents_path):
                for agent_dir in os.listdir(agents_path):
                    agent_config_path = os.path.join(agents_path, agent_dir, "agent.json")
                    if os.path.exists(agent_config_path):
                        try:
                            with open(agent_config_path, "r", encoding="utf-8") as f:
                                agent_config = json.load(f)
                            
                            agent_name = agent_dir.replace("_", " ")
                            residents_info[agent_name] = {
                                "age": agent_config.get("age", 25),
                                "personality": agent_config.get("personality", []),
                                "interests": agent_config.get("interests", []),
                                "lifestyle": agent_config.get("lifestyle", ""),
                                "current_activity": agent_config.get("current_activity", "")
                            }
                        except json.JSONDecodeError:
                            print(f"無法解析 {agent_config_path}")
                            continue
            
            # 如果無法從配置載入，使用預設值
            if not residents_info:
                residents_info = self._get_default_residents_info()
            
            return residents_info
            
        except Exception as e:
            print(f"載入AI居民信息失敗: {e}")
            return self._get_default_residents_info()
    
    def _get_default_residents_info(self) -> Dict[str, Dict]:
        """獲取預設的AI居民信息"""
        return {
            "盧品蓉": {
                "age": 20,
                "personality": ["友善", "樂於助人", "社交活躍"],
                "interests": ["溝通", "組織活動", "社團參與"],
                "lifestyle": "外向社交型",
                "current_activity": "準備期末考試"
            },
            "鄭傑丞": {
                "age": 21, 
                "personality": ["認真負責", "注重細節", "理性思考"],
                "interests": ["程式設計", "數據分析", "技術研究"],
                "lifestyle": "規律學習型",
                "current_activity": "實習專案開發"
            },
            "莊于萱": {
                "age": 19,
                "personality": ["創意豐富", "藝術天賦", "自由奔放"],
                "interests": ["繪畫", "設計", "攝影", "藝術創作"],
                "lifestyle": "藝術創作型", 
                "current_activity": "準備藝術展覽"
            },
            "施宇鴻": {
                "age": 22,
                "personality": ["邏輯思維", "冷靜理性", "深度思考"],
                "interests": ["工程技術", "問題解決", "研究分析"],
                "lifestyle": "獨立研究型",
                "current_activity": "研究項目進行"
            },
            "游庭瑄": {
                "age": 45,
                "personality": ["博學多聞", "循循善誘", "關愛學生"],
                "interests": ["教學", "學術研究", "知識分享"],
                "lifestyle": "教育工作型",
                "current_activity": "指導學生論文"
            },
            "李昇峰": {
                "age": 50,
                "personality": ["細心專業", "服務至上", "穩重可靠"],
                "interests": ["藥學專業", "健康諮詢", "家庭照顧"],
                "lifestyle": "專業服務型",
                "current_activity": "管理藥店業務"
            },
            "魏祺紘": {
                "age": 18,
                "personality": ["活潑好動", "求知慾強", "適應力強"],
                "interests": ["快速學習", "新事物探索", "青春活動"],
                "lifestyle": "青春探索型",
                "current_activity": "適應大學生活"
            },
            "陳冠佑": {
                "age": 35,
                "personality": ["健談幽默", "善於交際", "夜生活活躍"],
                "interests": ["調酒技藝", "人際溝通", "娛樂活動"],
                "lifestyle": "社交服務型",
                "current_activity": "經營酒吧生意"
            },
            "蔡宗陞": {
                "age": 28,
                "personality": ["溫和親切", "追求品質", "注重細節"],
                "interests": ["咖啡製作", "店面管理", "生活品味"],
                "lifestyle": "品質生活型",
                "current_activity": "研發咖啡配方"
            }
        }
    
    def set_game_context(self):
        """設置遊戲環境（如果可用）"""
        try:
            from modules.game import get_game
            self.game = get_game()
        except Exception as e:
            print(f"無法載入遊戲環境: {e}")
            self.game = None
    
    def fill_survey_for_all_residents(self, survey_id: str) -> List[SurveyResponse]:
        """讓所有AI居民填寫問卷"""
        survey = self.survey_manager.load_survey(survey_id)
        if not survey:
            raise ValueError(f"問卷 {survey_id} 不存在")
        
        self.set_game_context()
        responses = []
        
        for resident_name, resident_info in self.residents_info.items():
            print(f"正在生成 {resident_name} 的問卷回應...")
            response = self._generate_resident_response(survey, resident_name, resident_info)
            
            if response:
                self.survey_manager.save_response(response)
                responses.append(response)
                print(f"✓ {resident_name} 的回應已生成並保存")
        
        return responses
    
    def fill_survey_for_resident(self, survey_id: str, resident_name: str) -> Optional[SurveyResponse]:
        """讓特定AI居民填寫問卷"""
        survey = self.survey_manager.load_survey(survey_id)
        if not survey:
            raise ValueError(f"問卷 {survey_id} 不存在")
        
        resident_info = self.residents_info.get(resident_name)
        if not resident_info:
            raise ValueError(f"AI居民 {resident_name} 不存在")
        
        self.set_game_context()
        response = self._generate_resident_response(survey, resident_name, resident_info)
        
        if response:
            self.survey_manager.save_response(response)
            print(f"✓ {resident_name} 的回應已生成並保存")
        
        return response
    
    def _generate_resident_response(self, survey: Survey, resident_name: str, 
                                  resident_info: Dict) -> SurveyResponse:
        """為特定居民生成問卷回應"""
        response = SurveyResponse(survey.survey_id, resident_name)
        
        for question in survey.questions:
            answer = self._generate_answer(question, resident_name, resident_info)
            response.add_response(question["id"], answer)
        
        response.complete()
        return response
    
    def _generate_answer(self, question: Dict, resident_name: str, 
                        resident_info: Dict) -> Any:
        """根據問題類型和居民特性生成答案"""
        question_type = question["type"]
        question_text = question["text"].lower()
        options = question.get("options", [])
        
        if question_type == "single_choice":
            return self._generate_single_choice_answer(question_text, options, resident_name, resident_info)
        
        elif question_type == "multiple_choice":
            return self._generate_multiple_choice_answer(question_text, options, resident_name, resident_info)
        
        elif question_type == "rating":
            return self._generate_rating_answer(question_text, resident_name, resident_info)
        
        elif question_type == "text":
            return self._generate_text_answer(question_text, resident_name, resident_info)
        
        return "未知問題類型"
    
    def _generate_single_choice_answer(self, question_text: str, options: List[str], 
                                     resident_name: str, resident_info: Dict) -> str:
        """生成單選題答案"""
        if not options:
            return "無選項"
        
        # 基於居民特性的智能選擇
        personality = resident_info.get("personality", [])
        interests = resident_info.get("interests", [])
        age = resident_info.get("age", 25)
        
        # 年齡相關問題
        if "年齡" in question_text or "age" in question_text:
            for option in options:
                if self._age_matches_option(age, option):
                    return option
        
        # 滿意度相關問題
        if any(word in question_text for word in ["滿意", "satisfaction", "happy", "開心"]):
            if "友善" in personality or "樂於助人" in personality:
                return self._choose_positive_option(options, 0.8)
            elif "冷靜理性" in personality:
                return self._choose_moderate_option(options)
            else:
                return self._choose_positive_option(options, 0.6)
        
        # 活動參與相關
        if any(word in question_text for word in ["參與", "活動", "participate", "activity"]):
            if "社交活躍" in personality or "健談幽默" in personality:
                return self._choose_active_option(options)
            elif "獨立研究型" in resident_info.get("lifestyle", ""):
                return self._choose_passive_option(options)
        
        # 基於興趣選擇
        for interest in interests:
            for option in options:
                if any(keyword in option.lower() for keyword in interest.lower().split()):
                    return option
        
        # 使用名字hash保證一致性
        name_hash = hash(resident_name + question_text) % len(options)
        return options[name_hash]
    
    def _generate_multiple_choice_answer(self, question_text: str, options: List[str],
                                       resident_name: str, resident_info: Dict) -> List[str]:
        """生成多選題答案"""
        if not options:
            return []
        
        selected = []
        interests = resident_info.get("interests", [])
        personality = resident_info.get("personality", [])
        
        # 基於興趣匹配選項
        for option in options:
            option_lower = option.lower()
            
            # 直接興趣匹配
            for interest in interests:
                if any(keyword in option_lower for keyword in interest.lower().split()):
                    selected.append(option)
                    break
        
        # 基於性格匹配
        if "社交" in question_text or "活動" in question_text:
            social_keywords = ["聊天", "交流", "社交", "討論", "分享"]
            if any(p in ["友善", "健談幽默", "社交活躍"] for p in personality):
                for option in options:
                    if any(keyword in option for keyword in social_keywords) and option not in selected:
                        selected.append(option)
        
        # 確保至少選擇一個，最多選擇一半
        if not selected:
            name_hash = hash(resident_name + question_text)
            selected.append(options[name_hash % len(options)])
        
        max_selections = min(3, len(options) // 2 + 1)
        return selected[:max_selections]
    
    def _generate_rating_answer(self, question_text: str, resident_name: str, 
                              resident_info: Dict) -> int:
        """生成評分答案（1-5分）"""
        personality = resident_info.get("personality", [])
        
        # 基於性格給出不同傾向的評分
        if "友善" in personality or "樂於助人" in personality:
            # 友善的人傾向給較高分
            base_score = 4
        elif "注重細節" in personality or "認真負責" in personality:
            # 嚴謹的人傾向給中等偏上分數
            base_score = 3
        elif "冷靜理性" in personality:
            # 理性的人給分較為客觀
            base_score = 3
        else:
            base_score = 3
        
        # 滿意度相關問題給分較高
        if any(word in question_text for word in ["滿意", "satisfaction", "推薦", "recommend"]):
            base_score = min(5, base_score + 1)
        
        # 添加一些隨機性，但保持一致性
        name_hash = hash(resident_name + question_text) % 3 - 1  # -1, 0, 1
        final_score = max(1, min(5, base_score + name_hash))
        
        return final_score
    
    def _generate_text_answer(self, question_text: str, resident_name: str, 
                            resident_info: Dict) -> str:
        """生成文字回應"""
        personality = resident_info.get("personality", [])
        interests = resident_info.get("interests", [])
        current_activity = resident_info.get("current_activity", "")
        
        # 基於問題類型生成不同風格的回應
        if "建議" in question_text or "意見" in question_text or "suggestion" in question_text:
            return self._generate_suggestion_response(resident_name, resident_info)
        
        elif "經驗" in question_text or "experience" in question_text:
            return self._generate_experience_response(resident_name, resident_info)
        
        elif "感受" in question_text or "feeling" in question_text:
            return self._generate_feeling_response(resident_name, resident_info)
        
        elif "未來" in question_text or "future" in question_text or "計劃" in question_text:
            return self._generate_future_response(resident_name, resident_info)
        
        else:
            return self._generate_general_response(resident_name, resident_info, question_text)
    
    def _generate_suggestion_response(self, resident_name: str, resident_info: Dict) -> str:
        """生成建議類回應"""
        personality = resident_info.get("personality", [])
        interests = resident_info.get("interests", [])
        
        if "教學" in interests:
            return f"身為{resident_name}，我建議可以增加更多學習和知識分享的機會，讓大家能夠互相學習成長。"
        elif "技術研究" in interests or "程式設計" in interests:
            return f"從技術角度來看，我認為可以導入更多數位化工具來提升效率和體驗。"
        elif "藝術創作" in interests:
            return f"希望能有更多創意和藝術相關的活動空間，讓大家發揮創造力。"
        elif "社交活躍" in personality:
            return f"我覺得可以多辦一些社交活動，增進大家的互動和友誼。"
        else:
            return f"作為{resident_name}，我希望能夠持續改善現有的環境，讓每個人都能找到適合自己的位置。"
    
    def _generate_experience_response(self, resident_name: str, resident_info: Dict) -> str:
        """生成經驗分享回應"""
        current_activity = resident_info.get("current_activity", "")
        interests = resident_info.get("interests", [])
        
        experience_templates = [
            f"在{current_activity}的過程中，我學到了很多寶貴的經驗。",
            f"我在{interests[0] if interests else '日常生活'}方面有一些心得可以分享。",
            f"最近的{current_activity}讓我對生活有了新的理解。"
        ]
        
        return random.choice(experience_templates)
    
    def _generate_feeling_response(self, resident_name: str, resident_info: Dict) -> str:
        """生成感受類回應"""
        personality = resident_info.get("personality", [])
        
        if "友善" in personality:
            return "我對目前的環境感到很溫暖，大家都很友善，讓我覺得很舒適。"
        elif "冷靜理性" in personality:
            return "客觀來說，整體環境還不錯，有一些可以改進的地方，但總的來說是正面的。"
        elif "活潑好動" in personality:
            return "我覺得這裡很有活力！每天都有新鮮的事物，讓我充滿期待。"
        else:
            return "總的來說，我對現狀還算滿意，希望能夠持續保持這樣的氛圍。"
    
    def _generate_future_response(self, resident_name: str, resident_info: Dict) -> str:
        """生成未來展望回應"""
        interests = resident_info.get("interests", [])
        
        future_templates = [
            f"未來我希望在{interests[0] if interests else '個人成長'}方面能有更多發展。",
            f"我計劃繼續深入{interests[0] if interests else '自己感興趣的領域'}，為社區貢獻更多價值。",
            "希望未來能夠看到更多正向的改變，讓每個人都能實現自己的目標。"
        ]
        
        return random.choice(future_templates)
    
    def _generate_general_response(self, resident_name: str, resident_info: Dict, 
                                 question_text: str) -> str:
        """生成一般性回應"""
        return f"作為{resident_name}，我認為這是一個很有意義的問題。基於我的經驗和觀察，我會認真考慮並給出我的想法。"
    
    # 輔助方法
    def _age_matches_option(self, age: int, option: str) -> bool:
        """檢查年齡是否匹配選項"""
        if "18-25" in option and 18 <= age <= 25:
            return True
        elif "26-35" in option and 26 <= age <= 35:
            return True
        elif "36-45" in option and 36 <= age <= 45:
            return True
        elif "46-55" in option and 46 <= age <= 55:
            return True
        elif "56" in option and age > 55:
            return True
        return False
    
    def _choose_positive_option(self, options: List[str], probability: float = 0.7) -> str:
        """選擇積極正面的選項"""
        positive_keywords = ["很好", "滿意", "非常", "excellent", "good", "滿意", "喜歡", "推薦"]
        
        positive_options = []
        for option in options:
            if any(keyword in option.lower() for keyword in positive_keywords):
                positive_options.append(option)
        
        if positive_options and random.random() < probability:
            return random.choice(positive_options)
        
        return random.choice(options)
    
    def _choose_moderate_option(self, options: List[str]) -> str:
        """選擇中等選項"""
        moderate_keywords = ["普通", "一般", "還可以", "尚可", "moderate", "average", "okay"]
        
        for option in options:
            if any(keyword in option.lower() for keyword in moderate_keywords):
                return option
        
        # 如果沒有明顯的中等選項，選擇中間位置的選項
        if len(options) >= 3:
            return options[len(options) // 2]
        
        return random.choice(options)
    
    def _choose_active_option(self, options: List[str]) -> str:
        """選擇積極活躍的選項"""
        active_keywords = ["參與", "積極", "主動", "經常", "喜歡", "participate", "active", "often"]
        
        for option in options:
            if any(keyword in option.lower() for keyword in active_keywords):
                return option
        
        return options[0] if options else ""
    
    def _choose_passive_option(self, options: List[str]) -> str:
        """選擇被動消極的選項"""
        passive_keywords = ["較少", "偶爾", "不太", "很少", "rarely", "sometimes", "not often"]
        
        for option in options:
            if any(keyword in option.lower() for keyword in passive_keywords):
                return option
        
        return options[-1] if options else ""