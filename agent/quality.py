"""报告质检模块

基于规则 + LLM 的轻量质检，检查 Markdown 报告是否满足交付要求。

规则检查：
1. 是否有标题
2. 是否有新闻摘要（至少 1 条）
3. 是否有资源量表格
4. 是否有价格走势
5. 是否有风险提示（至少 3 条）
6. 是否有引用链接

LLM 判断（可选）：
- 报告是否完整
- 是否有明显缺项
"""
import re
from typing import Dict, Any, List

from agent.llm_client import llm_client


def check_report_quality(markdown: str, state: Dict[str, Any]) -> Dict[str, Any]:
    """检查 Markdown 报告质量

    Args:
        markdown: 生成的 Markdown 报告
        state: LangGraph 状态

    Returns:
        {"score": float, "issues": List[str]}
        score >= 8 通过，否则需要修订
    """
    issues: List[str] = []
    score = 10.0

    # 规则 1：有标题
    if not markdown.strip().startswith("#"):
        issues.append("报告缺少主标题")
        score -= 2.0

    # 规则 2：有新闻摘要（至少 1 条）
    news_count = markdown.count("### 新闻")
    if news_count < 1:
        issues.append("新闻摘要不足，至少需要 1 条新闻")
        score -= 1.5

    # 规则 3：有资源量表格
    if "|" not in markdown or "Indicated" not in markdown and "Inferred" not in markdown and "Measured" not in markdown:
        issues.append("缺少资源量数据表格")
        score -= 1.5

    # 规则 4：有价格走势
    if "价格" not in markdown:
        issues.append("缺少价格走势章节")
        score -= 1.0

    # 规则 5：有风险提示（至少 3 条）
    risk_section = _extract_section(markdown, "风险提示")
    risk_count = risk_section.count("\n") if risk_section else 0
    # 简单计算：以数字开头的行
    risk_lines = re.findall(r"^\d+\.\s", risk_section, re.MULTILINE) if risk_section else []
    if len(risk_lines) < 3:
        issues.append(f"风险提示不足，当前 {len(risk_lines)} 条，至少需要 3 条")
        score -= 1.0

    # 规则 6：有引用链接
    http_links = re.findall(r"https?://", markdown)
    if len(http_links) < 3:
        issues.append("引用源链接不足，新闻、PDF、价格来源至少各有链接")
        score -= 1.0

    # 确保分数在 0-10 之间
    score = max(0.0, min(10.0, score))

    return {
        "score": round(score, 1),
        "issues": issues,
    }


def _extract_section(markdown: str, section_name: str) -> str:
    """从 Markdown 中提取指定章节内容

    Args:
        markdown: Markdown 文本
        section_name: 章节名（如 "风险提示"）

    Returns:
        章节内容字符串，找不到时返回空字符串
    """
    # 使用 [^\n]* 限制标题行匹配在单行内，避免 DOTALL 下贪婪跨行
    pattern = rf"##[^\n]*{section_name}[^\n]*\n(.*?)(?=\n## |\Z)"
    match = re.search(pattern, markdown, re.DOTALL)
    return match.group(1) if match else ""


async def check_report_quality_with_llm(markdown: str, state: Dict[str, Any]) -> Dict[str, Any]:
    """规则 + LLM 联合质检

    先执行规则检查，如果 LLM 可用则结合 LLM 判断。

    Args:
        markdown: 生成的 Markdown 报告
        state: LangGraph 状态

    Returns:
        {"score": float, "issues": List[str]}
    """
    # 先执行规则检查
    rule_result = check_report_quality(markdown, state)

    # 如果 LLM 可用，结合 LLM 判断
    if llm_client.available:
        llm_result = await llm_client.check_quality(markdown)
        if llm_result:
            # 取规则和 LLM 的平均分
            rule_score = rule_result["score"]
            llm_score = llm_result.get("score", rule_score)
            combined_score = (rule_score + llm_score) / 2

            # 合并问题列表（去重）
            combined_issues = list(rule_result["issues"])
            for issue in llm_result.get("issues", []):
                if issue not in combined_issues:
                    combined_issues.append(issue)

            return {
                "score": round(combined_score, 1),
                "issues": combined_issues,
            }

    return rule_result
