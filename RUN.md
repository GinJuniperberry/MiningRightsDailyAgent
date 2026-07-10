# RUN.md — 矿权日报 Agent 运行说明

## 1. 环境要求

| 依赖 | 版本 | 说明 |
|------|------|------|
| Python | 3.11+ | 后端 Agent / MCP Server / FastAPI |
| pip | 最新 | Python 包管理 |
| Node.js | 18+ / 20+ | 前端构建（仅前后端分离或前端开发时需要） |
| npm / pnpm | npm 9+ | 前端包管理 |
| Docker & Docker Compose | 最新（可选） | 一键容器化部署 |
| 通义千问 API Key | 可选 | 不配置则走纯规则模式，仍可生成完整日报 |

## 2. 安装依赖

### 2.1 后端依赖

```bash
pip install -r requirements.txt
```

### 2.2 前端依赖（仅前后端分离 / 前端开发时需要）

```bash
cd frontend
npm install
```

## 3. 配置环境变量（可选）

复制 `.env.example` 为 `.env` 并填入通义千问 API Key：

```bash
cp .env.example .env
```

编辑 `.env`：

```text
DASHSCOPE_API_KEY=sk-your-dashscope-api-key
USE_LLM=true
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL=qwen-plus
```

> 不配置 API Key 时，Agent 自动走纯规则模式，仍可生成完整日报（摘要、风险提示由规则模板生成）。

## 4. 启动 Demo

提供三种运行方式，按场景选择：

### 方式一：命令行直跑（最快验证 Agent）

无需启动 Web 服务，直接在终端生成报告：

```bash
python agent/main.py "给我生成一份关于 Pilbara 锂矿的今日简报"
```

报告默认保存到 `reports/` 目录，执行约 57 秒。

### 方式二：Docker 一键启动（前后端完整 Demo）

```bash
docker compose up --build
```

启动后访问：

| 服务 | 地址 |
|------|------|
| 前端 Web | http://localhost:8080 |
| 后端 API | http://localhost:8000 |
| API 健康检查 | http://localhost:8000/api/health |

### 方式三：前后端分离本地开发（推荐调试）

分别启动后端 API 服务和前端开发服务器。

**步骤 1：启动后端 FastAPI 服务（端口 8000）**

```bash
uvicorn serve.app:app --host 0.0.0.0 --port 8000 --reload
```

**步骤 2：启动前端 Vite 开发服务器（端口 5173）**

```bash
cd frontend
npm run dev
```

前端开发服务器已配置代理，`/api` 请求自动转发到 `http://localhost:8000`，无需额外配置跨域。

访问 http://localhost:5173 即可使用 Web 界面。

> 两个终端分别保持运行，修改代码会自动热更新。

## 5. 前端构建与预览

```bash
cd frontend

# 类型检查
npm run check

# 生产构建（输出到 dist/）
npm run build

# 本地预览生产构建
npm run preview
```

## 6. API 接口说明

后端 FastAPI 提供以下 REST 接口：

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/briefings` | 创建日报任务，返回 `task_id` |
| GET | `/api/briefings/{task_id}/events` | SSE 实时事件流（节点进度） |
| GET | `/api/briefings/{task_id}` | 获取报告详情（任务运行中返回 202） |
| GET | `/api/briefings/{task_id}/download` | 下载 Markdown 报告 |
| GET | `/api/briefings` | 获取历史报告列表（支持分页、关键词搜索） |
| GET | `/api/health` | 健康检查 |

### 创建任务示例

```bash
curl -X POST http://localhost:8000/api/briefings \
  -H "Content-Type: application/json" \
  -d '{"query": "给我生成一份关于 Pilbara 锂矿的今日简报"}'
```

返回：

```json
{"task_id": "briefing_20260710_143022_a1b2c3", "status": "running"}
```

### SSE 事件流

通过 `EventSource` 订阅 `/api/briefings/{task_id}/events`，接收事件类型：

| 事件 type | 说明 |
|-----------|------|
| `node_start` | 节点开始执行 |
| `node_success` | 节点执行成功 |
| `node_warning` | 节点降级 / 出现警告 |
| `task_done` | 任务完成 |
| `task_failed` | 任务失败 |

## 7. 单独启动 MCP Server（调试用）

三个 MCP Server 通过 stdio 传输，通常由 Agent 自动拉起。如需单独调试：

```bash
python servers/mining_news_mcp/server.py
python servers/mineral_pdf_mcp/server.py
python servers/lme_price_mcp/server.py
```

## 8. 接入 Claude Desktop / Cursor

将 `configs/mcp-config.json` 内容复制到对应 MCP 配置中：

- Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)
- Cursor: Settings → MCP → Add new MCP Server

## 9. 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 仅运行单元测试（不启动 MCP Server）
pytest tests/test_graph.py tests/test_news_mcp.py tests/test_pdf_mcp.py tests/test_price_mcp.py -v -k "not async"

# 运行端到端测试（需要 MCP Server 可启动）
pytest tests/test_agent_e2e.py -v
```

