#=------------封装LLM调用函数------------=#
import os
import json
import logging
from openai import OpenAI
from dotenv import load_dotenv
#import traceback
load_dotenv()

#暴露参数包括messages、tools等
logger = logging.getLogger(__name__)

# 定义响应结构（模拟 OpenAI 的 message 对象）
class FunctionCall:
    def __init__(self, name: str, arguments: dict):
        self.name = name
        self.arguments = arguments  # 注意：是 dict，不是字符串

class ToolCall:
    def __init__(self, id: str, function: FunctionCall):
        self.id = id
        self.function = function

class LLMMessage:
    def __init__(self, content: str, tool_calls: list = None):
        self.content = content
        self.tool_calls = tool_calls or []


class HelloAgentLLM:
    def __init__(self,model:str=None,apiKey:str=None,baseUrl:str=None):
        self.model = model or os.getenv("LLM_MODEL_ID")
        apiKey = apiKey or os.getenv("LLM_API_KEY")
        baseUrl = baseUrl or os.getenv("LLM_BASE_URL")

        if not self.model or not apiKey or not baseUrl:
            logger.error("模型ID、API密钥和服务地址必须被提供或在.env文件中定义。")
            raise ValueError("模型ID、API密钥和服务地址必须被提供或在.env文件中定义。")

        self.client = OpenAI(api_key=apiKey,base_url=baseUrl)

    async def generate_response(self,
    messages:list[dict[str,str]], tools: list[dict] = None,max_tokens:int=4096,temperature:float=0.7):
        logger.debug(f"调用LLM模型: {self.model}, max_tokens={max_tokens}, temperature={temperature}")
        try:
            # 构建请求参数
            params = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                #"extra_body":{"enable_thinking": False}
            }

            # 如果提供了 tools，则加入请求，让llm知道有什么工具，以及其数据格式
            if tools:
                params["tools"] = tools
                params["tool_choice"] = "auto"  # 让模型自主决定是否调用工具

            response = self.client.chat.completions.create(**params)
            message = response.choices[0].message
            #print(f"LLM返回的原始内容:{message}\n")

            # 提取文本内容（可能为 None，比如纯工具调用时）,如何确保提取的内容是纯文本的？
            content = (message.content or "").strip()

            #解析LLM中工具调用，返回成agent接受的格式
            tool_calls=[]
            if hasattr(message,'tool_calls') and message.tool_calls:
                for tc in message.tool_calls:
                    func_name = tc.function.name
                    try:
                        # OpenAI 返回的是 JSON 字符串，需解析为 dict
                        func_args = json.loads(tc.function.arguments)
                    except(json.JSONDecodeError,TypeError):
                        logger.warning(f"工具参数解析失败: {tc.function.arguments}")
                        func_args={}
                    function_call=FunctionCall(name=func_name,arguments=func_args)
                    tool_call = ToolCall(id=tc.id,function=function_call)
                    tool_calls.append(tool_call)

            print("调用LLM模型成功")
            logger.info("LLM模型调用成功")
            return LLMMessage(content=content, tool_calls=tool_calls)  # 去除首尾空格
        except Exception as e:
            print(f"调用LLM模型失败: {e}")
            #traceback.print_exc()  # 打印完整错误堆栈，这能告诉我到底是什么问题
            logger.error(f"调用LLM模型失败: {e}", exc_info=True)
            # exc_info=True 会记录完整的异常堆栈信息
            return LLMMessage(content="抱歉，我遇到了错误。", tool_calls=[])

# #----测试----#
# if __name__ == "__main__":
#     llm = HelloAgentLLM() #实例化类
#     messages = [
#         {"role":"system","content":"你是一个助手，回答用户的问题。"},
#         {"role":"user","content":"你好，你是谁？"}
#     ]
#     response = llm.generate_response(messages)
#     print(response)
