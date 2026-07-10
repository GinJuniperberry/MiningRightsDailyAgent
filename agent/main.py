"""矿权日报 Agent 入口

使用方式：
    python agent/main.py "给我生成一份关于 Pilbara 锂矿的今日简报"

不传参数时使用默认查询。
"""
import asyncio
import sys
import os

# 加载 .env 环境变量
from dotenv import load_dotenv

load_dotenv()

# 确保项目根目录在 PYTHONPATH 中
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from agent.graph import build_graph
from agent.mcp_clients import close_all_clients


async def main():
    """主入口：解析命令行参数，构建图，执行并输出结果"""
    # 解析查询参数
    query = " ".join(sys.argv[1:]) or "给我生成一份关于 Pilbara 锂矿的今日简报"

    print(f"{'=' * 60}")
    print(f"矿权日报 Agent")
    print(f"查询: {query}")
    print(f"{'=' * 60}\n")

    # 构建 LangGraph
    graph = build_graph()

    try:
        # 执行图
        result = await graph.ainvoke({"user_query": query})

        # 输出结果
        print(f"\n{'=' * 60}")
        print("生成的报告：")
        print(f"{'=' * 60}\n")
        print(result.get("markdown", ""))

        print(f"\n{'=' * 60}")
        print(f"报告路径: {result.get('report_path', '未保存')}")
        print(f"质检分数: {result.get('quality_score', 'N/A')}")
        print(f"修订次数: {result.get('revise_count', 0)}")

        warnings = result.get("warnings", [])
        if warnings:
            print(f"\n警告信息:")
            for w in warnings:
                print(f"  - {w}")

        print(f"{'=' * 60}\n")

    finally:
        # 清理 MCP 客户端连接
        await close_all_clients()


if __name__ == "__main__":
    asyncio.run(main())
