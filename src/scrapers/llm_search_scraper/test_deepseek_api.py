"""
腾讯云 DeepSeek API 测试脚本（官方参数版）
使用官方推荐的 enable_search 参数
"""

import os
import json
from openai import OpenAI, APIConnectionError, APIError, RateLimitError

# 配置信息 - 替换为你的实际信息
CONFIG = {
    "api_key": "sk-24XB4aUrtxi5iGUIUwHDLsgkst4sy47hKHy4j9Mg97gLG1sC",      # 从腾讯云控制台获取
    "base_url": "https://api.lkeap.cloud.tencent.com/v1",  # 腾讯云专用端点
    "model": "deepseek-v3",           # 可选 deepseek-r1 或 deepseek-v3
    "knowledge_base_id": "kb-你的知识库ID"  # 可选，如果有私有知识库
}

def test_basic_chat(client):
    """测试基础对话功能"""
    try:
        response = client.chat.completions.create(
            model=CONFIG["model"],
            messages=[
                {"role": "system", "content": "你是一个专业的技术助手"},
                {"role": "user", "content": "请用Python写一个快速排序算法"}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        print("✅ 基础对话测试成功！")
        print("=" * 50)
        print("👤 用户提问：请用Python写一个快速排序算法")
        print("🤖 AI回复：")
        print(response.choices[0].message.content)
        print("=" * 50)
        print(f"消耗Token: 输入 {response.usage.prompt_tokens} | 输出 {response.usage.completion_tokens}")
        return True
    except Exception as e:
        print(f"❌ 基础对话测试失败: {str(e)}")
        return False

def test_online_search(client):
    """测试联网搜索功能 - 使用官方推荐的 enable_search 参数"""
    try:
        # 使用官方推荐的 enable_search 参数
        response = client.chat.completions.create(
            model=CONFIG["model"],
            messages=[
                {"role": "user", "content": "请搜索广州新华学院的esi前百分之一的学科"}
            ],
            max_tokens=400,
            extra_body={
                "enable_search": True  # 官方推荐的联网搜索参数
            }
        )
        
        print("✅ 联网搜索测试成功！")
        print("=" * 50)
        print("👤 用户提问：请搜索广州新华学院的esi前百分之一的学科")
        print("🤖 AI回复：")
        print(response.choices[0].message.content)
        print("=" * 50)
        
        
        return True
    except Exception as e:
        print(f"❌ 联网搜索测试失败: {str(e)}")
        return False



def main():
    # 初始化客户端 - 使用官方推荐格式
    client = OpenAI(
        api_key=CONFIG["api_key"],
        base_url=CONFIG["base_url"]
    )
    
    print(f"🚀 开始测试腾讯云 DeepSeek API (模型: {CONFIG['model']})")
    print("-" * 60)
    print("注意：使用官方推荐的 enable_search 参数")
    print("-" * 60)
    
    tests = [
        ("联网搜索", test_online_search),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n🔍 正在测试: {name}...")
        results.append(test_func(client))
    
    print("\n" + "=" * 60)
    print("📊 测试结果汇总:")
    for i, (name, _) in enumerate(tests):
        status = "✅ 成功" if results[i] else "❌ 失败"
        print(f"{name:15} {status}")
    
    success_rate = sum(results) / len(results) * 100
    print(f"\n测试完成! 成功率: {success_rate:.1f}%")

if __name__ == "__main__":
    # 检查API密钥是否已配置
    if CONFIG["api_key"].startswith("sk-你的") or "你的" in CONFIG["api_key"]:
        print("❌ 错误：请先在脚本中配置你的腾讯云API密钥")
        print("请将CONFIG字典中的api_key替换为你的实际密钥")
        print("获取API密钥：https://cloud.tencent.com/document/product/1772/115970")
    else:
        try:
            main()
        except APIConnectionError:
            print("❌ 网络连接失败，请检查网络设置")
        except RateLimitError:
            print("❌ 请求超限，请检查API配额或稍后重试")
        except APIError as e:
            print(f"❌ API错误: {e.message} (状态码: {e.status_code})")
        except Exception as e:
            print(f"❌ 未知错误: {str(e)}")