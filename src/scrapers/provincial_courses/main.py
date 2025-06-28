"""省级一流课程爬虫主程序"""
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

from config import *
from models.course_data import ProvincialCourseData
from utils.data_utils import save_provincial_course_data, generate_statistics
from utils.scraper_utils import crawl_provincial_course_data

# 加载环境变量
load_dotenv()


async def main():
    """
    主程序：爬取省级一流课程数据
    """
    print("🎯 开始爬取省级一流课程数据...")
    print(f"📍 目标URL: {TARGET_URL}")
    print(f"🤖 使用模型: {LLM_MODEL}")
    print(f"🔥 使用技术: Crawl4ai自动分块 + LLM智能提取")
    
    # 设置输出目录
    output_dir = Path(__file__).parent.parent.parent / "data" / OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"📁 输出目录: {output_dir}")
    
    try:
        # 爬取数据
        print(f"\n{'='*80}")
        print("🚀 开始爬取...")
        print(f"{'='*80}")
        
        courses = await crawl_provincial_course_data(TARGET_URL)
        
        if courses:
            print(f"\n{'='*80}")
            print("📊 爬取成功，开始保存数据...")
            print(f"{'='*80}")
            
            # 保存主数据文件
            output_file = output_dir / OUTPUT_FILE
            save_provincial_course_data(courses, str(output_file), TARGET_URL)
            
            # 生成并保存统计信息
            stats = generate_statistics(courses)
            stats_file = output_dir / "statistics.json"
            
            with open(stats_file, 'w', encoding='utf-8') as f:
                import json
                json.dump(stats, f, ensure_ascii=False, indent=2)
            
            # 打印统计信息
            print(f"\n{'='*80}")
            print("📊 数据统计")
            print(f"{'='*80}")
            print(f"🏫 学校总数: {stats['overview']['total_schools']}")
            print(f"📚 第一批课程总数: {stats['overview']['total_first_batch']}")
            print(f"📚 第二批课程总数: {stats['overview']['total_second_batch']}")
            print(f"📚 第三批课程总数: {stats['overview']['total_third_batch']}")
            print(f"📚 课程总数: {stats['overview']['total_all_batches']}")
            print(f"📊 平均每校课程数: {stats['overview']['average_per_school']}")
            
            print(f"\n🏆 课程数量前10的学校:")
            for school in stats['top_10_schools'][:10]:
                print(f"  {school['rank']}. {school['school']}: {school['total']}门")
            
            print(f"\n📁 文件已保存:")
            print(f"  📄 {OUTPUT_FILE} - 完整数据 ({len(courses)} 所学校)")
            print(f"  📄 statistics.json - 统计信息")
            
        else:
            print("❌ 未获取到任何数据")
            print("\n💡 可能的解决方案:")
            print("   1. 检查网络连接")
            print("   2. 验证目标URL是否正确")
            print("   3. 检查LLM API配置")
            print("   4. 增加页面等待时间")
            
    except KeyboardInterrupt:
        print(f"\n👋 用户取消操作")
        
    except Exception as e:
        print(f"❌ 程序异常: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())