## 10. 查看报告

报告默认保存到 `reports/` 目录：

```bash
cat reports/pilbara_daily_briefing_2026-07-09.md
```

也可通过 Web 界面下载，或调用 `/api/briefings/{task_id}/download` 接口。

## 11. 端口说明

| 服务 | 端口 | 说明 |
|------|------|------|
| 后端 FastAPI | 8000 | REST + SSE API |
| 前端 Vite dev | 5173 | 开发服务器（代理 /api → 8000） |
| 前端 Nginx（Docker） | 8080 → 80 | 生产容器，反代 /api → backend:8000 |

## 12. 项目结构

```text
mining-rights-daily-agent/
├── servers/              # 3 个 MCP Server
│   ├── mining_news_mcp/  # 新闻采集（search / fetch_article）
│   ├── mineral_pdf_mcp/  # PDF 资源量抽取（extract_resources）
│   └── lme_price_mcp/    # 价格行情（get_price / get_trend）
├── agent/                # LangGraph Agent
│   ├── main.py           # 命令行入口
│   ├── graph.py          # StateGraph 定义（14 节点 + 2 条件路由）
│   ├── state.py          # BriefingState 状态定义
│   ├── nodes.py          # 14 个节点函数
│   ├── routers.py        # 条件路由函数
│   ├── mcp_clients.py    # MCP 客户端封装（stdio 传输）
│   ├── llm_client.py     # 通义千问 LLM 客户端（OpenAI 兼容）
│   ├── report_generator.py # Markdown 报告生成
│   └── quality.py        # 报告质检（规则 + LLM）
├── serve/                # FastAPI 后端服务
│   └── app.py            # REST + SSE API
├── frontend/             # React 前端
│   ├── src/
│   │   ├── pages/        # 4 个页面
│   │   ├── components/   # 通用 + 业务组件
│   │   ├── store/        # Zustand 全局状态
│   │   ├── services/     # API 客户端 + SSE 客户端
│   │   ├── hooks/        # 自定义 Hooks
│   │   └── types/        # TypeScript 类型定义
│   ├── Dockerfile        # 前端多阶段构建
│   └── nginx.conf        # Nginx 配置（SPA + API 反代 + SSE）
├── configs/              # 配置文件
│   ├── assets.yaml       # 矿权资产配置
│   ├── sources.yaml      # 数据源配置
│   └── mcp-config.json   # MCP Server 配置
├── reports/              # 生成的报告
├── tests/                # 测试（44 单元 + 3 E2E）
├── docker-compose.yml    # 容器编排
├── Dockerfile            # 后端镜像
└── requirements.txt
```

## 13. 数据降级说明

系统采用"真实数据源 + Mock 兜底"策略，保证 demo 任何时候可运行：

| 数据源 | 真实来源 | 降级方案 |
|--------|----------|----------|
| 新闻 | RSS 源（mining.com 等） | 内置 Mock 新闻数据（基于 Pilbara 锂矿公开信息） |
| PDF 资源量 | 下载真实 NI 43-101 PDF 解析 | Mock 资源量数据（Indicated / Inferred） |
| 价格行情 | 真实价格 API | Mock 价格 + 趋势数据 |

降级时会在报告中以 `warnings` 字段标注，前端会在警告面板中展示。

## 14. 常见问题

**Q: 启动后端报 `ModuleNotFoundError: No module named 'agent'`？**
A: 确保在项目根目录执行命令，或设置 `PYTHONPATH=.`。

**Q: 前端页面打开后接口报 502 / 连接失败？**
A: 检查后端 8000 端口是否启动；Vite 代理配置在 `frontend/vite.config.ts`。

**Q: Docker 启动后前端访问不到？**
A: 等待后端 healthcheck 通过（约 15 秒），前端容器依赖后端健康。

**Q: 不想配置 LLM API Key 可以吗？**
A: 可以。系统自动走纯规则模式，摘要和风险由模板生成，报告功能完整。
