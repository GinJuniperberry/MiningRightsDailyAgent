"""Markdown 报告生成器

基于 LangGraph 状态数据渲染结构化 Markdown 日报。
报告结构：
1. 标题与生成时间
2. 今日结论
3. 新闻摘要
4. 资源量/储量数据（表格）
5. 价格走势
6. 风险提示
7. 引用源
"""
from datetime import date
from typing import Dict, Any, Optional, List


def generate_markdown_report(state: Dict[str, Any],
                             previous_markdown: Optional[str] = None,
                             quality_issues: Optional[List[str]] = None) -> str:
    """生成完整的 Markdown 日报

    Args:
        state: LangGraph 状态字典
        previous_markdown: 上一次生成的报告（修订时使用）
        quality_issues: 质检问题列表（修订时用于针对性修复）

    Returns:
        完整的 Markdown 报告字符串
    """
    project = state.get("project", "Unknown")
    commodity = state.get("commodity", "unknown")
    today = date.today().isoformat()

    sections = []

    # 1. 标题与生成时间
    sections.append(_render_header(project, commodity, today))

    # 2. 今日结论
    sections.append(_render_conclusion(state))

    # 3. 新闻摘要
    sections.append(_render_news_section(state))

    # 4. 资源量数据
    sections.append(_render_resources_section(state))

    # 5. 价格走势
    sections.append(_render_price_section(state))

    # 6. 风险提示
    sections.append(_render_risks_section(state))

    # 7. 引用源
    sections.append(_render_references_section(state))

    # 8. 警告信息（如果有）
    warnings = state.get("warnings", [])
    if warnings:
        sections.append(_render_warnings_section(warnings))

    report = "\n\n".join(sections)

    # 如果是修订且 LLM 不可用，在报告末尾追加质检问题说明
    if quality_issues and previous_markdown:
        report += "\n\n---\n\n> **修订说明**：已根据质检问题进行修订。\n"
        for issue in quality_issues:
            report += f"> - {issue}\n"

    return report


def _render_header(project: str, commodity: str, today: str) -> str:
    """渲染标题"""
    return f"# {project} {commodity} 日报\n\n生成时间：{today}"


def _render_conclusion(state: Dict[str, Any]) -> str:
    """渲染今日结论"""
    conclusions = []

    news_summary = state.get("news_summary", "")
    if news_summary:
        conclusions.append(f"- {news_summary}")

    price_summary = state.get("price_summary", "")
    if price_summary:
        conclusions.append(f"- {price_summary}")

    risks = state.get("risks", [])
    if risks:
        conclusions.append(f"- 当前主要风险包括 {('、'.join(risks[:3]))}。")

    if not conclusions:
        conclusions.append("- 今日数据采集完毕，详见各章节。")

    return "## 1. 今日结论\n\n" + "\n".join(conclusions)


def _render_news_section(state: Dict[str, Any]) -> str:
    """渲染新闻摘要"""
    articles = state.get("articles", [])
    news_items = state.get("news_items", [])

    if not articles and not news_items:
        return "## 2. 新闻摘要\n\n暂无相关新闻。"

    lines = ["## 2. 新闻摘要\n"]

    # 优先使用 articles（有正文的）
    source_list = articles if articles else news_items

    for i, item in enumerate(source_list[:5], 1):
        title = item.get("title", "无标题")
        url = item.get("url", "")
        published_at = item.get("published_at", "")
        source = item.get("source", "")
        summary = item.get("summary", item.get("content", "")[:200] if item.get("content") else "")

        lines.append(f"### 新闻 {i}：{title}\n")
        if published_at or source:
            meta = " | ".join(filter(None, [published_at, source]))
            lines.append(f"*{meta}*\n")

        if summary:
            # 截取前 300 字作为摘要
            summary_text = summary[:300]
            if len(summary) > 300:
                summary_text += "..."
            lines.append(f"{summary_text}\n")

        if url:
            lines.append(f"来源：{url}\n")

    return "\n".join(lines)


