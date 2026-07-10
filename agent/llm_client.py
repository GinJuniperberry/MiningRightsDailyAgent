"""通义千问 LLM 客户端

基于阿里云 DashScope 的 OpenAI 兼容接口调用通义千问模型。
不配置 DASHSCOPE_API_KEY 或 USE_LLM=false 时，所有方法返回 None，
调用方需走规则兜底，保证无 API Key 也能运行 demo。
"""
import os
import json
from typing import Optional, Dict, Any, List

from openai import AsyncOpenAI

from agent.prompts import (
    PARSE_INTENT_SYSTEM,
    PARSE_INTENT_USER,
    SUMMARIZE_NEWS_SYSTEM,
    SUMMARIZE_NEWS_USER,
    GENERATE_RISKS_SYSTEM,
    GENERATE_RISKS_USER,
    QUALITY_CHECK_SYSTEM,
    QUALITY_CHECK_USER,
    REVISE_REPORT_SYSTEM,
    REVISE_REPORT_USER,
)


class LLMClient:
    """通义千问 LLM 客户端封装

    环境变量：
        DASHSCOPE_API_KEY: 通义千问 API Key（不配置则禁用 LLM）
        USE_LLM: 是否启用 LLM（"false" 禁用，默认 "true"）
        LLM_BASE_URL: API 地址，默认 DashScope 兼容接口
        LLM_MODEL: 模型名，默认 qwen-plus
    """

    def __init__(self):
        self.api_key = os.getenv("DASHSCOPE_API_KEY", "")
        self.use_llm = os.getenv("USE_LLM", "true").lower() == "true"
        self.base_url = os.getenv(
            "LLM_BASE_URL",
            "https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        self.model = os.getenv("LLM_MODEL", "qwen-plus")

        self.client = None
        if self.api_key and self.use_llm:
            try:
                self.client = AsyncOpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url,
                )
            except Exception as e:
                print(f"[LLM] 客户端初始化失败，将走规则模式: {e}")
                self.client = None

    @property
    def available(self) -> bool:
        """LLM 是否可用"""
        return self.client is not None

    async def chat(self, system_prompt: str, user_prompt: str,
                   temperature: float = 0.3) -> Optional[str]:
        """通用 LLM 对话接口

        Args:
            system_prompt: 系统提示词
            user_prompt: 用户提示词
            temperature: 温度参数

        Returns:
            LLM 生成的文本，或 None（不可用或调用失败时）
        """
        if not self.available:
            return None

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
                max_tokens=2000,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"[LLM] 调用失败: {e}")
            return None

    async def parse_intent(self, query: str) -> Optional[Dict[str, Any]]:
        """LLM 意图解析

        Args:
            query: 用户输入文本

        Returns:
            解析结果字典（project, company, commodity, report_type, days），
            或 None（不可用或解析失败时，调用方走规则兜底）
        """
        user_prompt = PARSE_INTENT_USER.format(query=query)
        result = await self.chat(PARSE_INTENT_SYSTEM, user_prompt)

        if not result:
            return None

        try:
            # 尝试提取 JSON
            result = result.strip()
            if result.startswith("```"):
                # 去除 markdown 代码块
                result = result.split("\n", 1)[1].rsplit("```", 1)[0]
            return json.loads(result)
        except (json.JSONDecodeError, IndexError) as e:
            print(f"[LLM] 意图解析 JSON 解析失败: {e}")
            return None

    async def summarize_news(self, project: str, commodity: str,
                             news_text: str) -> Optional[str]:
        """LLM 新闻摘要生成

        Args:
            project: 项目名
            commodity: 矿种
            news_text: 新闻文本

        Returns:
            摘要文本，或 None
        """
        user_prompt = SUMMARIZE_NEWS_USER.format(
            project=project,
            commodity=commodity,
            news_text=news_text,
        )
        return await self.chat(SUMMARIZE_NEWS_SYSTEM, user_prompt)

    async def generate_risks(self, project: str, commodity: str,
                             news_summary: str, resource_summary: str,
                             price_summary: str) -> Optional[List[str]]:
        """LLM 风险生成

        Returns:
            风险列表，或 None
        """
        user_prompt = GENERATE_RISKS_USER.format(
            project=project,
            commodity=commodity,
            news_summary=news_summary,
            resource_summary=resource_summary,
            price_summary=price_summary,
        )
        result = await self.chat(GENERATE_RISKS_SYSTEM, user_prompt)

        if not result:
            return None

        try:
            result = result.strip()
            if result.startswith("```"):
                result = result.split("\n", 1)[1].rsplit("```", 1)[0]
            risks = json.loads(result)
            if isinstance(risks, list):
                return risks
            return None
        except (json.JSONDecodeError, IndexError):
            return None

    async def check_quality(self, markdown: str) -> Optional[Dict[str, Any]]:
        """LLM 质检

        Returns:
            {"score": float, "issues": List[str]}，或 None
        """
        user_prompt = QUALITY_CHECK_USER.format(markdown=markdown)
        result = await self.chat(QUALITY_CHECK_SYSTEM, user_prompt)

        if not result:
            return None

        try:
            result = result.strip()
            if result.startswith("```"):
                result = result.split("\n", 1)[1].rsplit("```", 1)[0]
            data = json.loads(result)
            return {
                "score": float(data.get("score", 0)),
                "issues": data.get("issues", []),
            }
        except (json.JSONDecodeError, IndexError, ValueError):
            return None

    async def revise_report(self, markdown: str, issues: List[str]) -> Optional[str]:
        """LLM 报告修订

        Returns:
            修订后的 Markdown，或 None
        """
        issues_text = "\n".join(f"- {issue}" for issue in issues)
        user_prompt = REVISE_REPORT_USER.format(
            issues=issues_text,
            markdown=markdown,
        )
        return await self.chat(REVISE_REPORT_SYSTEM, user_prompt)


# 全局单例
llm_client = LLMClient()
