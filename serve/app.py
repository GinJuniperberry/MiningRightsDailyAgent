"""矿权日报 Agent FastAPI 后端

提供 REST + SSE API，封装 LangGraph Agent，供前端调用。

API 端点：
- POST /api/briefings — 创建日报任务
- GET /api/briefings/{task_id}/events — SSE 实时事件流
- GET /api/briefings/{task_id} — 获取报告详情
- GET /api/briefings/{task_id}/download — 下载 Markdown
- GET /api/briefings — 获取历史报告列表
"""
import os
import sys
import json
import asyncio
import uuid
from datetime import datetime, date
from typing import Dict, Any, List, Optional
from collections import OrderedDict

# 确保项目根目录在 PYTHONPATH 中
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, Response, JSONResponse
from pydantic import BaseModel

load_dotenv()

from agent.graph import build_graph
from agent.mcp_clients import close_all_clients

app = FastAPI(title="矿权日报 Agent API", version="1.0.0")

# 允许前端跨域（开发环境）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ 数据模型 ============

class CreateBriefingRequest(BaseModel):
    query: str


class CreateBriefingResponse(BaseModel):
    task_id: str
    status: str


# ============ 内存存储 ============

class TaskStore:
    """内存任务存储（demo 版，重启后丢失）"""

    def __init__(self):
        self._tasks: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        self._events: Dict[str, List[Dict[str, Any]]] = {}
        self._event_subscribers: Dict[str, List[asyncio.Queue]] = {}

    def create_task(self, query: str) -> str:
        """创建新任务，返回 task_id"""
        task_id = f"briefing_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        self._tasks[task_id] = {
            "task_id": task_id,
            "query": query,
            "status": "running",
            "created_at": datetime.now().isoformat(),
            "finished_at": None,
            "result": None,
            "warnings": [],
        }
        self._events[task_id] = []
        self._event_subscribers[task_id] = []
        return task_id

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        return self._tasks.get(task_id)

    def update_task(self, task_id: str, **kwargs):
        if task_id in self._tasks:
            self._tasks[task_id].update(kwargs)

    def list_tasks(self, page: int = 1, page_size: int = 20,
                   keyword: str = "") -> Dict[str, Any]:
        """分页获取任务列表"""
        items = list(self._tasks.values())
        # 按创建时间倒序
        items.sort(key=lambda x: x.get("created_at", ""), reverse=True)

        # 关键词过滤
        if keyword:
            kw = keyword.lower()
            items = [
                t for t in items
                if kw in t.get("query", "").lower()
                or kw in str(t.get("result", {}).get("project", "")).lower()
                or kw in str(t.get("result", {}).get("commodity", "")).lower()
            ]

        total = len(items)
        start = (page - 1) * page_size
        end = start + page_size
        page_items = items[start:end]

        # 转换为列表项格式
        list_items = []
        for t in page_items:
            result = t.get("result") or {}
            list_items.append({
                "task_id": t["task_id"],
                "title": _build_title(result.get("project", ""), result.get("commodity", "")),
                "project": result.get("project", ""),
                "commodity": result.get("commodity", ""),
                "status": t["status"],
                "created_at": t["created_at"],
                "warning_count": len(result.get("warnings", [])),
            })

        return {"items": list_items, "total": total}

    def add_event(self, task_id: str, event: Dict[str, Any]):
        """添加事件并通知所有订阅者"""
        if task_id not in self._events:
            self._events[task_id] = []
        self._events[task_id].append(event)

        # 通知订阅者
        for queue in self._event_subscribers.get(task_id, []):
            try:
                queue.put_nowait(event)
            except asyncio.QueueFull:
                pass

    def get_events(self, task_id: str) -> List[Dict[str, Any]]:
        return self._events.get(task_id, [])

    def subscribe(self, task_id: str) -> asyncio.Queue:
        """订阅任务事件"""
        if task_id not in self._event_subscribers:
            self._event_subscribers[task_id] = []
        queue: asyncio.Queue = asyncio.Queue(maxsize=1000)
        self._event_subscribers[task_id].append(queue)
        return queue

    def unsubscribe(self, task_id: str, queue: asyncio.Queue):
        """取消订阅"""
        if task_id in self._event_subscribers:
            try:
                self._event_subscribers[task_id].remove(queue)
            except ValueError:
                pass


store = TaskStore()


# ============ 节点名称映射 ============

NODE_LABELS = {
    "parse_intent": "解析用户输入",
    "resolve_asset": "识别矿权信息",
    "search_news": "搜索矿业新闻",
    "expand_news_days": "扩大搜索范围",
    "fetch_articles": "抓取新闻正文",
    "extract_resources": "抽取资源量数据",
    "fetch_price": "获取价格行情",
    "analyze_context": "聚合上下文",
    "generate_risks": "生成风险提示",
    "render_report": "渲染日报",
    "quality_check": "质量检查",
    "revise_report": "修订报告",
    "save_report": "保存报告",
    "save_report_with_warnings": "保存报告（带警告）",
}


