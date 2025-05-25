"""学科评估爬虫配置"""

# 目标网页URL
TARGET_URL = 'https://www.cdgdc.edu.cn/dslxkpgjggb/'

# 输出文件配置
OUTPUT_DIR = "../../data/subject_evaluation"
RAW_FILENAME = 'raw_subject_evaluation_data.json'
PROCESSED_FILENAME = 'subject_evaluation_data.json'

# 🔥 新增：输出控制配置 🔥
OUTPUT_OPTIONS = {
    'save_raw_data': False,        # 是否保存原始数据
    'save_processed_data': True,  # 是否保存转换后数据
    'output_format': 'processed',      # 'raw', 'processed', 'both'
    'auto_convert': True,         # 是否自动转换格式
}

# 浏览器配置
BROWSER_CONFIG = {
    'window_width_range': (1000, 1200),
    'window_height_range': (800, 1000),
    'wait_time_range': (1, 3),
    'page_load_wait': (5, 10),
    'click_wait': (1, 2),
    'iframe_wait': (3, 5)
}

# 选择器配置
SELECTORS = {
    'yxphb_div': '.yxphb',
    'iframe': 'iframe',
    'categories': '.Zmen, .Zmen2',
    'subjects': '#leftgundong a.hei12',
    'result_content': '#vsb_content'
}

# 评级筛选配置
TARGET_RATINGS = ["A+", "A", "A-"]

# 调试文件配置
DEBUG_FILES = {
    'iframe_content': 'iframe_content.html',
    'error_page': 'error_page.html'
}