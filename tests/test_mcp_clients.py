"""MCP 客户端生命周期测试。"""
import pytest

from agent import mcp_clients


@pytest.mark.asyncio
async def test_call_tool_once_always_closes_client(monkeypatch):
    events = []

    class FakeClient:
        def __init__(self, server_name, config):
            events.append(("init", server_name, config))

        async def call_tool(self, tool_name, arguments):
            events.append(("call", tool_name, arguments))
            return {"ok": True}

        async def close(self):
            events.append(("close",))

    monkeypatch.setattr(mcp_clients, "MCPToolClient", FakeClient)
    monkeypatch.setattr(mcp_clients, "_load_mcp_config", lambda name: {"name": name})

    result = await mcp_clients._call_tool_once(
        "test-server", "test-tool", {"value": 1}
    )

    assert result == {"ok": True}
    assert [event[0] for event in events] == ["init", "call", "close"]


@pytest.mark.asyncio
async def test_call_tool_once_closes_client_after_failure(monkeypatch):
    closed = False

    class FailingClient:
        def __init__(self, server_name, config):
            pass

        async def call_tool(self, tool_name, arguments):
            raise RuntimeError("tool failed")

        async def close(self):
            nonlocal closed
            closed = True

    monkeypatch.setattr(mcp_clients, "MCPToolClient", FailingClient)
    monkeypatch.setattr(mcp_clients, "_load_mcp_config", lambda name: {})

    with pytest.raises(RuntimeError, match="tool failed"):
        await mcp_clients._call_tool_once("test-server", "test-tool", {})

    assert closed is True
