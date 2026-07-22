"""PDF 资源量抽取器

从 NI 43-101 / 矿权报告 PDF 中抽取 Indicated / Inferred 资源量数据。

解析策略：
1. 用 httpx 下载 PDF 到内存（缓存到 data/cache）
2. 用 pdfplumber 扫描所有页面的表格
3. 匹配含 "Indicated" / "Inferred" / "Measured" 的表格
4. 提取矿石量、品位、金属量字段
5. 失败时由 server.py 降级到 Mock 数据
"""
import os
import io
import hashlib
import re
import httpx
import pdfplumber
from typing import Dict, Any, List, Optional

from servers.mineral_pdf_mcp.table_parser import (
    parse_quantity,
    parse_grade,
    is_resource_table_row,
    extract_category_from_row,
)

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_CACHE_DIR = os.path.join(_PROJECT_ROOT, "data", "cache")


class PDFExtractor:
    """从 NI 43-101 报告 PDF 中抽取资源量表"""

    async def download_pdf(self, url: str) -> bytes:
        """下载 PDF 到内存，缓存到 data/cache

        Args:
            url: PDF 文件的 URL

        Returns:
            PDF 文件的字节内容

        Raises:
            Exception: 下载失败时抛出异常
        """
        os.makedirs(_CACHE_DIR, exist_ok=True)

        # 用 URL hash 作为缓存文件名
        url_hash = hashlib.md5(url.encode()).hexdigest()
        cache_path = os.path.join(_CACHE_DIR, f"{url_hash}.pdf")

        # 如果缓存存在，直接读取
        if os.path.exists(cache_path):
            with open(cache_path, "rb") as f:
                return f.read()

        # 下载 PDF
        async with httpx.AsyncClient(
            timeout=60,
            follow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0"},
        ) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            pdf_bytes = resp.content

        # 写入缓存
        with open(cache_path, "wb") as f:
            f.write(pdf_bytes)

        return pdf_bytes

    def extract_resources(self, pdf_bytes: bytes) -> Dict[str, Any]:
        """解析 PDF，提取 Indicated/Inferred/Measured 资源量数据

        Args:
            pdf_bytes: PDF 文件的字节内容

        Returns:
            抽取结果字典，含 project, resources 列表, warnings
        """
        resources: List[Dict[str, Any]] = []
        warnings: List[str] = []
        page_texts = []

        try:
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    page_text = page.extract_text() or ""
                    page_texts.append(page_text)

                    tables = page.extract_tables()
                    for table in tables or []:
                        for row in table:
                            if not is_resource_table_row(row):
                                continue

                            entry = self._parse_resource_row(row, page_num)
                            if entry:
                                resources.append(entry)

                    # 部分 ASX PDF 的数值与分类在视觉上属于同一行，但
                    # extract_tables() 会把它们拆散；此时从页面文本补抽。
                    resources.extend(
                        self._parse_resource_text(page_text, page_num)
                    )

        except Exception as e:
            warnings.append(f"PDF 表格解析出错: {e}")

        # 去重：同一分类只保留第一个
        seen_categories = set()
        unique_resources = []
        for r in resources:
            cat = r["category"]
            if cat not in seen_categories:
                seen_categories.add(cat)
                unique_resources.append(r)

        project = self._detect_project("\n".join(page_texts))
        return {
            "project": project,
            "resources": unique_resources,
            "warnings": warnings,
        }

    @staticmethod
    def _parse_resource_text(text: str, page_num: int) -> List[Dict[str, Any]]:
        """从 PDF 页面文本中解析标准 JORC 资源量数据行。"""
        pattern = re.compile(
            r"\b(Measured|Indicated|Inferred|Stockpiles)\s+"
            r"(?:In-situ\s+)?"
            r"(\d+(?:\.\d+)?)\s+"       # Tonnage (Mt)
            r"(\d+(?:\.\d+)?)\s+"       # Grade (% Li2O)
            r"\d[\d,.]*\s+"              # Grade (ppm Ta2O5)
            r"(\d[\d,.]*)\s+"            # Contained metal ('000 t Li2O)
            r"\d[\d,.]*\s+"              # Contained metal (lbs Ta2O5)
            r"[-+]?\d+(?:\.\d+)?%",
            re.IGNORECASE,
        )

        entries = []
        for match in pattern.finditer(text):
            category = match.group(1).title()
            if category == "Stockpiles":
                category = "Indicated (Stockpiles)"
            entries.append({
                "category": category,
                "ore_tonnage": {
                    "value": float(match.group(2)),
                    "unit": "Mt",
                },
                "grade": {
                    "value": float(match.group(3)),
                    "unit": "% Li2O",
                },
                "contained_metal": {
                    "value": float(match.group(4).replace(",", "")),
                    "unit": "kt Li2O",
                },
                "page": page_num,
                "confidence": 0.85,
            })
        return entries

    @staticmethod
    def _detect_project(text: str) -> str:
        """从报告正文识别当前已配置的矿权项目。"""
        known_projects = {
            "mount cattlin": "Mount Cattlin",
            "mt cattlin": "Mount Cattlin",
            "pilgangoora": "Pilgangoora",
            "greenbushes": "Greenbushes",
        }
        lowered = text.lower()
        for marker, project in known_projects.items():
            if marker in lowered:
                return project
        return "Unknown"

    def _parse_resource_row(self, row: List[Optional[str]],
                            page_num: int) -> Optional[Dict[str, Any]]:
        """解析单行资源量数据

        Args:
            row: pdfplumber 提取的表格行
            page_num: 页码

        Returns:
            资源量条目字典，或 None（解析失败时）
        """
        category = extract_category_from_row(row)
        if not category:
            return None

        # 清理单元格
        cells = [str(cell).strip() if cell else "" for cell in row]

        # 尝试从行中提取数值
        quantities: List[Dict[str, Any]] = []
        for cell in cells:
            if cell and cell != category:
                q = parse_quantity(cell)
                if q and q["value"] > 0:
                    quantities.append(q)

        if len(quantities) < 2:
            return None

        # 假设第一个数值是矿石量，第二个是品位
        ore_tonnage = quantities[0]
        grade = quantities[1] if len(quantities) > 1 else {"value": 0, "unit": ""}

        # 如果有第三个数值，作为金属量；否则计算
        if len(quantities) >= 3:
            contained_metal = quantities[2]
        else:
            # 金属量 = 矿石量 * 品位
            metal_value = ore_tonnage["value"] * grade["value"] / 100
            contained_metal = {"value": round(metal_value, 2), "unit": f"M{ore_tonnage['unit']}"}

        # 判断品位单位是否含 Li2O
        grade_text = " ".join(cells)
        if "Li2O" in grade_text:
            grade["unit"] = "% Li2O"

        return {
            "category": category,
            "ore_tonnage": ore_tonnage,
            "grade": grade,
            "contained_metal": contained_metal,
            "page": page_num,
            "confidence": 0.75,  # 规则解析的默认置信度
        }