def _build_title(project: str, commodity: str) -> str:
    """构建报告标题"""
    if project and commodity:
        return f"{project} {commodity} 日报"
    elif project:
        return f"{project} 日报"
    return "矿权日报"


def _build_report_response(task: Dict[str, Any]) -> Dict[str, Any]:
    """从任务结果构建报告响应"""
    result = task.get("result") or {}
    project = result.get("project", "")
    commodity = result.get("commodity", "")
    markdown = result.get("markdown", "")
    warnings = result.get("warnings", [])

    # 解析结构化数据
    articles = result.get("articles", [])
    news_items = result.get("news_items", [])
    resources = result.get("resources", {})
    resource_list = resources.get("resources", [])
    latest_price = result.get("latest_price", {})
    price_trend = result.get("price_trend", {})
    risks = result.get("risks", [])

    # 构建引用源
    citations = []
    for item in articles + news_items:
        url = item.get("url", "")
        if url and url not in [c["url"] for c in citations]:
            citations.append({
                "title": item.get("title", url),
                "url": url,
                "type": "news",
            })
    if resources.get("report_url"):
        citations.append({
            "title": "资源量报告 PDF",
            "url": resources["report_url"],
            "type": "pdf",
        })
    if latest_price.get("source"):
        citations.append({
            "title": f"价格数据源: {latest_price['source']}",
            "url": "#",
            "type": "price",
        })

    return {
        "task_id": task["task_id"],
        "title": _build_title(project, commodity),
        "project": project,
        "commodity": commodity,
        "status": task["status"],
        "created_at": task["created_at"],
        "finished_at": task.get("finished_at"),
        "markdown": markdown,
        "summary": {
            "news_count": len(articles) if articles else len(news_items),
            "resource_available": len(resource_list) > 0,
            "price_available": bool(latest_price or price_trend),
            "warning_count": len(warnings),
        },
        "sections": {
            "news": (articles if articles else news_items)[:5],
            "resources": resource_list,
            "price": {
                "commodity": commodity,
                "latest_price": latest_price.get("price", 0),
                "unit": latest_price.get("unit", ""),
                "change_pct": price_trend.get("change_pct", 0),
                "ma_7": price_trend.get("ma_7", 0),
                "ma_30": price_trend.get("ma_30", 0),
                "trend": price_trend.get("trend", "flat"),
                "observations": price_trend.get("observations", []),
            },
            "risks": risks,
        },
        "citations": citations,
        "warnings": warnings,
    }


# ============ LangGraph 执行器 ============

async def run_briefing_task(task_id: str, query: str):
    """后台执行 LangGraph 任务，发射事件到 SSE

    使用 graph.astream() 的双流模式同时获取节点更新和完整状态快照，
    避免重复执行图（旧代码 astream + ainvoke 会执行两遍）。
    """
    graph = build_graph()
    initial_state = {"user_query": query}

    final_state = None

    try:
        # 双流模式：updates 获取节点事件，values 获取完整状态快照
        async for chunk in graph.astream(initial_state, stream_mode=["updates", "values"]):
            mode, data = chunk

            if mode == "values":
                # data 是完整状态快照，保留最后一个作为最终结果
                final_state = data
                continue

            # mode == "updates"
            # data 是 {node_name: state_update} 格式
            for node_name, state_update in data.items():
                if node_name == "__end__":
                    continue

                label = NODE_LABELS.get(node_name, node_name)
                timestamp = datetime.now().isoformat()

                # 节点开始事件
                store.add_event(task_id, {
                    "type": "node_start",
                    "node": node_name,
                    "message": f"开始执行：{label}",
                    "timestamp": timestamp,
                })

                # 检查是否有警告
                warnings = state_update.get("warnings", [])
                errors = state_update.get("errors", [])

                if errors:
                    store.add_event(task_id, {
                        "type": "node_warning",
                        "node": node_name,
                        "message": f"{label} 执行中出现错误",
                        "timestamp": datetime.now().isoformat(),
                    })
                elif warnings and node_name in ("search_news", "extract_resources", "fetch_price"):
                    store.add_event(task_id, {
                        "type": "node_warning",
                        "node": node_name,
                        "message": f"{label} 降级处理，使用兜底数据",
                        "timestamp": datetime.now().isoformat(),
                    })

                # 节点成功事件
                msg = _build_node_message(node_name, state_update)
                store.add_event(task_id, {
                    "type": "node_success",
                    "node": node_name,
                    "message": msg,
                    "payload": _extract_payload(node_name, state_update),
                    "timestamp": datetime.now().isoformat(),
                })

        # 使用最后一次 values 快照作为最终结果
        if final_state is None:
            # 理论上不会发生，但作为兜底
            final_state = {"user_query": query, "warnings": ["未能获取最终状态"]}

        store.update_task(
            task_id,
            status="success",
            finished_at=datetime.now().isoformat(),
            result=final_state,
        )

        store.add_event(task_id, {
            "type": "task_done",
            "task_id": task_id,
            "report_url": f"/api/briefings/{task_id}",
            "timestamp": datetime.now().isoformat(),
        })

    except Exception as e:
        store.update_task(
            task_id,
            status="failed",
            finished_at=datetime.now().isoformat(),
        )
        store.add_event(task_id, {
            "type": "task_failed",
            "task_id": task_id,
            "message": str(e),
            "timestamp": datetime.now().isoformat(),
        })
    finally:
        await close_all_clients()


