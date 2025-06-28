# config.py

BASE_URL = "https://www.shanghairanking.cn/rankings/bcsr"
SUBJECT_LINK_SELECTOR = ".subject-item a"
CSS_SELECTOR = "[class^='rk-table-box']"
REQUIRED_KEYS = [
    "subject",
    "name",
    "layer",
]

# 🔥 测试模式配置 🔥
TEST_MODE = True  # 设为False可爬取所有
MAX_SUBJECTS = 93  # 最多爬取5个学科
MAX_PAGES_PER_SUBJECT = 1  # 每个学科最多2页

# 🔥 新增：多年份爬取配置 🔥
YEARS_TO_CRAWL = [2023]  # 要爬取的年份列表
# YEARS_TO_CRAWL = [2024]  # 只爬取单年份时使用这行