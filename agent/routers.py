"""LangGraph 条件路由函数

根据当前状态决定下一步走向哪个节点。
"""


def route_news_result(state: dict) -> str:
    """新闻搜索结果路由

    判断逻辑：
    - 有新闻（>= 1 条）→ enough_news → fetch_articles
    - 无新闻且 days < 30 → expand_days → expand_news_days（扩大搜索范围）
    - 无新闻且 days >= 30 → continue_with_warning → fetch_articles（带警告继续）

    Args:
        state: 当前 LangGraph 状态

    Returns:
        路由键: "enough_news" / "expand_days" / "continue_with_warning"
    """
    news_items = state.get("news_items", [])
    days = state.get("days", 1)

    if len(news_items) >= 1:
        return "enough_news"

    if days < 30:
        return "expand_days"

    return "continue_with_warning"


def route_quality_result(state: dict) -> str:
    """质检结果路由

    判断逻辑：
    - 分数 >= 8 → pass → save_report
    - 分数 < 8 且修订次数 < 2 → revise → revise_report
    - 分数 < 8 且修订次数 >= 2 → save_with_warnings → save_report_with_warnings

    Args:
        state: 当前 LangGraph 状态

    Returns:
        路由键: "pass" / "revise" / "save_with_warnings"
    """
    score = state.get("quality_score", 0)
    revise_count = state.get("revise_count", 0)

    if score >= 8:
        return "pass"

    if revise_count < 2:
        return "revise"

    return "save_with_warnings"
