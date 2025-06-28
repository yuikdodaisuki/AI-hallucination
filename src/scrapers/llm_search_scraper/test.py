from typing import *
import os
import json
from openai import OpenAI
from openai.types.chat.chat_completion import Choice

client = OpenAI(
    base_url="https://api.moonshot.cn/v1",
    api_key="sk-GvZqsEKUs6OIFg346ofcaHMCZRNFFlDl29xVKb8bqXujDg5r"  # 替换为你的 API 密钥
)

def search_impl(arguments: Dict[str, Any]) -> Any:
    # 直接返回参数即可，Kimi 会处理搜索逻辑
    return arguments

def chat(messages) -> Choice:
    completion = client.chat.completions.create(
        model="moonshot-v1-128k",
        messages=messages,
        temperature=0.3,
        tools=[
            {
                "type": "builtin_function",
                "function": {
                    "name": "$web_search",
                },
            }
        ]
    )
    return completion.choices[0]

def main():
    messages = [
        {"role": "system", "content": "你是 Kimi。"},
        {"role": "user", "content": "请搜索广州新华学院（中大新华）截止2024年的esi前百分之一的学科，并输出数据来源"}
    ]
    finish_reason = None
    while finish_reason is None or finish_reason == "tool_calls":
        choice = chat(messages)
        finish_reason = choice.finish_reason
        if finish_reason == "tool_calls":
            messages.append(choice.message)
            for tool_call in choice.message.tool_calls:
                tool_call_name = tool_call.function.name
                tool_call_arguments = json.loads(tool_call.function.arguments)
                if tool_call_name == "$web_search":
                    tool_result = search_impl(tool_call_arguments)
                else:
                    tool_result = f"Error: unable to find tool by name '{tool_call_name}'"
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_call_name,
                    "content": json.dumps(tool_result),
                })
    print(choice.message.content)  # 输出最终回复

if __name__ == "__main__":
    main()