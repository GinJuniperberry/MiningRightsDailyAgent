"""LangGraph 编排测试

测试图流程的各个节点和路由逻辑。
"""
import pytest
import sys
import os

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from agent.state import BriefingState
from agent.nodes import (
    parse_intent,
    resolve_asset,
    expand_news_days,
    analyze_context,
    generate_risks,
    render_report,
    save_report,
)
from agent.routers import route_news_result, route_quality_result
from agent.asset_resolver import resolve_asset_by_query
from agent.report_generator import generate_markdown_report
from agent.quality import check_report_quality


# ============ parse_intent 测试 ============

def test_parse_intent_pilbara():
    """测试 parse_intent 识别 Pilbara"""
    state = {"user_query": "给我生成一份关于 Pilbara 锂矿的今日简报"}
    result = parse_intent(state)

    assert result["project"] == "Pilbara"
    assert result["company"] == "Pilbara Minerals"
    assert result["commodity"] == "lithium"
    assert result["report_type"] == "daily_briefing"
    assert result["days"] == 1
    assert result["revise_count"] == 0


def test_parse_intent_greenbushes():
    """测试 parse_intent 识别 Greenbushes"""
    state = {"user_query": "Greenbushes lithium briefing"}
    result = parse_intent(state)

    assert result["project"] == "Greenbushes"
    assert result["commodity"] == "lithium"


def test_parse_intent_unknown():
    """测试 parse_intent 未识别项目"""
    state = {"user_query": "给我一份铜矿报告"}
    result = parse_intent(state)

    assert result["project"] == "unknown"
    assert result["commodity"] == "copper"
    assert len(result["warnings"]) > 0


# ============ resolve_asset 测试 ============

def test_resolve_asset_pilbara():
    """测试 resolve_asset 补全 Pilbara 配置"""
    state = {
        "project": "Pilbara",
        "company": "Pilbara Minerals",
        "commodity": "lithium",
    }
    result = resolve_asset(state)

    assert "aliases" in result
    assert len(result["aliases"]) > 0
    assert len(result["pdf_urls"]) > 0


def test_resolve_asset_by_query_function():
    """测试 resolve_asset_by_query 函数"""
    asset = resolve_asset_by_query(project="Pilbara")

    assert asset["company"] == "Pilbara Minerals"
    assert asset["commodity"] == "lithium"
    assert "Pilbara" in asset["aliases"]


def test_resolve_asset_unknown():
    """测试 resolve_asset 未匹配项目"""
    asset = resolve_asset_by_query(project="NonExistent")

    assert asset["company"] == "NonExistent" or asset["company"] == "Unknown"


# ============ expand_news_days 测试 ============

def test_expand_news_days_1_to_7():
    """测试新闻搜索天数扩展 1→7"""
    state = {"days": 1}
    result = expand_news_days(state)
    assert result["days"] == 7


def test_expand_news_days_7_to_30():
    """测试新闻搜索天数扩展 7→30"""
    state = {"days": 7}
    result = expand_news_days(state)
    assert result["days"] == 30


def test_expand_news_days_30_stays_30():
    """测试新闻搜索天数 30 不再扩展"""
    state = {"days": 30}
    result = expand_news_days(state)
    assert result["days"] == 30


# ============ 路由测试 ============

def test_route_news_result_enough():
    """测试新闻路由：有足够新闻"""
    state = {"news_items": [{"title": "test"}], "days": 1}
    assert route_news_result(state) == "enough_news"


def test_route_news_result_expand():
    """测试新闻路由：无新闻，需扩大搜索"""
    state = {"news_items": [], "days": 1}
    assert route_news_result(state) == "expand_days"


def test_route_news_result_continue_with_warning():
    """测试新闻路由：无新闻且已达 30 天"""
    state = {"news_items": [], "days": 30}
    assert route_news_result(state) == "continue_with_warning"


def test_route_quality_result_pass():
    """测试质检路由：通过"""
    state = {"quality_score": 8.5, "revise_count": 0}
    assert route_quality_result(state) == "pass"


def test_route_quality_result_revise():
    """测试质检路由：需修订"""
    state = {"quality_score": 6.0, "revise_count": 0}
    assert route_quality_result(state) == "revise"


def test_route_quality_result_save_with_warnings():
    """测试质检路由：修订次数达上限，带警告保存"""
    state = {"quality_score": 6.0, "revise_count": 2}
    assert route_quality_result(state) == "save_with_warnings"


