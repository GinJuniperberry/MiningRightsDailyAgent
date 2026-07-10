"""PDF 表格解析辅助函数

从 pdfplumber 提取的表格行中，识别并解析资源量数据。
"""
import re
from typing import Dict, Any, Optional, List


# 资源量分类关键词（Total 是汇总行，不算独立分类）
RESOURCE_CATEGORIES = ["Measured", "Indicated", "Inferred"]


def parse_quantity(text: str) -> Optional[Dict[str, Any]]:
    """解析量值字符串

    示例:
        "120.5 Mt" -> {"value": 120.5, "unit": "Mt"}
        "1.2" -> {"value": 1.2, "unit": ""}
        "1,200.5" -> {"value": 1200.5, "unit": ""}

    Args:
        text: 包含数值和可能的单位的字符串

    Returns:
        {"value": float, "unit": str} 或 None（解析失败时）
    """
    if not text:
        return None

    text = text.strip()

    # 匹配数值 + 可选单位
    match = re.match(r"^([\d,.]+)\s*([A-Za-z%\/]+(?:\s*[A-Za-z0-9]+)?)?", text)
    if not match:
        return None

    num_str = match.group(1).replace(",", "")
    unit = (match.group(2) or "").strip()

    try:
        value = float(num_str)
    except ValueError:
        return None

    return {"value": value, "unit": unit}


def parse_grade(text: str) -> Optional[Dict[str, Any]]:
    """解析品位字符串

    示例:
        "1.2% Li2O" -> {"value": 1.2, "unit": "% Li2O"}
        "1.2%" -> {"value": 1.2, "unit": "%"}
    """
    if not text:
        return None

    text = text.strip()
    match = re.match(r"^([\d,.]+)\s*%?\s*(Li2O|Li|Fe|Cu|Au|Ag)?", text, re.IGNORECASE)
    if not match:
        return None

    num_str = match.group(1).replace(",", "")
    try:
        value = float(num_str)
    except ValueError:
        return None

    metal = match.group(2)
    unit = f"% {metal}" if metal else "%"

    return {"value": value, "unit": unit}


def is_resource_table_row(row: List[str]) -> bool:
    """判断表格行是否为资源量数据行

    通过检查行中是否包含资源量分类关键词来判断。

    Args:
        row: pdfplumber 提取的表格行（单元格列表）

    Returns:
        True 如果该行包含资源量分类关键词
    """
    if not row:
        return False

    row_text = " ".join(str(cell) for cell in row if cell)
    for category in RESOURCE_CATEGORIES:
        if category.lower() in row_text.lower():
            return True

    return False


def extract_category_from_row(row: List[str]) -> Optional[str]:
    """从表格行中提取资源量分类"""
    row_text = " ".join(str(cell) for cell in row if cell)
    for category in RESOURCE_CATEGORIES:
        if category.lower() in row_text.lower():
            return category
    return None
