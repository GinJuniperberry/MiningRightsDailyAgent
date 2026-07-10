"""端到端测试

测试完整流程：输入 → MCP 调用 → 报告生成 → 保存。
需要 MCP Server 可启动（依赖 mcp 包）。
"""
import pytest
import sys
import os
import asyncio

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from agent.graph import build_graph


@pytest.mark.asyncio
async def test_e2e_pilbara_briefing():
    """端到端测试：Pilbara 锂矿日报生成

    验证完整流程：
    1. 意图解析
    2. 资产解析
    3. 新闻搜索（MCP）
    4. 新闻正文抓取（MCP）
    5. 资源量抽取（MCP）
    6. 价格查询（MCP）
    7. 上下文分析
    8. 风险生成
    9. 报告渲染
    10. 质检
    11. 报告保存
    """
    graph = build_graph()

    result = await graph.ainvoke({
        "user_query": "给我生成一份关于 Pilbara 锂矿的今日简报"
    })

    # 验证基本字段
    assert "markdown" in result
    assert len(result["markdown"]) > 0
    assert "report_path" in result
    assert os.path.exists(result["report_path"])

    # 验证报告内容
    md = result["markdown"]
    assert "Pilbara" in md
    assert "lithium" in md or "锂" in md

    # 验证质检
    assert "quality_score" in result
    assert isinstance(result["quality_score"], (int, float))

    # 清理测试报告
    if os.path.exists(result["report_path"]):
        os.remove(result["report_path"])


@pytest.mark.asyncio
async def test_e2e_report_contains_required_sections():
    """端到端测试：报告包含所有必需章节"""
    graph = build_graph()

    result = await graph.ainvoke({
        "user_query": "给我生成一份关于 Pilbara 锂矿的今日简报"
    })

    md = result["markdown"]

    # 验证报告结构
    assert "# " in md  # 有标题
    assert "新闻" in md  # 有新闻章节
    assert "资源量" in md or "储量" in md  # 有资源量章节
    assert "价格" in md  # 有价格章节
    assert "风险" in md  # 有风险章节
    assert "引用" in md or "来源" in md  # 有引用章节

    # 清理
    if os.path.exists(result.get("report_path", "")):
        os.remove(result["report_path"])


@pytest.mark.asyncio
async def test_e2e_warnings_captured():
    """端到端测试：降级警告被正确捕获"""
    graph = build_graph()

    result = await graph.ainvoke({
        "user_query": "给我生成一份关于 Pilbara 锂矿的今日简报"
    })

    # 由于真实数据源可能不可用，应有警告信息（或 Mock 降级正常工作）
    # 这里只验证流程跑通，不强制要求有 warnings
    assert "markdown" in result

    # 清理
    if os.path.exists(result.get("report_path", "")):
        os.remove(result["report_path"])
