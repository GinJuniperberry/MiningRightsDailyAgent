"""MCP 客户端封装

在 LangGraph node 内调用 MCP tools。基于 stdio transport 与 MCP Server 通信。
提供单例缓存的客户端管理，避免重复创建连接。
"""
import os
import sys
import json
from typing import Dict, Any, Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _load_mcp_config(server_name: str) -> Dict[str, Any]:
    """从 mcp-config.json 加载指定 server 的配置

    Args:
        server_name: MCP Server 名称

    Returns:
        server 配置字典，含 command, args, env
    """
    config_path = os.path.join(_PROJECT_ROOT, "configs", "mcp-config.json")
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    return config["mcpServers"][server_name]


class MCPToolClient:
    """单个 MCP Server 的客户端连接"""

    def __init__(self, server_name: str, config: Dict[str, Any]):
        self.server_name = server_name
        self.config = config
        self.session: Optional[ClientSession] = None
        self._exit_stack: Optional[AsyncExitStack] = None

    async def connect(self):
        """建立与 MCP Server 的 stdio 连接

        启动子进程运行 MCP Server，通过 stdin/stdout 通信。
        """
        self._exit_stack = AsyncExitStack()

        # 构建环境变量（继承当前进程环境 + 配置的 env）
        env = {**os.environ, **self.config.get("env", {})}

        # 确保 PYTHONPATH 包含项目根目录
        pythonpath = env.get("PYTHONPATH", "")
        if _PROJECT_ROOT not in pythonpath:
            env["PYTHONPATH"] = f"{_PROJECT_ROOT};{pythonpath}" if pythonpath else _PROJECT_ROOT

        server_params = StdioServerParameters(
            command=self.config["command"],
            args=self.config["args"],
            env=env,
        )

        stdio_transport = await self._exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        read, write = stdio_transport
        self.session = await self._exit_stack.enter_async_context(
            ClientSession(read, write)
        )
        await self.session.initialize()

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """调用 MCP tool 并返回结果

        Args:
            tool_name: 工具名称
            arguments: 工具参数

        Returns:
            工具返回的 JSON 数据

        Raises:
            Exception: 调用失败时抛出异常
        """
        if not self.session:
            await self.connect()

        result = await self.session.call_tool(tool_name, arguments)

        # MCP 返回的是 content 列表，取第一个 text 内容解析为 JSON
        if result.content:
            for content in result.content:
                if hasattr(content, "text"):
                    try:
                        return json.loads(content.text)
                    except json.JSONDecodeError:
                        return {"raw_text": content.text}

        return {}

    async def close(self):
        """关闭连接，清理资源"""
        if self._exit_stack:
            await self._exit_stack.aclose()
        self.session = None
        self._exit_stack = None


# 全局客户端缓存
_clients: Dict[str, MCPToolClient] = {}


async def get_client(server_name: str) -> MCPToolClient:
    """获取或创建 MCP 客户端（单例缓存）

    Args:
        server_name: MCP Server 名称

    Returns:
        已连接的 MCPToolClient 实例
    """
    if server_name not in _clients:
        config = _load_mcp_config(server_name)
        client = MCPToolClient(server_name, config)
        await client.connect()
        _clients[server_name] = client
    return _clients[server_name]


async def call_mining_news_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """调用 mining-news-mcp 的工具"""
    client = await get_client("mining-news-mcp")
    return await client.call_tool(tool_name, arguments)


async def call_mineral_pdf_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """调用 mineral-pdf-mcp 的工具"""
    client = await get_client("mineral-pdf-mcp")
    return await client.call_tool(tool_name, arguments)


async def call_price_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """调用 lme-price-mcp 的工具"""
    client = await get_client("lme-price-mcp")
    return await client.call_tool(tool_name, arguments)


async def close_all_clients():
    """关闭所有客户端连接"""
    for client in _clients.values():
        try:
            await client.close()
        except Exception as e:
            print(f"[MCPClient] 关闭 {client.server_name} 失败: {e}")
    _clients.clear()