def _build_node_message(node_name: str, state_update: Dict[str, Any]) -> str:
    """构建节点成功消息"""
    label = NODE_LABELS.get(node_name, node_name)

    if node_name == "parse_intent":
        project = state_update.get("project", "")
        return f"识别到项目：{project}" if project else "意图解析完成"

    if node_name == "search_news":
        items = state_update.get("news_items", [])
        return f"找到 {len(items)} 条相关新闻"

    if node_name == "fetch_articles":
        articles = state_update.get("articles", [])
        return f"抓取 {len(articles)} 篇新闻正文"

    if node_name == "extract_resources":
        resources = state_update.get("resources", {})
        count = len(resources.get("resources", []))
        return f"抽取到 {count} 条资源量数据" if count else "资源量数据待人工复核"

    if node_name == "fetch_price":
        price = state_update.get("latest_price", {})
        return f"获取价格数据：{price.get('price', 'N/A')}" if price else "价格数据不可用"

    if node_name == "render_report":
        return "Markdown 报告生成完成"

    if node_name == "quality_check":
        score = state_update.get("quality_score", 0)
        return f"质检分数：{score}"

    if node_name == "save_report":
        return "报告已保存"

    return f"{label} 完成"


def _extract_payload(node_name: str, state_update: Dict[str, Any]) -> Dict[str, Any]:
    """提取节点负载信息"""
    if node_name == "search_news":
        return {"count": len(state_update.get("news_items", []))}
    if node_name == "extract_resources":
        return {"count": len(state_update.get("resources", {}).get("resources", []))}
    if node_name == "quality_check":
        return {"score": state_update.get("quality_score", 0)}
    return {}


# ============ API 端点 ============

@app.post("/api/briefings", response_model=CreateBriefingResponse)
async def create_briefing(request: CreateBriefingRequest):
    """创建日报任务"""
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="查询不能为空")

    task_id = store.create_task(request.query)

    # 后台执行任务
    asyncio.create_task(run_briefing_task(task_id, request.query))

    return CreateBriefingResponse(task_id=task_id, status="running")


@app.get("/api/briefings/{task_id}/events")
async def briefing_events(task_id: str):
    """SSE 实时事件流"""
    task = store.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    queue = store.subscribe(task_id)

    async def event_generator():
        try:
            # 先发送已完成的事件（重连场景）
            for event in store.get_events(task_id):
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

            # 如果任务已结束，直接关闭
            if task["status"] in ("success", "failed"):
                return

            # 监听新事件
            while True:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=30)
                    yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

                    if event.get("type") in ("task_done", "task_failed"):
                        break
                except asyncio.TimeoutError:
                    # 发送心跳
                    yield f": heartbeat\n\n"
        finally:
            store.unsubscribe(task_id, queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/api/briefings/{task_id}")
async def get_briefing(task_id: str):
    """获取报告详情"""
    task = store.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    if task["status"] == "running":
        return JSONResponse(
            status_code=202,
            content={"task_id": task_id, "status": "running", "message": "任务仍在执行中"}
        )

    return _build_report_response(task)


@app.get("/api/briefings/{task_id}/download")
async def download_briefing(task_id: str):
    """下载 Markdown 报告"""
    task = store.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    result = task.get("result") or {}
    markdown = result.get("markdown", "")
    project = result.get("project", "briefing")
    today = date.today().isoformat()

    filename = f"{project.lower().replace(' ', '_')}_daily_briefing_{today}.md"

    return Response(
        content=markdown,
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.get("/api/briefings")
async def list_briefings(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str = Query(""),
):
    """获取历史报告列表"""
    return store.list_tasks(page, page_size, keyword)


@app.get("/api/health")
async def health():
    """健康检查"""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
