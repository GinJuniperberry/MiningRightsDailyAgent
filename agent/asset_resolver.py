"""矿权资产配置解析器

根据项目名/公司名/矿种匹配 assets.yaml 中的资产配置，
补全 PDF URL、别名、公司、矿种等信息。
"""
import os
import yaml
from typing import Dict, Any

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def load_assets_config() -> Dict[str, Any]:
    """加载 assets.yaml 配置

    Returns:
        assets 配置字典
    """
    config_path = os.path.join(_PROJECT_ROOT, "configs", "assets.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def resolve_asset_by_query(project: str = "",
                           company: str = "",
                           commodity: str = "",
                           query: str = "") -> Dict[str, Any]:
    """根据项目名/公司名匹配 assets.yaml 中的资产配置

    匹配策略：
    1. 精确匹配 project 或 company
    2. 模糊匹配 aliases（不区分大小写）
    3. 匹配失败返回默认值

    Args:
        project: 项目名
        company: 公司名
        commodity: 矿种
        query: 用户原始查询，用于匹配项目别名

    Returns:
        资产配置字典，含 aliases, company, commodity, pdf_urls, keywords
    """
    config = load_assets_config()
    assets = config.get("assets", {})

    # 收集所有输入文本用于匹配
    search_terms = [
        project.lower().strip(),
        company.lower().strip(),
        query.lower().strip(),
    ]
    search_terms = [t for t in search_terms if t]

    # 遍历所有资产配置，尝试匹配
    for asset_key, asset_config in assets.items():
        # 精确匹配 key
        if project and project.lower() == asset_key.lower():
            return _with_project(asset_key, asset_config)

        # 匹配 company
        if company and company.lower() == asset_config.get("company", "").lower():
            return _with_project(asset_key, asset_config)

        # 模糊匹配 aliases
        aliases = [a.lower() for a in asset_config.get("aliases", [])]
        for term in search_terms:
            if term in aliases:
                return _with_project(asset_key, asset_config)
            # 部分匹配
            for alias in aliases:
                if term and (term in alias or alias in term):
                    return _with_project(asset_key, asset_config)

    # 匹配失败，返回默认值
    return {
        "project": project or "unknown",
        "aliases": [project] if project else [],
        "company": company or "Unknown",
        "commodity": commodity or "unknown",
        "pdf_urls": [],
        "keywords": [],
    }


def _with_project(asset_key: str, asset_config: Dict[str, Any]) -> Dict[str, Any]:
    """返回资产配置副本，并补充稳定的项目名称。"""
    aliases = asset_config.get("aliases", [])
    project = aliases[0] if aliases else asset_key.replace("_", " ").title()
    return {**asset_config, "project": project}