# ============ analyze_context 测试 ============

@pytest.mark.asyncio
async def test_analyze_context_with_data():
    """测试上下文分析（有数据）"""
    state = {
        "articles": [{"title": "Test", "content": "Test content"}],
        "resources": {"resources": [{"category": "Indicated"}]},
        "price_trend": {"change_pct": 7.14, "trend": "up", "days": 30},
        "project": "Pilbara",
        "commodity": "lithium",
    }
    result = await analyze_context(state)

    assert "news_summary" in result
    assert "resource_summary" in result
    assert "price_summary" in result
    assert "1 条" in result["news_summary"] or "条" in result["news_summary"]
    assert "Indicated" in result["resource_summary"]
    assert "7.14" in result["price_summary"]


@pytest.mark.asyncio
async def test_analyze_context_empty():
    """测试上下文分析（无数据）"""
    state = {
        "articles": [],
        "resources": {},
        "price_trend": {},
        "project": "Test",
        "commodity": "test",
    }
    result = await analyze_context(state)

    assert "暂无" in result["news_summary"]
    assert "待人工" in result["resource_summary"]
    assert "不可用" in result["price_summary"]


# ============ generate_risks 测试 ============

@pytest.mark.asyncio
async def test_generate_risks():
    """测试风险生成"""
    state = {
        "price_trend": {"change_pct": 7.14},
        "resources": {"resources": [{"category": "Indicated"}]},
        "articles": [{"title": "Test"}],
        "project": "Pilbara",
        "commodity": "lithium",
    }
    result = await generate_risks(state)

    assert "risks" in result
    assert len(result["risks"]) >= 3


# ============ render_report 测试 ============

def test_render_report():
    """测试报告渲染"""
    state = {
        "project": "Pilbara",
        "commodity": "lithium",
        "articles": [{"title": "Test News", "url": "https://example.com", "summary": "Test"}],
        "resources": {
            "resources": [
                {
                    "category": "Indicated",
                    "ore_tonnage": {"value": 120.5, "unit": "Mt"},
                    "grade": {"value": 1.2, "unit": "% Li2O"},
                    "contained_metal": {"value": 1.45, "unit": "Mt Li2O"},
                    "page": 128,
                    "confidence": 0.86,
                }
            ],
            "report_url": "https://example.com/report.pdf",
        },
        "latest_price": {"price": 105000, "unit": "CNY/t", "source": "test"},
        "price_trend": {"change_pct": 7.14, "trend": "up", "ma_7": 103200, "ma_30": 99700, "days": 30},
        "risks": ["风险1", "风险2", "风险3"],
        "news_summary": "共检索到 1 条新闻",
        "price_summary": "近 30 天上涨 7.14%",
    }
    result = render_report(state)

    assert "markdown" in result
    md = result["markdown"]
    assert "# Pilbara lithium 日报" in md
    assert "新闻摘要" in md
    assert "Indicated" in md
    assert "105000" in md
    assert "风险1" in md


# ============ quality_check 测试 ============

def test_quality_check_good_report():
    """测试质检：完整报告"""
    markdown = """# Test 日报

## 1. 今日结论
- 测试结论

## 2. 新闻摘要
### 新闻 1：Test
来源：https://example.com/news1

## 3. 资源量 / 储量数据
| 分类 | 矿石量 |
|---|---:|
| Indicated | 120.5 Mt |

报告来源：https://example.com/report.pdf

## 4. 价格走势
- 当前价格：105000 CNY/t

## 5. 风险提示
1. 风险1
2. 风险2
3. 风险3

## 6. 引用源
- https://example.com/news1
- https://example.com/report.pdf
- price-api
"""
    state = {}
    result = check_report_quality(markdown, state)

    assert result["score"] >= 8
    assert len(result["issues"]) == 0


def test_quality_check_bad_report():
    """测试质检：不完整报告"""
    markdown = "# Test"
    state = {}
    result = check_report_quality(markdown, state)

    assert result["score"] < 8
    assert len(result["issues"]) > 0


# ============ save_report 测试 ============

def test_save_report():
    """测试报告保存"""
    state = {
        "markdown": "# Test Report\n\nContent",
        "project": "TestProject",
    }
    result = save_report(state)

    assert "report_path" in result
    assert os.path.exists(result["report_path"])

    # 清理测试文件
    if os.path.exists(result["report_path"]):
        os.remove(result["report_path"])
