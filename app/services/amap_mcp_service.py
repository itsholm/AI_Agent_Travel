import os
import requests
from fastmcp import FastMCP

# 初始化 MCP 服务端
mcp = FastMCP("AmapMapService")

# 从环境变量获取高德 API KEY
AMAP_API_KEY = os.getenv("AMAP_API_KEY")

def _make_request(url, params):
    """通用请求处理函数"""
    if not AMAP_API_KEY:
        return "错误：未配置 AMAP_API_KEY 环境变量。"
    
    params["key"] = AMAP_API_KEY
    params["output"] = "json"
    
    try:
        response = requests.get(url, params=params, timeout=10)
        return response.json()
    except Exception as e:
        return {"status": "0", "info": f"网络请求异常: {str(e)}"}


@mcp.tool()
def amap_maps_text_search(keywords: str, city: str = None) -> str:
    """
    搜索高德地图上的地点、景点、酒店或餐厅信息。
    :param keywords: 搜索关键词，如 '故宫'、'五星级酒店'
    :param city: 城市名称或城市编码，如 '北京'
    """
    if not AMAP_API_KEY:
        return "错误：未配置 AMAP_API_KEY 环境变量。"

    url = "https://restapi.amap.com/v3/place/text"
    params = {"keywords": keywords, "city": city, "offset": 3, "page": 1}
    data = _make_request(url,params)

    if data.get("status") == "1":
        pois = data.get("pois", [])
        if not pois: return "未找到相关地点。"
        return "\n".join([f"名称: {p['name']}, 地址: {p['address']}, ID: {p['id']}, 坐标: {p['location']}" for p in pois])
    return f"搜索失败: {data.get('info')}"

    # try:
    #     response = requests.get(url, params=params, timeout=10)
    #     data = response.json()
        
    #     if data.get("status") == "1":
    #         pois = data.get("pois", [])
    #         if not pois:
    #             return "未找到相关地点。"
            
    #         result_lines = []
    #         for p in pois[:3]: # 限制返回 3 个最相关的，节省上下文
    #             info = f"名称: {p['name']}, 地址: {p['address']}, 类型: {p['type']}, 坐标: {p['location']}"
    #             result_lines.append(info)
    #         return "\n".join(result_lines)
    #     return f"查询失败：{data.get('info')}"
    # except Exception as e:
    #     return f"接口调用异常: {str(e)}"

@mcp.tool()
def amap_maps_weather(city: str) -> str:
    """
    查询指定城市的天气信息。
    :param city: 城市名称或城市编码，如 '杭州' 或 '330100'
    """
    if not AMAP_API_KEY:
        return "错误：未配置 AMAP_API_KEY 环境变量。"

    url = "https://restapi.amap.com/v3/weather/weatherInfo"
    params = {"city": city, "extensions": "base"}

    data = _make_request(url, params)

    if data.get("status") == "1":
            lives = data.get("lives", [])
            if not lives:
                return "未查询到该城市的天气信息。"
            w = lives[0]
            return f"城市: {w['city']}, 天气: {w['weather']}, 温度: {w['temperature']}°C, 风向: {w['winddirection']}, 湿度: {w['humidity']}%"
    return f"查询失败：{data.get('info')}"

#FastMCP的@tool装饰器通常期望同步函数，异步声明可能导致协议层异常
@mcp.tool()
def amap_hotel_search(city: str, keywords: str = "酒店", radius: int = 3000) -> str:
    """
    搜索指定城市内的酒店信息。
    :param city: 城市名称或城市编码，如 '杭州'
    :param keywords: 搜索关键词，默认为 '酒店'
    :param radius: 搜索半径（米），默认为 3000
    """
    # 使用高德地点搜索 API (周边搜索或关键字搜索)
    # 这里采用 text 接口，并限定 POI 类型为酒店住宿 (100000)
    url = "https://restapi.amap.com/v3/place/text"
    params = {
        "keywords": keywords,
        "city": city,
        "types": "100000",  # 酒店住宿类代码，确保结果偏向酒店 
        "offset": 5,        # 返回前5条结果
        "page": 1,
        "extensions": "all" # 获取深度信息（如评分、价格） 
    }

    # 调用通用的请求处理函数
    data = _make_request(url, params)

    # 逻辑处理：如果是字符串，说明 _make_request 报错（如 KEY 缺失）
    if isinstance(data, str):
        return data

    if data.get("status") == "1":
        pois = data.get("pois", [])
        if not pois:
            return f"在 {city} 未找到相关的酒店信息。"
        
        results = [f"已为您在 {city} 找到以下酒店："]
        for i, p in enumerate(pois[:3], 1):  # 取前3个最相关的
            biz_ext = p.get("biz_ext", {})
            rating = biz_ext.get("rating", "暂无评分")
            cost = biz_ext.get("cost", "暂无价格")
            info = (f"{i}. {p['name']} - 评分: {rating}, "
                    f"均价: {cost}元, 地址: {p['address']}")
            results.append(info)
            
        return "\n".join(results)
    
    return f"酒店查询失败：{data.get('info', '未知错误')}"