def _render_resources_section(state: Dict[str, Any]) -> str:
    """渲染资源量数据表格"""
    resources = state.get("resources", {})
    resource_list = resources.get("resources", [])

    if not resource_list:
        return "## 3. 资源量 / 储量数据\n\n资源量数据待人工复核。"

    lines = [
        "## 3. 资源量 / 储量数据\n",
        "| 分类 | 矿石量 | 品位 | 金属量 | 页码 | 置信度 |",
        "|---|---:|---:|---:|---:|---:|",
    ]

    for r in resource_list:
        category = r.get("category", "-")
        ore = r.get("ore_tonnage", {})
        grade = r.get("grade", {})
        metal = r.get("contained_metal", {})
        page = r.get("page", "-")
        confidence = r.get("confidence", 0)

        ore_str = f"{ore.get('value', '-')} {ore.get('unit', '')}".strip()
        grade_str = f"{grade.get('value', '-')} {grade.get('unit', '')}".strip()
        metal_str = f"{metal.get('value', '-')} {metal.get('unit', '')}".strip()

        lines.append(
            f"| {category} | {ore_str} | {grade_str} | {metal_str} | {page} | {confidence} |"
        )

    report_url = resources.get("report_url", "")
    if report_url:
        lines.append(f"\n报告来源：{report_url}")

    return "\n".join(lines)


def _render_price_section(state: Dict[str, Any]) -> str:
    """渲染价格走势"""
    latest_price = state.get("latest_price", {})
    price_trend = state.get("price_trend", {})

    if not latest_price and not price_trend:
        return "## 4. 价格走势\n\n价格数据不可用。"

    lines = ["## 4. 价格走势\n"]

    if latest_price:
        price_val = latest_price.get("price", "-")
        unit = latest_price.get("unit", "")
        currency = latest_price.get("currency", "")
        lines.append(f"- 当前价格：{price_val} {unit}")

    if price_trend:
        change_pct = price_trend.get("change_pct", "-")
        trend = price_trend.get("trend", "-")
        ma_7 = price_trend.get("ma_7", "-")
        ma_30 = price_trend.get("ma_30", "-")
        days = price_trend.get("days", 30)

        trend_text = {"up": "上涨", "down": "下跌", "flat": "震荡"}.get(trend, trend)

        lines.append(f"- 近 {days} 天涨跌幅：{change_pct}%")
        lines.append(f"- 7 日均线：{ma_7} {unit if latest_price else ''}")
        lines.append(f"- 30 日均线：{ma_30} {unit if latest_price else ''}")
        lines.append(f"- 趋势判断：{trend_text}")

        observations = price_trend.get("observations", [])
        if observations:
            lines.append("\n**趋势观察：**\n")
            for obs in observations:
                lines.append(f"- {obs}")

    return "\n".join(lines)


def _render_risks_section(state: Dict[str, Any]) -> str:
    """渲染风险提示"""
    risks = state.get("risks", [])

    if not risks:
        return "## 5. 风险提示\n\n暂无风险提示。"

    lines = ["## 5. 风险提示\n"]
    for i, risk in enumerate(risks, 1):
        lines.append(f"{i}. {risk}")

    return "\n".join(lines)


def _render_references_section(state: Dict[str, Any]) -> str:
    """渲染引用源"""
    lines = ["## 6. 引用源\n"]

    # 新闻来源
    articles = state.get("articles", [])
    news_items = state.get("news_items", [])
    news_urls = set()
    for item in articles + news_items:
        url = item.get("url", "")
        if url:
            news_urls.add(url)

    if news_urls:
        lines.append("**新闻来源：**")
        for url in news_urls:
            lines.append(f"- {url}")
        lines.append("")

    # PDF 报告来源
    resources = state.get("resources", {})
    report_url = resources.get("report_url", "")
    if report_url:
        lines.append("**PDF 报告：**")
        lines.append(f"- {report_url}")
        lines.append("")

    # 价格来源
    latest_price = state.get("latest_price", {})
    price_source = latest_price.get("source", "")
    if price_source:
        lines.append("**价格来源：**")
        lines.append(f"- {price_source}")

    return "\n".join(lines)


def _render_warnings_section(warnings: List[str]) -> str:
    """渲染警告信息"""
    lines = ["## 7. 数据警告\n", "> 以下警告在数据采集过程中产生：\n"]
    for w in warnings:
        lines.append(f"- {w}")
    return "\n".join(lines)
