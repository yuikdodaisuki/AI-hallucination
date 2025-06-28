import json
import os
from datetime import datetime
from typing import List

from models.school_intro_data import SchoolIntroData, CrawlResult
from config import OUTPUT_DIR


def save_school_intro_data(
    schools: List[SchoolIntroData], 
    output_file: str = None,
    source_info: str = "学校简介数据爬取"
) -> str:
    """
    保存学校简介数据到JSON文件
    """
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(OUTPUT_DIR, f"school_intro_data_{timestamp}.json")
    
    print(f"💾 保存数据到: {output_file}")
    
    # 准备保存的数据
    save_data = {
        "extraction_info": {
            "timestamp": datetime.now().isoformat(),
            "source_info": source_info,
            "total_schools": len(schools),
            "total_undergraduate_majors": sum(school.undergraduate_majors for school in schools),
            "total_national_first_class_majors": sum(school.national_first_class_majors for school in schools),
            "total_provincial_first_class_majors": sum(school.provincial_first_class_majors for school in schools),
        },
        "schools": [school.to_dict() for school in schools]
    }
    
    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # 保存到JSON文件
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(save_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 数据保存成功!")
    print(f"  🏫 学校总数: {len(schools)}")
    print(f"  📚 本科专业总数: {sum(school.undergraduate_majors for school in schools)}")
    print(f"  🥇 国家级一流专业总数: {sum(school.national_first_class_majors for school in schools)}")
    print(f"  🥈 省级一流专业总数: {sum(school.provincial_first_class_majors for school in schools)}")
    print(f"  📁 文件路径: {output_file}")
    
    return output_file


def generate_school_statistics(schools: List[SchoolIntroData]) -> dict:
    """
    生成学校简介统计信息
    """
    if not schools:
        return {"error": "没有数据可统计"}
    
    # 计算各项总数
    total_undergraduate = sum(school.undergraduate_majors for school in schools)
    total_national_majors = sum(school.national_first_class_majors for school in schools)
    total_provincial_majors = sum(school.provincial_first_class_majors for school in schools)
    
    # 找出各项指标最高的学校
    top_by_majors = sorted(schools, key=lambda x: x.undergraduate_majors, reverse=True)[:10]
    top_by_national = sorted(schools, key=lambda x: x.national_first_class_majors, reverse=True)[:10]
    top_by_total_majors = sorted(schools, key=lambda x: x.total_first_class_majors, reverse=True)[:10]
    
    # 一流专业占比排行（过滤掉没有专业数据的学校）
    valid_schools = [s for s in schools if s.undergraduate_majors > 0 and s.total_first_class_majors > 0]
    top_by_ratio = sorted(valid_schools, key=lambda x: x.first_class_major_ratio, reverse=True)[:10]
    
    stats = {
        "overview": {
            "total_schools": len(schools),
            "total_undergraduate_majors": total_undergraduate,
            "total_national_first_class_majors": total_national_majors,
            "total_provincial_first_class_majors": total_provincial_majors,
            "average_undergraduate_majors": round(total_undergraduate / len(schools), 2),
            "average_national_majors": round(total_national_majors / len(schools), 2),
            "average_provincial_majors": round(total_provincial_majors / len(schools), 2)
        },
        "top_10_by_undergraduate_majors": [
            {
                "rank": i + 1,
                "school": school.school_name,
                "undergraduate_majors": school.undergraduate_majors,
                "national_first_class_majors": school.national_first_class_majors,
                "provincial_first_class_majors": school.provincial_first_class_majors
            }
            for i, school in enumerate(top_by_majors)
        ],
        "top_10_by_national_first_class_majors": [
            {
                "rank": i + 1,
                "school": school.school_name,
                "national_first_class_majors": school.national_first_class_majors,
                "provincial_first_class_majors": school.provincial_first_class_majors,
                "total_first_class_majors": school.total_first_class_majors
            }
            for i, school in enumerate(top_by_national) if school.national_first_class_majors > 0
        ],
        "top_10_by_total_first_class_majors": [
            {
                "rank": i + 1,
                "school": school.school_name,
                "total_first_class_majors": school.total_first_class_majors,
                "national_first_class_majors": school.national_first_class_majors,
                "provincial_first_class_majors": school.provincial_first_class_majors
            }
            for i, school in enumerate(top_by_total_majors) if school.total_first_class_majors > 0
        ],
        "top_10_by_first_class_ratio": [
            {
                "rank": i + 1,
                "school": school.school_name,
                "first_class_major_ratio": round(school.first_class_major_ratio, 2),
                "total_first_class_majors": school.total_first_class_majors,
                "undergraduate_majors": school.undergraduate_majors
            }
            for i, school in enumerate(top_by_ratio)
        ]
    }
    
    return stats


def print_school_statistics(schools: List[SchoolIntroData]):
    """
    打印学校简介统计信息（控制台输出）
    """
    if not schools:
        print("📊 暂无学校简介数据")
        return
    
    print(f"\n📊 学校简介数据分析报告")
    print(f"{'='*60}")
    print(f"📈 基础统计:")
    print(f"  🏫 学校总数: {len(schools)}")
    
    # 统计各项指标
    total_undergraduate = sum(s.undergraduate_majors for s in schools)
    total_national_majors = sum(s.national_first_class_majors for s in schools)
    total_provincial_majors = sum(s.provincial_first_class_majors for s in schools)
    
    print(f"  📚 本科专业总数: {total_undergraduate}")
    print(f"  🥇 国家级一流专业总数: {total_national_majors}")
    print(f"  🥈 省级一流专业总数: {total_provincial_majors}")
    
    # 平均值
    count = len(schools)
    print(f"\n📊 平均指标:")
    print(f"  📚 平均本科专业数: {total_undergraduate/count:.1f}")
    print(f"  🥇 平均国家级一流专业数: {total_national_majors/count:.1f}")
    print(f"  🥈 平均省级一流专业数: {total_provincial_majors/count:.1f}")
    
    # 排行榜
    print(f"\n🏆 各项指标排行榜 (Top 5)")
    print(f"{'='*60}")
    
    # 本科专业数排行榜
    print(f"📚 本科专业数排行榜:")
    sorted_by_majors = sorted(schools, key=lambda x: x.undergraduate_majors, reverse=True)
    for i, school in enumerate(sorted_by_majors[:5], 1):
        print(f"  {i}. {school.school_name}: {school.undergraduate_majors}个专业")
    
    # 国家级一流专业排行榜
    print(f"\n🥇 国家级一流专业排行榜:")
    sorted_by_national = sorted(schools, key=lambda x: x.national_first_class_majors, reverse=True)
    for i, school in enumerate(sorted_by_national[:5], 1):
        if school.national_first_class_majors > 0:
            print(f"  {i}. {school.school_name}: {school.national_first_class_majors}个")
    
    # 综合实力排行榜（一流专业总数）
    print(f"\n🏅 一流专业综合排行榜:")
    sorted_by_total = sorted(schools, key=lambda x: x.total_first_class_majors, reverse=True)
    for i, school in enumerate(sorted_by_total[:5], 1):
        if school.total_first_class_majors > 0:
            print(f"  {i}. {school.school_name}: {school.total_first_class_majors}个 (国家级:{school.national_first_class_majors} + 省级:{school.provincial_first_class_majors})")
    
    # 一流专业占比排行榜
    print(f"\n📈 一流专业占比排行榜:")
    valid_schools = [s for s in schools if s.undergraduate_majors > 0 and s.total_first_class_majors > 0]
    sorted_by_ratio = sorted(valid_schools, key=lambda x: x.first_class_major_ratio, reverse=True)
    for i, school in enumerate(sorted_by_ratio[:5], 1):
        print(f"  {i}. {school.school_name}: {school.first_class_major_ratio:.1f}% ({school.total_first_class_majors}/{school.undergraduate_majors})")