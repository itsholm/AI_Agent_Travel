
import os
import re
import json
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from datetime import datetime
from models.schemas import TripRequest,TripPlan,Budget


# 导入你之前的组件
from trip_planner import TripMaster
from llm_client import HelloAgentLLM
from dotenv import load_dotenv
#import traceback
load_dotenv()

app = FastAPI(title="智能旅行规划助手")
# 配置允许跨域的列表
origins = [
    "http://localhost:5173", # 你的 Vue 开发环境地址
    "http://127.0.0.1:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      # 允许这些来源
    allow_credentials=True,
    allow_methods=["*"],        # 允许所有方法 (GET, POST 等)
    allow_headers=["*"],        # 允许所有请求头
)

# 全局变量，用于在不同请求间复用
#MCP 服务进程在整个 API 运行期间只启动一次。所有的用户请求都会复用这个已有的连接

mcp_manager = {
    "amap_session": None,
    "unsplash_session": None, # 👈 新增 Unsplash 会话
    "master": None,
    "exit_stack": None
}

@app.on_event("startup")
async def startup_event():
    """应用启动时：建立两个 MCP 连接"""
    from contextlib import AsyncExitStack
    stack = AsyncExitStack()
    mcp_manager["exit_stack"] = stack

    # --- 连接高德服务 ---
    amap_params = StdioServerParameters(
        command="python",
        args=["services/amap_mcp_service.py"],
        env={"AMAP_API_KEY": os.getenv("AMAP_API_KEY")}
    )
    a_read, a_write = await stack.enter_async_context(stdio_client(amap_params))
    amap_session = await stack.enter_async_context(ClientSession(a_read, a_write))
    await amap_session.initialize()
    mcp_manager["amap_session"] = amap_session

    # --- 💡 新增：连接 Unsplash 服务 ---
    unsplash_params = StdioServerParameters(
        command="python",
        args=["services/unsplash_mcp_service.py"], # 👈 确保文件名和路径正确
        env={"UNSPLASH_ACCESS_KEY": os.getenv("UNSPLASH_ACCESS_KEY")}
    )
    u_read, u_write = await stack.enter_async_context(stdio_client(unsplash_params))
    unsplash_session = await stack.enter_async_context(ClientSession(u_read, u_write))
    await unsplash_session.initialize()
    mcp_manager["unsplash_session"] = unsplash_session

    # 3. 初始化 TripMaster (传入高德会话供 Agent 使用)
    llm = HelloAgentLLM()
    master = TripMaster(llm, amap_session) 
    await master.initialize_team()
    mcp_manager["master"] = master
    
    print("🚀 服务初始化完成：高德(地图数据) & Unsplash(视觉增强) 已就绪。")

@app.post("/api/plan")  #高度解耦，它不需要知道MCP存在，也不知道工具有多少
async def create_plan(request: TripRequest):
    """
    接收用户旅行需求，调用 TripMaster 进行规划
    """
    master = mcp_manager["master"]
    if not master:
        raise HTTPException(status_code=500, detail="系统尚未初始化完成")
    
    try:
       # 直接传递对象，不再传递拼凑的字符串
        plan_object = await master.create_plan(request)
        # 2. 💡 核心逻辑：利用对象属性进行数学计算
        # 使用列表推导式优雅地累加各项支出
        calc_attractions = sum(attr.ticket_price for day in plan_object.days for attr in day.attractions)
        calc_hotels = sum(day.hotel.estimated_cost for day in plan_object.days if day.hotel)
        calc_meals = sum(meal.estimated_cost for day in plan_object.days for meal in day.meals)
        
        # 交通费：根据天数计算固定预估值（或保留模型预估值）
        calc_transportation = 50.0 * plan_object.travel_days

        # 3. 更新对象的 budget 属性
        # 实例化新的 Budget 对象并赋值给 plan.budget
        plan_object.budget = Budget(
            total_attractions=int(calc_attractions),
            total_hotels=int(calc_hotels),
            total_meals=int(calc_meals),
            total_transportation=int(calc_transportation),
            total=int(calc_attractions + calc_hotels + calc_meals + calc_transportation)
        )

        # 4. 直接返回 Pydantic 对象,FastAPI 会自动将其序列化为 JSON
        return plan_object
            
    except Exception as e:
        print(f"Plan Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/poi/photo")
async def poi_photo_api(name: str):
    """
    前端异步调用此接口。它不再直接运行函数，而是通过 MCP 协议向 Unsplash 服务发起调用。
    """
    session = mcp_manager["unsplash_session"]
    if not session:
        return {"success": False, "error": "视觉服务未就绪"}
    
    try:
        # 👈 核心修复：使用 call_tool 按照协议名称调用
        result = await session.call_tool("get_poi_photo", arguments={"name": name})
        # MCP 返回的是 content 列表，提取其中的 text (即图片 URL)
        img_url = result.content[0].text if result.content else ""
        
        return {
            "success": True,
            "data": { "photo_url": img_url }
        }
    except Exception as e:
        print(f"Unsplash Call Error: {e}")
        return {"success": False, "error": str(e)}

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时：释放 MCP 连接资源"""
    stack = mcp_manager["exit_stack"]
    if stack:
        await stack.aclose()
    print("👋 系统已安全关闭，资源已释放。")

    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)