"""mineral-pdf-mcp Mock 兜底数据

当真实 PDF 下载或解析失败时，使用这些样例数据保证 demo 可运行。
数据基于 Pilbara Minerals Pilgangoora 项目的公开资源量报告。
"""

MOCK_RESOURCES = {
    "project": "Pilbara",
    "report_url": "",
    "resources": [
        {
            "category": "Indicated",
            "ore_tonnage": {"value": 120.5, "unit": "Mt"},
            "grade": {"value": 1.20, "unit": "% Li2O"},
            "contained_metal": {"value": 1.45, "unit": "Mt Li2O"},
            "page": 128,
            "confidence": 0.86
        },
        {
            "category": "Inferred",
            "ore_tonnage": {"value": 45.2, "unit": "Mt"},
            "grade": {"value": 1.00, "unit": "% Li2O"},
            "contained_metal": {"value": 0.45, "unit": "Mt Li2O"},
            "page": 129,
            "confidence": 0.81
        },
        {
            "category": "Measured",
            "ore_tonnage": {"value": 52.8, "unit": "Mt"},
            "grade": {"value": 1.28, "unit": "% Li2O"},
            "contained_metal": {"value": 0.68, "unit": "Mt Li2O"},
            "page": 127,
            "confidence": 0.92
        }
    ],
    "warnings": []
}
