import os
import sys
# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, '../../..')  # 回到scrapetest目录
sys.path.insert(0, os.path.abspath(project_root))

from src.scrapers.moe_scraper.moeScrape import startScrape


def ensure_data_directories():
    """确保数据目录存在"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dirs = [
        "../../data/moepolicies",
        "../../data/consolidated",
        "../../data/subject_evaluation"
    ]
    
    for data_dir in data_dirs:
        full_path = os.path.join(current_dir, data_dir)
        os.makedirs(full_path, exist_ok=True)
        print(f"确保目录存在: {full_path}")


def run_all_task():
    # 首先确保目录结构
    ensure_data_directories()
    # 然后开始爬取
    startScrape()


if __name__ == '__main__':
    run_all_task()
