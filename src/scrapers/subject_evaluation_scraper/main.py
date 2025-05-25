"""学科评估爬虫主入口"""
import os
import sys
from src.scrapers.subject_evaluation_scraper.scraper import start_scrape, scrape_raw_only, scrape_processed_only, scrape_both
from src.scrapers.subject_evaluation_scraper.config import OUTPUT_OPTIONS  # 🔥 导入配置

def ensure_data_directories():
    """确保数据目录存在"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dirs = [
        "../../data/subject_evaluation",
    ]
    
    for data_dir in data_dirs:
        full_path = os.path.join(current_dir, data_dir)
        os.makedirs(full_path, exist_ok=True)
        print(f"确保目录存在: {full_path}")


def run_subject_evaluation_scraper(output_format=None):
    """运行学科评估爬虫
    
    Args:
        output_format: 'raw', 'processed', 'both' None时使用配置文件
    """
    # 确保目录结构
    ensure_data_directories()

    final_format = output_format or OUTPUT_OPTIONS['output_format']
    
    print(f"🎯 输出格式: {final_format} (来源: {'参数' if output_format else '配置文件'})")
    
    # 开始爬取
    success = start_scrape(final_format)
    
    if success:
        print("🎉 学科评估数据爬取完成!")
    else:
        print("💥 学科评估数据爬取失败!")
    
    return success

def print_usage():
    """打印使用说明"""
    print("🔧 学科评估爬虫使用说明:")
    print("   python main.py              # 使用配置文件设置")
    print("   python main.py raw          # 只输出原始数据")
    print("   python main.py processed    # 只输出转换后数据")
    print("   python main.py both         # 输出两种格式")
    print(f"   当前配置文件默认格式: {OUTPUT_OPTIONS['output_format']}")

if __name__ == '__main__':
    # 🔥 改进的命令行处理
    if len(sys.argv) > 1:
        format_arg = sys.argv[1].lower()
        if format_arg in ['raw', 'processed', 'both']:
            print(f"📝 使用命令行参数: {format_arg}")
            run_subject_evaluation_scraper(format_arg)  # 传入命令行参数
        elif format_arg in ['help', '-h', '--help']:
            print_usage()
        else:
            print("❌ 无效的输出格式。请使用: raw, processed, both")
            print_usage()
    else:
        # 🔥 没有命令行参数时，使用配置文件设置
        print(f"📝 使用配置文件设置: {OUTPUT_OPTIONS['output_format']}")
        run_subject_evaluation_scraper()  # 不传参数，使用配置文件