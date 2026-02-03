import asyncio
from mcp import ClientSession
from typing import List

class AmapMCPTool:
    """单个工具的执行实体"""
    def __init__(self, mcp_client_session, mcp_tool_info):
        self.session = mcp_client_session
        self.name = mcp_tool_info.name
        self.description = mcp_tool_info.description
        self.input_schema = mcp_tool_info.inputSchema #初始化时自动读取MCP服务端定义的inputSchema

    def to_dict(self):
        """转换为你的 llm_client 需要的 OpenAI 工具格式"""
        """OpenAI 期望的 JSON Schema 格式"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.input_schema
            }
        }

    async def run(self, **kwargs):
        """直接使用异步调用 MCP 工具"""
        # 确保 session.call_tool 是异步调用的
        result = await self.session.call_tool(self.name, arguments=kwargs)
        # MCP 返回通常是 content 列表，提取文本内容
        return result.content[0].text if result.content else ""

class AmapMCPBatch:
    """MCP 工具包：负责发现并展开所有工具"""
    def __init__(self, mcp_client_session: ClientSession,include_keywords:list = None):
        self.session = mcp_client_session
        self.auto_expand = True  # 标记为可自动展开
        self.include_keywords = include_keywords

    async def get_expanded_tools(self) -> List[AmapMCPTool]:
        """从 MCP 会话中拉取所有可用工具并封装"""
        """每个工具只做一次，避免多个agent重复封装"""
        # 调用 MCP 协议获取工具列表
        mcp_tools_resp = await self.session.list_tools()
        expanded = []
        for t in mcp_tools_resp.tools:
            # 逻辑：如果没有指定关键字，则加载全部；如果指定了，则匹配名称
            should_include = True
            if self.include_keywords:
                should_include = any(kw in t.name for kw in self.include_keywords)
            
            if should_include:
                expanded.append(AmapMCPTool(self.session, t))

        return expanded
        #返回mcptool工具实例列表