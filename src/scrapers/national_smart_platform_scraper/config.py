"""智慧教育平台爬虫配置文件"""

# 项目基本信息
PROJECT_NAME = "National Smart Education Platform Scraper"
VERSION = "1.0.0"

# 网站基础配置
BASE_URL = "https://higher.smartedu.cn"
SCHOOL_INDEX_URL = "https://higher.smartedu.cn/school"
SEARCH_URL_TEMPLATE = "https://higher.smartedu.cn/search?school={school_name}"

# CSS选择器配置
LOAD_MORE_BUTTON_SELECTOR = "button.text-white.bg-blue-600"
COURSE_CONTAINER_SELECTOR = "border-b border-gray-300"

# 爬取行为配置
MAX_SCROLL_ATTEMPTS = 30  # 最大滚动尝试次数
SCROLL_DELAY = 3  # 滚动间隔时间(秒)
LOAD_MORE_DELAY = 5  # 点击加载更多后等待时间(秒)
REQUEST_DELAY = 5  # 请求间隔时间(秒)
PAGE_LOAD_TIMEOUT = 20  # 页面加载超时时间(秒)

# 测试模式配置
TEST_MODE = False  # 设为False可爬取所有学校
MAX_SCHOOLS = 2  # 测试模式下最多爬取学校数量

# 🔥 DeepSeek LLM配置
LLM_BATCH_SIZE = 5  # 每批处理的课程数量
MAX_INPUT_TOKENS = 8000  # DeepSeek支持更大的输入
MAX_OUTPUT_TOKENS = 2000  # DeepSeek支持更大的输出
LLM_MODEL = "openai/deepseek-v3-0324"  # 🔥 更改为DeepSeek模型
LLM_BASE_URL = "https://api.lkeap.cloud.tencent.com/v1"  # 🔥 腾讯云DeepSeek API地址

# 🔥 API密钥配置
API_KEY_ENV = "DEEPSEEK_API_KEY"  # DeepSeek API密钥环境变量名

# 请求控制（DeepSeek限制较宽松）
REQUEST_DELAY = 10        # 减少请求间隔
SCROLL_DELAY = 3          # 滚动延迟
LOAD_MORE_DELAY = 5       # 加载更多延迟
MAX_SCROLL_ATTEMPTS = 10  # 增加滚动尝试次数

# DeepSeek速率限制（相对宽松）
RATE_LIMIT_RETRY_ATTEMPTS = 3    # 重试次数
RATE_LIMIT_BASE_DELAY = 30       # 基础延迟30秒
RATE_LIMIT_BACKOFF_MULTIPLIER = 2

# DeepSeek Token限制（更宽松）
TOKENS_PER_MINUTE = 20000        # DeepSeek支持更高的TPM
MIN_REQUEST_INTERVAL = 3         # 最小请求间隔减少到3秒

# 数据文件路径配置
SCHOOL_LIST_FILE = "ai_evaluation_dataset_long.csv"  # 学校指标列表文件
OUTPUT_DIR = "smartedu_courses"  # 输出目录名
OUTPUT_FILES = {
    "all_courses": "all_courses.json",
    "school_summary": "school_course_summary.json", 
    "statistics": "statistics.json"
}

# 重试配置
MAX_RETRIES = 3  # 最大重试次数
RETRY_DELAY = 5  # 重试间隔时间(秒)