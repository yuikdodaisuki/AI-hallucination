import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from utils.scraper_utils import crawl_multiple_school_intros
from utils.data_utils import print_school_statistics, save_school_intro_data
from config import *

# 加载环境变量
load_dotenv()


async def main():
    """学校简介信息爬取主程序"""
    print("🚀 启动学校简介信息爬取程序")
    print(f"📋 配置的学校数量: {len(SCHOOL_WEBSITES)}")

    # 设置输出目录
    output_dir = Path(__file__).parent.parent.parent / "data" / OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"📁 输出目录: {output_dir}")
    
    try:
        # 爬取学校简介数据
        print("\n🔄 开始爬取学校简介数据...")
        crawl_results = await crawl_multiple_school_intros(SCHOOL_WEBSITES)
        
        # 提取成功的数据
        successful_data = [result.data for result in crawl_results if result.success and result.data]
        
        if successful_data:
            print(f"\n✅ 成功提取 {len(successful_data)} 所学校的数据")
            
            # 数据分析（控制台输出）
            print_school_statistics(successful_data)
            
            # 显示详细数据
            print(f"\n📋 详细学校信息:")
            print(f"{'='*80}")
            for i, school in enumerate(successful_data, 1):
                print(f"\n{i}. {school}")
            
            # 导出数据为JSON
            print(f"\n💾 开始导出数据...")
            output_file = save_school_intro_data(successful_data)
            
            print(f"\n🎉 学校简介数据爬取和导出完成!")
            print(f"📁 数据文件: {output_file}")
        else:
            print("❌ 未获取到任何学校简介数据")
            
            # 显示失败原因
            failed_results = [result for result in crawl_results if not result.success]
            if failed_results:
                print(f"\n❌ 失败详情:")
                for result in failed_results:
                    print(f"  🏫 {result.school_name}: {result.error_message}")
            
    except KeyboardInterrupt:
        print("\n⏹️ 用户中断程序")
    except Exception as e:
        print(f"❌ 程序执行异常: {e}")
        import traceback
        traceback.print_exc()


def show_help():
    """显示帮助信息"""
    print("🏫 学校简介信息爬取程序")
    print("=" * 50)
    print("📖 使用说明:")
    print("  python main.py          - 开始爬取所有配置的学校")
    print("  python main.py --help   - 显示此帮助信息")
    print()
    print("📝 配置说明:")
    print("  在 config.py 中的 SCHOOL_WEBSITES 字典中配置要爬取的学校和网址")
    print()
    print("📊 输出说明:")
    print("  程序会自动生成JSON、CSV、Excel格式的数据文件")
    print("  文件保存在 output/ 目录下")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h']:
        show_help()
    else:
        # 运行学校简介爬取程序
        asyncio.run(main())