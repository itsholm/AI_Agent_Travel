# 智能旅行规划助手 (AI Travel Agent)

基于**多智能体协作**与 **MCP（Model Context Protocol）** 的智能旅行规划系统。用户输入目的地、日期与偏好后，系统自动调用天气、景点、酒店等专家 Agent，结合高德地图与 Unsplash 数据，生成结构化行程（含每日景点及图片、住宿、餐饮、天气与预算），并提供可编辑的可视化前端。

---

## 功能概览

- **多智能体协作**：天气专家、景点专家、酒店专家、行程规划专家分工协作，按流程生成行程
- **真实数据接入**：高德地图（POI 搜索、天气、路线、周边）、Unsplash（景点配图）
- **结构化输出**：Pydantic Schema 约束 LLM 输出，保证行程 JSON 可解析、可校验
- **预算后处理**：后端根据行程内容自动汇总门票、酒店、餐饮、交通预算
- **前端能力**：行程概览、预算卡片、地图展示、天气预报、每日行程折叠、景点图片异步加载、行程编辑（调整顺序/删除景点）

---

## 技术栈

| 层级     | 技术 |
|----------|------|
| 后端 API | FastAPI、Uvicorn |
| 大模型   | OpenAI API（兼容 OpenAI 协议的大模型） |
| Agent    | 自研 ReAct + Tool Calling 循环、多 Agent 编排（TripMaster） |
| 工具协议 | MCP（Model Context Protocol），FastMCP 实现工具端 |
| 数据模型 | Pydantic（请求/响应 Schema 统一） |
| 外部服务 | 高德地图 Web 服务 API、Unsplash API |
| 前端     | Vue 3、TypeScript、Vite、Ant Design Vue、高德 JS API（地图） |

---

## 项目结构

```
MCP/
├── app/                          # 后端（运行与工作目录）
│   ├── api.py                    # FastAPI 入口、路由、MCP 生命周期
│   ├── trip_planner.py           # 多智能体编排 TripMaster
│   ├── SimpleAgent.py           # Agent 基类（ReAct + 工具调用）
│   ├── llm_client.py             # LLM 调用封装（OpenAI SDK）
│   ├── system_prompt.py          # 各专家 Agent 的 system prompt
│   ├── amap_mcp.py              # MCP 客户端封装（AmapMCPBatch / AmapMCPTool）
│   ├── models/
│   │   └── schemas.py            # Pydantic 模型（TripRequest, TripPlan, DayPlan 等）
│   ├── services/                 # MCP 服务端（子进程方式运行）
│   │   ├── amap_mcp_service.py   # 高德地图 MCP 工具
│   │   └── unsplash_mcp_service.py  # Unsplash 搜图 MCP 工具
│   ├── tools/
│   │   └── registry.py          # 工具注册表（ToolRegistry）
│   ├── .env.example              # 环境变量示例（需自行复制为 .env）
│   └── test_api.py              # 接口测试脚本
├── frontend/                     # 前端
│   ├── src/
│   │   ├── App.vue              # 主页面（表单 + 结果展示）
│   │   ├── main.ts
│   │   ├── request.ts           # axios 封装
│   │   ├── types/travel.ts      # 前端类型定义
│   │   └── components/
│   │       ├── TravelResult.vue # 行程结果（概览、预算、地图、天气、每日行程）
│   │       └── AMapView.vue     # 高德地图组件
│   ├── index.html
│   ├── package.json
│   └── vite.config.ts           # 开发代理 /api -> http://127.0.0.1:8000
├── README.md
├── requirements.txt             # Python 依赖
└── .gitignore
```

---

## 环境要求

- **Python**：3.10+
- **Node.js**：18+（用于前端开发与构建）
- **密钥与配置**：高德 API Key、Unsplash Access Key、LLM API（OpenAI 或兼容端点）

---

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/你的用户名/你的仓库名.git
cd 你的仓库名
```

### 2. 后端配置与运行

```bash
# 进入后端目录
cd app

# 创建虚拟环境（推荐）
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
# source venv/bin/activate

# 安装依赖（依赖文件在项目根目录）
pip install -r ../requirements.txt

# 配置环境变量：复制示例并填写
copy .env.example .env   # Windows
# cp .env.example .env   # macOS/Linux
# 编辑 .env，填入 LLM_API_KEY、LLM_BASE_URL、LLM_MODEL_ID、AMAP_API_KEY、UNSPLASH_ACCESS_KEY
```

**.env 示例（`app/.env`）**

```env
# LLM（OpenAI 或兼容 API）
LLM_API_KEY=your_api_key
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL_ID=gpt-4o

# 高德地图
AMAP_API_KEY=your_amap_key

# Unsplash
UNSPLASH_ACCESS_KEY=your_unsplash_key
```

**启动后端**

```bash
# 确保当前在 app 目录下
uvicorn api:app --host 0.0.0.0 --port 8000
```

后端启动后会拉取 MCP 工具列表并初始化多 Agent，控制台出现“服务初始化完成”即表示就绪。

### 3. 前端配置与运行

```bash
# 在项目根目录
cd frontend

# 安装依赖
npm install

# 开发模式（默认代理 /api 到 http://127.0.0.1:8000）
npm run dev
```

浏览器访问 `http://localhost:5173`，填写目的地、日期、偏好后提交，即可看到生成的行程与地图、预算、天气等。

### 4. 生产构建（可选）

```bash
cd frontend
npm run build
# 将 dist 目录部署到任意静态服务器，并配置 /api 反向代理到后端 8000 端口
```

---

## API 说明

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/plan` | 提交旅行需求，返回结构化行程（TripPlan）。请求体为 TripRequest（city, start_date, end_date, travel_days, transportation, accommodation, preferences, free_text_input） |
| GET  | `/api/poi/photo?name=景点名` | 根据景点名称获取配图 URL（通过 Unsplash MCP 工具） |

---

## 环境变量汇总

| 变量 | 说明 | 必填 |
|------|------|------|
| `LLM_API_KEY` | LLM 服务 API Key | 是 |
| `LLM_BASE_URL` | LLM 服务 Base URL（如 OpenAI） | 是 |
| `LLM_MODEL_ID` | 模型 ID（如 gpt-4o） | 是 |
| `AMAP_API_KEY` | 高德 Web 服务 Key | 是 |
| `UNSPLASH_ACCESS_KEY` | Unsplash API Access Key | 是（用于景点配图） |

---

## 测试

在后端已启动的前提下，可在项目根目录或 `app` 目录执行：

```bash
cd app
python test_api.py
```

用于验证 `/api/plan` 的请求与响应是否符合预期。

---

## 常见问题

1. **MCP 子进程启动失败**  
   确保在 `app` 目录下执行 `uvicorn api:app`，这样 `services/amap_mcp_service.py` 等相对路径才能正确找到。

2. **前端请求 /api 报错**  
   确认后端已监听 `http://127.0.0.1:8000`，且 `frontend/vite.config.ts` 中 proxy 的 target 为 `http://127.0.0.1:8000`。

3. **行程生成失败或格式错误**  
   检查 LLM 配置与网络；若返回 JSON 不完整，可查看后端日志中的原始 LLM 输出与 Pydantic 校验错误。

4. **地图或图片不显示**  
   高德地图需在开放平台配置 Key 与域名；Unsplash 需有效 Access Key，且 `app/.env` 中 `UNSPLASH_ACCESS_KEY` 已配置。

---

## 许可证

MIT
