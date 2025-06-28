import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 目标网站配置
TARGET_URL = "https://app.gaokaozhitongche.com/news/h/xO3Ev9r2"

# LLM配置 - 使用与智慧教育平台相同的配置
LLM_MODEL = "openai/deepseek-v3-0324"
LLM_BASE_URL = "https://api.lkeap.cloud.tencent.com/v1"  # 🔥 腾讯云DeepSeek API地址
API_KEY_ENV = "sk-24XB4aUrtxi5iGUIUwHDLsgkst4sy47hKHy4j9Mg97gLG1sC"




# 输出配置
OUTPUT_DIR = "teaching_achievements/provincial_courses"
OUTPUT_FILE = "provincial_courses_data.json"