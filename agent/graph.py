"""LangGraph StateGraph 构建

构建矿权日报 Agent 的完整工作流图。

节点流程：
START → parse_intent → resolve_asset → search_news → [条件路由]
  → fetch_articles → extract_resources → fetch_price
  → analyze_context → generate_risks → render_report
  → quality_check → [条件路由]
  → save_report / revise_report / save_report_with_warnings → END
"""
from langgraph.graph import StateGraph, START, END

from agent.state import BriefingState
from agent.nodes import (
    parse_intent,
    resolve_asset,
    search_news,
    expand_news_days,
    fetch_articles,
    extract_resources,
    fetch_price,
    analyze_context,
    generate_risks,
    render_report,
    quality_check,
    revise_report,
    save_report,
    save_report_with_warnings,
)
from agent.routers import (
    route_news_result,
    route_quality_result,
)


def build_graph():
    """构建并编译 LangGraph StateGraph

    Returns:
        编译后的 LangGraph 可执行图
    """
    graph = StateGraph(BriefingState)

    # 添加所有节点
    graph.add_node("parse_intent", parse_intent)
    graph.add_node("resolve_asset", resolve_asset)
    graph.add_node("search_news", search_news)
    graph.add_node("expand_news_days", expand_news_days)
    graph.add_node("fetch_articles", fetch_articles)
    graph.add_node("extract_resources", extract_resources)
    graph.add_node("fetch_price", fetch_price)
    graph.add_node("analyze_context", analyze_context)
    graph.add_node("generate_risks", generate_risks)
    graph.add_node("render_report", render_report)
    graph.add_node("quality_check", quality_check)
    graph.add_node("revise_report", revise_report)
    graph.add_node("save_report", save_report)
    graph.add_node("save_report_with_warnings", save_report_with_warnings)

    # 添加线性边
    graph.add_edge(START, "parse_intent")
    graph.add_edge("parse_intent", "resolve_asset")
    graph.add_edge("resolve_asset", "search_news")

    # 新闻搜索条件路由
    graph.add_conditional_edges(
        "search_news",
        route_news_result,
        {
            "enough_news": "fetch_articles",
            "expand_days": "expand_news_days",
            "continue_with_warning": "fetch_articles",
        }
    )

    # 扩大搜索天数后重新搜索
    graph.add_edge("expand_news_days", "search_news")

    # 继续线性流程
    graph.add_edge("fetch_articles", "extract_resources")
    graph.add_edge("extract_resources", "fetch_price")
    graph.add_edge("fetch_price", "analyze_context")
    graph.add_edge("analyze_context", "generate_risks")
    graph.add_edge("generate_risks", "render_report")
    graph.add_edge("render_report", "quality_check")

    # 质检条件路由
    graph.add_conditional_edges(
        "quality_check",
        route_quality_result,
        {
            "pass": "save_report",
            "revise": "revise_report",
            "save_with_warnings": "save_report_with_warnings",
        }
    )

    # 修订后重新质检
    graph.add_edge("revise_report", "quality_check")

    # 保存后结束
    graph.add_edge("save_report", END)
    graph.add_edge("save_report_with_warnings", END)

    return graph.compile()