# amap_mcp_service.py 补充部分

@mcp.tool()
def amap_maps_direction(origin: str, destination: str, mode: str = "driving") -> str:
    """
    路径规划：获取起点到终点的路线、距离和耗时。
    :param origin: 起点经纬度 (如 '116.481,39.990')
    :param destination: 终点经纬度 (如 '116.434,39.908')
    :param mode: 出行方式: driving(驾车), walking(步行), bicycling(骑行)
    """
    # 映射高德不同的接口 URL
    mode_map = {
        "driving": "https://restapi.amap.com/v3/direction/driving",
        "walking": "https://restapi.amap.com/v3/direction/walking",
        "bicycling": "https://restapi.amap.com/v4/direction/bicycling"
    }
    url = mode_map.get(mode, mode_map["driving"])
    params = {"origin": origin, "destination": destination}
    
    data = _make_request(url, params)
    
    # 驾车/步行在 v3，骑行在 v4，结构略有不同
    try:
        if data.get("status") == "1" or data.get("errcode") == 0:
            route = data.get("route", {}) if "route" in data else data.get("data", {}).get("paths", [{}])[0]
            path = route.get("paths", [{}])[0] if "paths" in route else route
            distance = int(path.get("distance", 0)) / 1000
            duration = int(path.get("duration", 0)) // 60
            return f"路线规划成功：全长约 {distance:.2f}km，预计耗时 {duration} 分钟。"
        return f"路径规划失败: {data.get('info') or data.get('errmsg')}"
    except:
        return "解析路径数据失败。"

@mcp.tool()
def amap_maps_poi_detail(poi_id: str) -> str:
    """
    获取 POI 的详细信息（如电话、评分、深度详情等）。
    :param poi_id: 地点的 ID
    """
    url = "https://restapi.amap.com/v3/place/detail"
    params = {"id": poi_id}
    data = _make_request(url, params)
    
    if data.get("status") == "1":
        pois = data.get("pois", [])
        if not pois: return "未找到该地点的详细信息。"
        p = pois[0]
        biz_info = p.get("biz_ext", {})
        rating = biz_info.get("rating", "暂无评分")
        cost = biz_info.get("cost", "暂无")
        return f"【{p['name']}】 评分: {rating}, 人均消费: {cost}, 地址: {p['address']}, 电话: {p.get('tel', '无')}"
    return f"详情查询失败: {data.get('info')}"


@mcp.tool()
def search_nearby(location: str, keyword: str, radius: int = 3000) -> str:
    """
    在指定坐标周边搜索特定类型的场所。
    :param location: 中心点经纬度，格式 "经度,纬度"
    :param keyword: 搜索关键词，如 "酒店" 或 "餐厅"
    :param radius: 搜索半径，单位米，默认3000米
    """
    url = "https://restapi.amap.com/v3/place/around"
    params = {
        "key": AMAP_API_KEY,
        "location": location,
        "keywords": keyword,
        "radius": radius,
        "offset": 5, # 仅返回前5个最相关的
        "page": 1,
        "extensions": "all"
    }
    
    # 💡 关键部分：使用 location 参数进行精确的“周边”过滤
    response = requests.get(url, params=params)
    data = response.json()
    
    if data.get("status") == "1" and data.get("pois"):
        results = []
        for poi in data["pois"]:
            results.append(f"{poi['name']} (距离中心: {poi['distance']}米, 地址: {poi['address']})")
        return "\n".join(results)
    return f"在坐标 {location} 周边 {radius}米内未找到相关{keyword}"

if __name__ == "__main__":
    # 启动 MCP 服务器，默认使用标准输入输出 (stdio) 通信
    # 重点：设置 dev_mode=False 并且关闭内置的日志装饰
    # 确保没有 print() 语句在代码的其他地方执行
    mcp.run(transport="stdio")