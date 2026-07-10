"""mineral-pdf-mcp 测试

测试 extract_resources 工具和 PDF 表格解析逻辑。
"""
import pytest
import sys
import os

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from servers.mineral_pdf_mcp.mock_data import MOCK_RESOURCES
from servers.mineral_pdf_mcp.table_parser import (
    parse_quantity,
    parse_grade,
    is_resource_table_row,
    extract_category_from_row,
)
from servers.mineral_pdf_mcp.schemas import ResourceEntry, Quantity, ExtractResponse


def test_mock_resources_structure():
    """测试 Mock 资源量数据结构"""
    assert "project" in MOCK_RESOURCES
    assert "resources" in MOCK_RESOURCES
    assert len(MOCK_RESOURCES["resources"]) >= 2

    categories = [r["category"] for r in MOCK_RESOURCES["resources"]]
    assert "Indicated" in categories
    assert "Inferred" in categories


def test_mock_resource_entry_fields():
    """测试 Mock 资源量条目字段完整性"""
    for r in MOCK_RESOURCES["resources"]:
        assert "category" in r
        assert "ore_tonnage" in r
        assert "grade" in r
        assert "contained_metal" in r
        assert "page" in r
        assert "confidence" in r

        assert "value" in r["ore_tonnage"]
        assert "unit" in r["ore_tonnage"]
        assert "value" in r["grade"]
        assert "unit" in r["grade"]


def test_parse_quantity():
    """测试量值解析"""
    q = parse_quantity("120.5 Mt")
    assert q is not None
    assert q["value"] == 120.5
    assert q["unit"] == "Mt"

    q = parse_quantity("1,200.5")
    assert q is not None
    assert q["value"] == 1200.5

    q = parse_quantity("")
    assert q is None


def test_parse_grade():
    """测试品位解析"""
    g = parse_grade("1.2% Li2O")
    assert g is not None
    assert g["value"] == 1.2

    g = parse_grade("1.5%")
    assert g is not None
    assert g["value"] == 1.5


def test_is_resource_table_row():
    """测试资源量行识别"""
    assert is_resource_table_row(["Indicated", "120.5", "Mt", "1.2", "% Li2O"])
    assert is_resource_table_row(["Inferred", "45.2", "Mt"])
    assert not is_resource_table_row(["Total", "165.7", "Mt"])
    assert not is_resource_table_row(["", "", ""])
    assert not is_resource_table_row([])


def test_extract_category_from_row():
    """测试分类提取"""
    assert extract_category_from_row(["Indicated", "120.5"]) == "Indicated"
    assert extract_category_from_row(["Inferred", "45.2"]) == "Inferred"
    assert extract_category_from_row(["Measured", "52.8"]) == "Measured"
    assert extract_category_from_row(["Other", "data"]) is None


def test_quantity_schema():
    """测试 Quantity Pydantic 模型"""
    q = Quantity(value=120.5, unit="Mt")
    assert q.value == 120.5
    assert q.unit == "Mt"


def test_resource_entry_schema():
    """测试 ResourceEntry Pydantic 模型"""
    entry = ResourceEntry(
        category="Indicated",
        ore_tonnage=Quantity(value=120.5, unit="Mt"),
        grade=Quantity(value=1.2, unit="% Li2O"),
        contained_metal=Quantity(value=1.45, unit="Mt Li2O"),
        page=128,
        confidence=0.86,
    )
    assert entry.category == "Indicated"
    assert entry.ore_tonnage.value == 120.5


@pytest.mark.asyncio
async def test_extract_resources_with_mock_fallback():
    """测试 extract_resources 在 PDF 不可访问时返回 Mock 数据"""
    from servers.mineral_pdf_mcp.server import extract_resources

    result = await extract_resources(
        pdf_url="https://example.com/nonexistent.pdf"
    )

    assert "resources" in result
    assert len(result["resources"]) > 0
    assert "report_url" in result
