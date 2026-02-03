
"""Unsplash图片服务"""

import requests
import os
from typing import List, Optional
from fastmcp import FastMCP

mcp = FastMCP("VisualService")

# 从环境变量获取 Unsplash Access Key
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")

def _make_unsplash_request(url, params):
    """通用 Unsplash 请求处理"""
    if not UNSPLASH_ACCESS_KEY:
        return {"error": "未配置 UNSPLASH_ACCESS_KEY"}
    
    headers = {"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"}
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        return response.json()
    except Exception as e:
        return {"error": f"网络请求异常: {str(e)}"}

@mcp.tool()
def get_poi_photo(name: str) -> str:
    """
    根据地点名称搜索高清风景图。
    :param location_name: 地点或景点名称，如 'Forbidden City' 或 '故宫'
    :return: 图片的 URL 地址
    """
    url = "https://api.unsplash.com/search/photos"
    # 建议加上 'travel' 或 'scenery' 关键词以获得更相关的结果
    params = {
        "query": f"{name}",
        "per_page": 1,
        "orientation": "landscape"
    }
    
    data = _make_unsplash_request(url, params)
    
    if "results" in data and len(data["results"]) > 0:
        # 返回 raw 或 regular 尺寸的 URL
        return data["results"][0]["urls"]["regular"]
    
    # 如果没搜到具体景点，返回一张通用的旅行占位图
    return "https://images.unsplash.com/photo-1488646953014-85cb44e25828?q=80&w=1000"

if __name__ == "__main__":
    mcp.run(transport="stdio")