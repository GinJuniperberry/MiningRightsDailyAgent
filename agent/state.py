"""LangGraph 共享状态定义

BriefingState 是整个 LangGraph StateGraph 的共享状态，
所有节点围绕这个状态读写数据。
"""
from typing import TypedDict, Optional, List, Dict, Any


class BriefingState(TypedDict, total=False):
    """矿权日报 Agent 的共享状态

    Attributes:
        user_query: 用户原始输入

        # 意图解析结果
        project: 矿权项目名称
        company: 公司名
        commodity: 矿种
        report_type: 报告类型
        days: 搜索天数

        # 配置解析结果
        aliases: 项目别名列表
        pdf_urls: PDF 报告 URL 列表

        # MCP 工具结果
        news_items: 新闻搜索结果列表
        articles: 新闻正文列表
        resources: 资源量数据
        latest_price: 最新价格
        price_trend: 价格趋势

        # 中间分析结果
        news_summary: 新闻摘要
        resource_summary: 资源量摘要
        price_summary: 价格摘要
        risks: 风险提示列表

        # 报告结果
        markdown: 生成的 Markdown 报告
        report_path: 报告保存路径

        # 质量控制
        quality_score: 质检分数
        quality_issues: 质检问题列表
        revise_count: 修订次数

        # 异常与降级
        errors: 错误列表
        warnings: 警告列表
    """
    # 原始输入
    user_query: str

    # 意图解析结果
    project: str
    company: str
    commodity: str
    report_type: str
    days: int

    # 配置解析结果
    aliases: List[str]
    pdf_urls: List[str]

    # MCP 工具结果
    news_items: List[Dict[str, Any]]
    articles: List[Dict[str, Any]]
    resources: Dict[str, Any]
    latest_price: Dict[str, Any]
    price_trend: Dict[str, Any]

    # 中间分析结果
    news_summary: str
    resource_summary: str
    price_summary: str
    risks: List[str]

    # 报告结果
    markdown: str
    report_path: str

    # 质量控制
    quality_score: float
    quality_issues: List[str]
    revise_count: int

    # 异常与降级
    errors: List[Dict[str, Any]]
    warnings: List[str]
