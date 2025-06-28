"""智慧教育平台课程爬虫主程序"""
import asyncio
import os
import json
from pathlib import Path
from dotenv import load_dotenv

from crawl4ai import AsyncWebCrawler

from config import *
from models.course import Course, SchoolCourseSummary
from utils.data_utils import (
    read_school_list_from_csv,
    save_courses_to_json,
    save_school_summary_to_json,
    generate_statistics
)
from utils.scraper_utils import get_browser_config, crawl_school_courses

# 加载环境变量
load_dotenv()


async def main():
    """
    主程序：爬取国家高等教育智慧教育平台课程数据 - 使用自动分块
    """
    print("🎯 开始爬取国家高等教育智慧教育平台课程数据...")
    print(f"📍 基础URL: {BASE_URL}")
    print(f"🧪 测试模式: {'开启' if TEST_MODE else '关闭'}")
    print(f"🤖 使用模型: {LLM_MODEL}")
    print(f"📦 批处理大小: {LLM_BATCH_SIZE}")
    print(f"🔥 新特性: 使用Crawl4ai自动分块技术")
    
    # 设置输出目录
    output_dir = Path(__file__).parent.parent.parent / "data" / OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"📁 输出目录: {output_dir}")
    
    # 读取学校列表
    school_list_file = Path(__file__).parent.parent.parent.parent / SCHOOL_LIST_FILE
    if not school_list_file.exists():
        print(f"❌ 学校列表文件不存在: {school_list_file}")
        return
    
    schools = read_school_list_from_csv(str(school_list_file))
    if not schools:
        print("❌ 未读取到学校数据")
        return
    
    # 测试模式限制学校数量
    if TEST_MODE and len(schools) > MAX_SCHOOLS:
        schools = schools[:MAX_SCHOOLS]
        print(f"🧪 测试模式：只爬取前 {MAX_SCHOOLS} 所学校")
    
    print(f"📋 共需爬取 {len(schools)} 所学校")
    
    # 🔥 使用自动分块爬取策略
    print(f"🤖 使用策略: Crawl4ai自动分块 + LLM智能提取")
    print(f"📦 分块大小: 6000 tokens")
    print(f"🔄 重叠率: 15%")
    
    # 初始化浏览器配置
    browser_config = get_browser_config()
    session_id = "smartedu_auto_chunking_crawl"
    
    # 存储所有数据
    all_courses = []
    school_summaries = []
    successful_schools = 0
    failed_schools = []
    
    try:
        # 🔥 不再创建单独的crawler，直接调用crawl_school_courses
        # 因为新的函数内部已经管理了crawler的生命周期
        
        for index, school_name in enumerate(schools):
            print(f"\n🔄 进度: {index + 1}/{len(schools)} - {school_name}")
            
            try:
                # 🔥 使用新的自动分块爬取函数
                # 每个学校使用独立的session
                school_session_id = f"{session_id}_{index}_{school_name.replace(' ', '_')}"
                
                school_courses = await crawl_school_courses(
                    school_name, school_session_id
                )
                
                if school_courses:
                    # 添加到总课程列表
                    all_courses.extend(school_courses)
                    
                    # 创建学校汇总
                    school_summary = SchoolCourseSummary(
                        school=school_name,
                        total_courses=len(school_courses),
                        courses=school_courses
                    )
                    school_summaries.append(school_summary)
                    
                    successful_schools += 1
                    print(f"✅ {school_name}: {len(school_courses)} 门课程")
                    
                    # 显示课程样例
                    if len(school_courses) > 0:
                        print(f"   📚 样例课程:")
                        for i, course in enumerate(school_courses[:3], 1):  # 显示前3个
                            print(f"     {i}. {course.course_name} - {course.teacher}")
                        if len(school_courses) > 3:
                            print(f"     ... 还有 {len(school_courses) - 3} 门课程")
                else:
                    failed_schools.append(school_name)
                    print(f"❌ {school_name}: 未获取到课程数据")
                
                # 🔥 自动分块策略下的请求间隔
                # 由于自动分块可能会增加处理时间，适当调整间隔
                if index < len(schools) - 1:
                    interval = max(REQUEST_DELAY, 5)  # 最少5秒间隔
                    print(f"⏱️ 等待 {interval} 秒...")
                    await asyncio.sleep(interval)
                    
            except Exception as e:
                failed_schools.append(school_name)
                print(f"❌ 爬取 {school_name} 异常: {e}")
                # 🔥 异常时也要等待，避免频繁重试
                if index < len(schools) - 1:
                    await asyncio.sleep(3)
                continue
        
        # 保存数据
        if all_courses:
            print(f"\n{'='*100}")
            print(f"📊 开始保存数据...")
            print(f"{'='*100}")
            
            # 保存所有课程数据
            all_courses_file = output_dir / OUTPUT_FILES["all_courses"]
            save_courses_to_json(all_courses, str(all_courses_file))
            
            # 保存学校汇总数据
            school_summary_file = output_dir / OUTPUT_FILES["school_summary"]
            save_school_summary_to_json(school_summaries, str(school_summary_file))
            
            # 生成并保存统计信息
            stats = generate_statistics(school_summaries)
            stats_file = output_dir / OUTPUT_FILES["statistics"]
            
            # 🔥 增加自动分块相关的统计信息
            enhanced_stats = {
                **stats,
                "extraction_method": "Crawl4ai自动分块 + LLM智能提取",
                "chunk_size": "6000 tokens",
                "overlap_rate": "15%",
                "total_extraction_time": "实际运行时间",
                "failed_schools_list": failed_schools,
                "success_rate": f"{successful_schools}/{len(schools)} ({successful_schools/len(schools)*100:.1f}%)"
            }
            
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(enhanced_stats, f, ensure_ascii=False, indent=2)
            
            # 打印统计信息
            print(f"\n{'='*100}")
            print(f"📊 爬取完成统计 - 自动分块版本")
            print(f"{'='*100}")
            print(f"🎯 爬取策略: Crawl4ai自动分块 + LLM智能提取")
            print(f"✅ 成功爬取学校: {successful_schools}/{len(schools)} ({successful_schools/len(schools)*100:.1f}%)")
            print(f"📚 总课程数量: {len(all_courses)}")
            print(f"📊 平均每校课程数: {enhanced_stats.get('average_courses_per_school', 0)}")
            
            # 🔥 数据质量分析
            if len(all_courses) > 0:
                # 分析教师名称长度分布
                teacher_lengths = [len(course.teacher) for course in all_courses]
                avg_teacher_length = sum(teacher_lengths) / len(teacher_lengths)
                
                # 分析课程名称长度分布
                course_lengths = [len(course.course_name) for course in all_courses]
                avg_course_length = sum(course_lengths) / len(course_lengths)
                
                print(f"\n🔍 数据质量分析:")
                print(f"   教师名称平均长度: {avg_teacher_length:.1f} 字符")
                print(f"   课程名称平均长度: {avg_course_length:.1f} 字符")
                
                # 检查可能的数据质量问题
                short_teachers = [c for c in all_courses if len(c.teacher) < 2]
                long_teachers = [c for c in all_courses if len(c.teacher) > 10]
                
                if short_teachers:
                    print(f"   ⚠️ 疑似无效教师名称: {len(short_teachers)} 个")
                if long_teachers:
                    print(f"   ⚠️ 疑似过长教师名称: {len(long_teachers)} 个")
                
                print(f"   ✅ 数据质量: {(len(all_courses)-len(short_teachers)-len(long_teachers))/len(all_courses)*100:.1f}%")
            
            if enhanced_stats.get('top_5_schools'):
                print(f"\n🏆 课程数量前5名学校:")
                for i, school_info in enumerate(enhanced_stats['top_5_schools'], 1):
                    print(f"   {i}. {school_info['name']}: {school_info['course_count']} 门")
            
            if failed_schools:
                print(f"\n❌ 失败学校 ({len(failed_schools)}):")
                for i, school in enumerate(failed_schools, 1):
                    print(f"   {i}. {school}")
                
                # 🔥 失败原因分析提示
                print(f"\n💡 失败可能原因:")
                print(f"   1. 学校名称在网站中不存在")
                print(f"   2. 网络连接问题或页面加载超时")
                print(f"   3. 网站结构发生变化")
                print(f"   4. LLM提取过程中出现错误")
                print(f"   5. 自动分块配置需要调整")
            
            print(f"\n📁 数据已保存到: {output_dir}")
            print(f"   📄 {OUTPUT_FILES['all_courses']} - 所有课程详细数据 ({len(all_courses)} 条)")
            print(f"   📄 {OUTPUT_FILES['school_summary']} - 学校课程汇总 ({len(school_summaries)} 所)")
            print(f"   📄 {OUTPUT_FILES['statistics']} - 统计信息 (含自动分块数据)")
            
            # 🔥 保存成功学校列表（用于后续分析）
            if successful_schools > 0:
                successful_schools_list = [summary.school for summary in school_summaries]
                success_file = output_dir / "successful_schools.json"
                with open(success_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        "successful_schools": successful_schools_list,
                        "total_count": len(successful_schools_list),
                        "extraction_method": "Crawl4ai自动分块"
                    }, f, ensure_ascii=False, indent=2)
                print(f"   📄 successful_schools.json - 成功学校列表 ({len(successful_schools_list)} 所)")
            
        else:
            print("❌ 未获取到任何课程数据")
            print("\n💡 可能的解决方案:")
            print("   1. 检查网络连接")
            print("   2. 验证学校列表文件中的学校名称")
            print("   3. 调整LLM配置参数")
            print("   4. 增加页面加载等待时间")
            print("   5. 检查自动分块配置是否合适")
            
    except KeyboardInterrupt:
        print(f"\n👋 用户取消操作")
        print(f"📊 已处理: {len(school_summaries)} 所学校")
        if all_courses:
            print(f"📚 已获取: {len(all_courses)} 门课程")
            # 即使被中断，也保存已获取的数据
            emergency_file = output_dir / f"emergency_save_{len(all_courses)}_courses.json"
            save_courses_to_json(all_courses, str(emergency_file))
            print(f"💾 应急保存: {emergency_file}")
            
    except Exception as e:
        print(f"❌ 程序异常: {e}")
        print(f"📊 已处理: {len(school_summaries)} 所学校")
        if all_courses:
            print(f"📚 已获取: {len(all_courses)} 门课程")
            # 异常时也保存已获取的数据
            emergency_file = output_dir / f"error_save_{len(all_courses)}_courses.json"
            save_courses_to_json(all_courses, str(emergency_file))
            print(f"💾 异常保存: {emergency_file}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())