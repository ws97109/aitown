"""
AI居民問卷填寫器 - 純 Ollama LLM 版本
所有回答均由 Ollama LLM 根據 agent.json 和 simulation.md 生成
不使用任何硬編碼或規則引擎
"""

import sys
import os
import json
from typing import Dict, List, Any, Optional

# 添加父目錄到路徑，以便導入遊戲模組
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .models import Survey, SurveyResponse, SurveyManager
from .ollama_generator import OllamaSurveyGenerator


class AIResidentSurveyFiller:
    """AI居民問卷填寫器 - 純 LLM 驅動，無硬編碼規則"""

    def __init__(self, survey_manager: SurveyManager, simulation_md_path: Optional[str] = None):
        """
        初始化AI居民問卷填寫器

        Args:
            survey_manager: 問卷管理器
            simulation_md_path: simulation.md文件路徑（包含活動歷史）
        """
        self.survey_manager = survey_manager
        self.game = None

        # 動態載入AI居民基本信息（用於列表和驗證）
        self.residents_info = self._load_residents_info()

        # 初始化Ollama生成器（必需）
        if not simulation_md_path:
            print("⚠️  警告：未提供 simulation_md_path，將無法使用活動歷史")

        self.ollama_generator = OllamaSurveyGenerator(simulation_md_path)
        print(f"✓ Ollama 生成器已初始化（純 LLM 模式，無硬編碼規則）")

    def _load_residents_info(self) -> Dict[str, Dict]:
        """
        動態載入AI居民基本信息
        僅用於獲取居民列表，不用於生成回答
        """
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

                            agent_name = agent_config.get("name", agent_dir)
                            scratch = agent_config.get("scratch", {})

                            # 僅保存基本信息用於列表顯示
                            residents_info[agent_name] = {
                                "age": scratch.get("age", 25),
                                "personality": scratch.get("innate", "").split("、") if scratch.get("innate") else [],
                                "current_activity": agent_config.get("currently", "")
                            }
                        except json.JSONDecodeError:
                            print(f"⚠️  無法解析 {agent_config_path}")
                            continue

            if not residents_info:
                print("❌ 未找到任何 AI 居民配置文件")
                print(f"   請確認路徑: {agents_path}")

            return residents_info

        except Exception as e:
            print(f"❌ 載入AI居民信息失敗: {e}")
            return {}

    def set_game_context(self):
        """設置遊戲上下文（保留接口兼容性）"""
        pass

    def fill_survey_for_all_residents(self, survey_id: str) -> List[SurveyResponse]:
        """
        讓所有AI居民填寫問卷
        使用純 Ollama LLM 生成所有回答

        Args:
            survey_id: 問卷ID

        Returns:
            所有居民的回應列表
        """
        survey = self.survey_manager.load_survey(survey_id)
        if not survey:
            raise ValueError(f"問卷 {survey_id} 不存在")

        print(f"\n📋 開始為所有居民填寫問卷: {survey.title}")
        print(f"   共 {len(self.residents_info)} 位居民")
        print(f"   問卷包含 {len(survey.questions)} 個問題")
        print(f"   使用 Ollama LLM 生成所有回答\n")

        responses = []
        for i, resident_name in enumerate(self.residents_info.keys(), 1):
            print(f"[{i}/{len(self.residents_info)}] 正在為 {resident_name} 生成回答...")

            try:
                response = self.fill_survey_for_resident(survey_id, resident_name)
                if response:
                    responses.append(response)
                    print(f"   ✓ {resident_name} 完成")
            except Exception as e:
                print(f"   ❌ {resident_name} 失敗: {e}")
                continue

        print(f"\n✅ 完成！成功生成 {len(responses)}/{len(self.residents_info)} 份問卷回應")
        return responses

    def fill_survey_for_resident(self, survey_id: str, resident_name: str) -> Optional[SurveyResponse]:
        """
        讓特定AI居民填寫問卷
        使用純 Ollama LLM 生成所有回答

        Args:
            survey_id: 問卷ID
            resident_name: 居民姓名

        Returns:
            問卷回應對象
        """
        survey = self.survey_manager.load_survey(survey_id)
        if not survey:
            raise ValueError(f"問卷 {survey_id} 不存在")

        if resident_name not in self.residents_info:
            raise ValueError(f"AI居民 {resident_name} 不存在")

        # 使用純 LLM 生成回應
        response = self._generate_resident_response_via_llm(survey, resident_name)

        if response:
            self.survey_manager.save_response(response)

        return response

    def _generate_resident_response_via_llm(self, survey: Survey, resident_name: str) -> SurveyResponse:
        """
        為特定居民生成問卷回應 - 純 LLM 驅動

        Args:
            survey: 問卷對象
            resident_name: 居民姓名

        Returns:
            問卷回應對象
        """
        response = SurveyResponse(survey.survey_id, resident_name)

        print(f"   📝 問卷: {survey.title}")
        print(f"   🤖 使用 Ollama LLM 生成 {len(survey.questions)} 個回答...")

        for i, question in enumerate(survey.questions, 1):
            try:
                # 使用 Ollama 生成回答（無 fallback 到規則引擎）
                answer = self._generate_answer_via_ollama(
                    question=question,
                    resident_name=resident_name
                )

                response.add_response(question["id"], answer)
                print(f"      [{i}/{len(survey.questions)}] {question['text'][:30]}... ✓")

            except Exception as e:
                print(f"      [{i}/{len(survey.questions)}] {question['text'][:30]}... ❌ 錯誤: {e}")
                # 發生錯誤時使用通用回答，而非硬編碼規則
                answer = self._get_error_fallback_answer(question["type"])
                response.add_response(question["id"], answer)

        response.complete()
        return response

    def _generate_answer_via_ollama(self, question: Dict, resident_name: str) -> Any:
        """
        使用 Ollama LLM 生成問卷回答

        Args:
            question: 問題字典
            resident_name: 居民姓名

        Returns:
            生成的回答
        """
        question_type = question["type"]
        question_text = question["text"]
        options = question.get("options", [])

        # 調用 Ollama 生成器（不使用 resident_info，因為 generator 會直接讀取 agent.json）
        llm_response = self.ollama_generator.generate_response(
            resident_name=resident_name,
            resident_info={},  # 空字典，generator 會自己載入 agent.json
            question_text=question_text,
            question_type=question_type,
            options=options
        )

        # 處理 LLM 回應格式
        return self._process_llm_response(llm_response, question_type, options)

    def _process_llm_response(self, llm_response: str, question_type: str, options: List[str]) -> Any:
        """
        處理 LLM 生成的回應，確保格式正確

        Args:
            llm_response: LLM 原始回應
            question_type: 問題類型
            options: 選項列表

        Returns:
            格式化後的回答
        """
        if not llm_response:
            return self._get_error_fallback_answer(question_type)

        llm_response = llm_response.strip()

        if question_type == "single_choice":
            # 單選題：匹配選項
            for option in options:
                # 精確匹配或包含匹配
                if option == llm_response or option in llm_response or llm_response in option:
                    return option

            # 如果無法匹配，嘗試模糊匹配
            for option in options:
                option_words = set(option.replace("、", " ").replace("，", " ").split())
                response_words = set(llm_response.replace("、", " ").replace("，", " ").split())
                if option_words & response_words:  # 有交集
                    return option

            # 仍無法匹配，返回 LLM 原始回應
            print(f"         ⚠️  無法匹配選項，使用 LLM 原始回應: {llm_response}")
            return llm_response

        elif question_type == "multiple_choice":
            # 多選題：提取所有匹配的選項
            selected = []
            for option in options:
                if option in llm_response:
                    selected.append(option)

            if selected:
                return selected

            # 嘗試用頓號或逗號分割
            parts = llm_response.replace("、", ",").replace("，", ",").split(",")
            for part in parts:
                part = part.strip()
                for option in options:
                    if part in option or option in part:
                        if option not in selected:
                            selected.append(option)

            if selected:
                return selected

            # 無法匹配，返回原始回應作為列表
            print(f"         ⚠️  無法匹配選項，使用 LLM 原始回應")
            return [llm_response]

        elif question_type == "rating":
            # 評分題：提取數字
            import re
            match = re.search(r'(\d+)', llm_response)
            if match:
                rating = int(match.group(1))
                # 確保在範圍內
                if 1 <= rating <= 10:
                    return rating
                else:
                    return max(1, min(10, rating))  # 限制範圍

            # 無法提取數字，返回 5
            print(f"         ⚠️  無法提取評分，使用預設值 5")
            return 5

        elif question_type == "text":
            # 文字題：直接返回
            return llm_response

        return llm_response

    def _get_error_fallback_answer(self, question_type: str) -> Any:
        """
        當 LLM 完全失敗時的緊急 fallback
        僅在異常情況下使用，避免整個問卷失敗

        Args:
            question_type: 問題類型

        Returns:
            最小可用回答
        """
        fallbacks = {
            'single_choice': '無法回答',
            'multiple_choice': [],
            'rating': 5,
            'text': '抱歉，目前無法提供回答。'
        }
        return fallbacks.get(question_type, '無法回答')
