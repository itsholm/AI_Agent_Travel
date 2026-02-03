import requests
import json
import time

def test_travel_planner(query):
    url = "http://127.0.0.1:8000/api/plan"
    # 注意：FastAPI 的 create_plan 接收的是 query 参数或 JSON 体
    # 根据你 api.py 的定义: async def create_plan(user_query: str)
    # 如果是路径参数或 Query 参数，采用以下格式：
    params = {"user_query": query}
    
    print(f"\n🚀 正在发送请求: {query}")
    print("-" * 50)
    
    start_time = time.time()
    try:
        # 发送 POST 请求
        response = requests.post(url, params=params, timeout=120)
        
        # 检查响应状态
        if response.status_code == 200:
            result = response.json()
            elapsed_time = time.time() - start_time
            
            print(f"✅ 请求成功！耗时: {elapsed_time:.2f} 秒")
            print("\n🤖 AI 规划建议：")
            print(result) # 或者 print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"❌ 请求失败，状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
            
    except Exception as e:
        print(f"💥 发生异常: {e}")

if __name__ == "__main__":
    # 测试用例 1：综合性需求（触发天气、酒店、景点多重工具）
    case_1 = "我想去杭州玩，帮我看看下周天气，推荐一个西湖附近的酒店，并规划去灵隐寺的路线。"
    
    # 测试用例 2：简单需求
    case_2 = "北京明天的天气怎么样？"

    test_travel_planner(case_1)
    # time.sleep(2) # 稍作停顿
    # test_travel_planner(case_2)