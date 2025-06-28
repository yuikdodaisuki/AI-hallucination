import os
from config import *

def check_api_configuration():
    """检查API配置"""
    print("🔍 检查API配置...")
    print(f"📋 LLM模型: {LLM_MODEL}")
    print(f"🌐 API Base URL: {LLM_BASE_URL}")
    print(f"🔑 API Key环境变量: {API_KEY_ENV}")
    
    # 检查环境变量
    api_key = os.getenv(API_KEY_ENV)
    if api_key:
        print(f"✅ 找到API Key: {api_key[:10]}...{api_key[-4:] if len(api_key) > 14 else '***'}")
    else:
        print(f"❌ 未找到环境变量 {API_KEY_ENV}")
        
        # 检查其他可能的环境变量
        alternative_keys = ["DEEPSEEK_API_KEY", "OPENAI_API_KEY", "API_KEY"]
        for alt_key in alternative_keys:
            alt_value = os.getenv(alt_key)
            if alt_value:
                print(f"🔍 找到替代Key {alt_key}: {alt_value[:10]}...{alt_value[-4:] if len(alt_value) > 14 else '***'}")
    
    return api_key

if __name__ == "__main__":
    check_api_configuration()