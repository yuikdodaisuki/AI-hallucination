"""修改main.py支持多年份爬取"""
# filepath: c:\Users\83789\PycharmProjects\scrapetest\src\scrapers\deepseek-ruanke-scraper\main.py

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

from config import BASE_URL, SUBJECT_LINK_SELECTOR, CSS_SELECTOR, REQUIRED_KEYS, YEARS_TO_CRAWL
from utils.data_utils import save_venues_to_csv
from utils.subject_crawler import crawl_all_subject_rankings
from utils.data_utils import save_venues_to_csv, save_venues_to_json, save_venues_to_both_formats

load_dotenv()


async def crawl_single_year(year: int, output_base_dir: Path) -> dict:
    """
    爬取单个年份的数据
    
    Args:
        year: 要爬取的年份
        output_base_dir: 输出基础目录
        
    Returns:
        dict: 包含爬取结果的字典
    """
    print(f"\n{'='*100}")
    print(f"🗓️  开始爬取 {year} 年数据")
    print(f"{'='*100}")
    
    # 🔥 构建该年份的完整URL 🔥
    year_url = f"{BASE_URL}/{year}"
    
    # 🔥 为该年份创建专门的输出目录 🔥
    year_output_dir = output_base_dir / str(year)
    year_output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📍 索引页面: {year_url}")
    print(f"📁 输出目录: {year_output_dir}")
    print(f"🔍 学科链接选择器: {SUBJECT_LINK_SELECTOR}")
    print(f"📊 排名表格选择器: {CSS_SELECTOR}")
    
    try:
        # 🔥 执行该年份的双层爬取 🔥
        all_data = await crawl_all_subject_rankings(
            index_url=year_url,
            subject_link_selector=SUBJECT_LINK_SELECTOR,
            ranking_css_selector=CSS_SELECTOR,
            required_keys=REQUIRED_KEYS
        )
        
        if all_data:
            # 🔥 为每条数据添加年份信息 🔥
            for item in all_data:
                item["year"] = year
            
            # 按学科分类统计
            subjects = {}
            for item in all_data:
                subject = item.get("subject", "unknown")
                if subject not in subjects:
                    subjects[subject] = []
                subjects[subject].append(item)
            
            # 🔥 保存该年份的总数据，文件名包含年份 🔥
            output_file_base = year_output_dir / f"all_subject_layers_{year}"
            save_venues_to_both_formats(all_data, str(output_file_base))
            output_file = output_file_base.with_suffix('.json')  # 更新返回的文件路径
            print(f"\n💾 保存 {year} 年数据: {len(all_data)} 条到 {output_file}")
            
            # 🔥 分学科保存（可选，包含年份） 🔥
            # print(f"\n📂 按学科分类保存 {year} 年数据:")
            # for subject_name, subject_data in subjects.items():
            #     safe_filename = subject_name.replace('/', '_').replace('\\', '_').replace(':', '_')
            #     filename = f"ranking_{safe_filename}_{year}.csv"
            #     subject_file = year_output_dir / filename
            #     save_venues_to_csv(subject_data, str(subject_file))
            #     print(f"   📄 {subject_name}: {len(subject_data)} 条 -> {filename}")
            
            # 统计信息
            print(f"\n🎉 {year} 年爬取完成!")
            print(f"📊 {year} 年总计: {len(all_data)} 条排名数据")
            print(f"🏫 {year} 年涵盖学科: {len(subjects)} 个")
            
            return {
                "year": year,
                "success": True,
                "data_count": len(all_data),
                "subjects_count": len(subjects),
                "output_file": str(output_file)
            }
            
        else:
            print(f"❌ {year} 年未获取到任何学科排名数据")
            return {
                "year": year,
                "success": False,
                "data_count": 0,
                "subjects_count": 0,
                "error": "无数据"
            }
            
    except Exception as e:
        print(f"❌ {year} 年爬取异常: {e}")
        return {
            "year": year,
            "success": False,
            "data_count": 0,
            "subjects_count": 0,
            "error": str(e)
        }


async def main():
    """
    主程序 - 多年份学科排名爬取
    """
    print("🎯 开始多年份学科排名爬取...")
    print(f"📍 基础URL: {BASE_URL}")
    print(f"🗓️  要爬取的年份: {', '.join(map(str, YEARS_TO_CRAWL))}")
    print("="*80)

    # 🔥 设置输出基础目录 🔥
    output_base_dir = Path(__file__).parent.parent.parent / "data" / "ruanke_subjects"
    output_base_dir.mkdir(parents=True, exist_ok=True)
    print(f"📁 输出基础目录: {output_base_dir}")
    
    # 🔥 存储所有年份的爬取结果 🔥
    all_years_results = []
    all_years_data = []  # 存储所有年份的数据，用于合并保存
    
    try:
        # 🔥 逐年爬取 🔥
        for index, year in enumerate(YEARS_TO_CRAWL):
            print(f"\n🔄 年份进度: {index + 1}/{len(YEARS_TO_CRAWL)}")
            
            # 爬取单个年份
            year_result = await crawl_single_year(year, output_base_dir)
            all_years_results.append(year_result)
            
            # 如果成功，读取数据用于合并（可选）
            if year_result["success"]:
                # 这里可以添加读取该年份数据的逻辑，用于后续合并
                pass
            
            # 🔥 年份间延迟，避免过于频繁的请求 🔥
            if index < len(YEARS_TO_CRAWL) - 1:  # 不是最后一个年份
                print(f"⏱️ 等待 30 秒后爬取下一年份...")
                await asyncio.sleep(30)
        
        # 🔥 生成总体统计报告 🔥
        print(f"\n{'='*100}")
        print(f"📊 多年份爬取完成统计")
        print(f"{'='*100}")
        
        successful_years = [r for r in all_years_results if r["success"]]
        failed_years = [r for r in all_years_results if not r["success"]]
        
        print(f"✅ 成功爬取年份: {len(successful_years)}/{len(YEARS_TO_CRAWL)}")
        for result in successful_years:
            print(f"   🗓️  {result['year']}: {result['data_count']} 条数据, {result['subjects_count']} 个学科")
        
        if failed_years:
            print(f"\n❌ 失败年份: {len(failed_years)}")
            for result in failed_years:
                print(f"   🗓️  {result['year']}: {result.get('error', '未知错误')}")
        
        print(f"\n📁 所有数据已保存到: {output_base_dir}")
        print(f"📂 目录结构:")
        for year in YEARS_TO_CRAWL:
            year_dir = output_base_dir / str(year)
            if year_dir.exists():
                print(f"   📁 {year}/")
                print(f"      📄 all_subject_layers_{year}.csv")
        
    except KeyboardInterrupt:
        print("\n👋 用户取消操作")
    except Exception as e:
        print(f"❌ 程序异常: {e}")


if __name__ == "__main__":
    asyncio.run(main())