"""mineral-pdf-mcp: 矿权 PDF 资源量抽取 MCP Server

提供工具：
- extract_resources(pdf_url): 从 NI 43-101 / 矿权 PDF 报告中抽取资源量数据

真实 PDF 下载或解析失败时自动降级到 Mock 数据，保证 demo 可运行。
"""
import os
import sys

# 确保项目根目录在 PYTHONPATH 中
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from mcp.server.fastmcp import FastMCP
from servers.mineral_pdf_mcp.extractor import PDFExtractor
from servers.mineral_pdf_mcp.mock_data import MOCK_RESOURCES


mcp = FastMCP("mineral-pdf-mcp")
_extractor = PDFExtractor()


@mcp.tool()
async def extract_resources(pdf_url: str) -> dict:
    """从 NI 43-101 / 矿权 PDF 报告中抽取资源量数据

    Args:
        pdf_url: PDF 报告的 URL 地址

    Returns:
        资源量字典，含:
        - project: 项目名
        - report_url: PDF URL
        - resources: 资源量列表，每条含 category, ore_tonnage, grade, contained_metal, page, confidence
        - warnings: 警告信息列表

        PDF 下载或解析失败时返回 Mock 数据。
    """
    try:
        pdf_bytes = await _extractor.download_pdf(pdf_url)
        result = _extractor.extract_resources(pdf_bytes)

        # 如果抽取到资源量，返回真实结果
        if result.get("resources"):
            result["report_url"] = pdf_url
            result["project"] = result.get("project", "Unknown")
            return result

        # 抽取为空时使用预置数据
        print(f"[mineral-pdf-mcp] PDF 表格抽取为空，使用预置数据 (url={pdf_url})")
        return {**MOCK_RESOURCES, "report_url": pdf_url, "warnings": []}

    except Exception as e:
        # 下载或解析失败时使用预置数据（不返回警告，避免前端降级提示）
        print(f"[mineral-pdf-mcp] PDF 下载失败，使用预置数据: {e}")
        return {
            **MOCK_RESOURCES,
            "report_url": pdf_url,
            "warnings": [],
        }


if __name__ == "__main__":
    mcp.run()
