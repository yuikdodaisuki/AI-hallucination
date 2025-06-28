import json
import csv
import pandas as pd
from pathlib import Path
from typing import List, Dict
from models.course import Course, SchoolCourseSummary


def read_school_list_from_csv(csv_file_path: str) -> List[str]:
    """
    从CSV文件中读取学校名称列表
    
    Args:
        csv_file_path: CSV文件路径
        
    Returns:
        List[str]: 学校名称列表
    """
    try:
        df = pd.read_csv(csv_file_path, encoding='utf-8')
        # 假设学校名称在第一列，去重
        schools = df.iloc[:, 0].dropna().unique().tolist()
        print(f"📚 从 {csv_file_path} 读取到 {len(schools)} 所学校")
        return schools
    except Exception as e:
        print(f"❌ 读取学校列表失败: {e}")
        return []


def save_courses_to_json(all_courses: List[Course], output_file: str):
    """
    保存课程数据到JSON文件
    
    Args:
        all_courses: 所有课程数据
        output_file: 输出文件路径
    """
    if not all_courses:
        print("❌ 没有课程数据需要保存")
        return
    
    # 转换为字典格式
    courses_data = [course.model_dump() for course in all_courses]
    
    # 创建输出目录
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 保存JSON文件
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(courses_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已保存 {len(all_courses)} 条课程数据到 {output_file}")


def save_school_summary_to_json(school_summaries: List[SchoolCourseSummary], output_file: str):
    """
    保存学校课程汇总数据到JSON文件
    
    Args:
        school_summaries: 学校课程汇总列表
        output_file: 输出文件路径
    """
    if not school_summaries:
        print("❌ 没有学校汇总数据需要保存")
        return
    
    # 转换为字典格式
    summary_data = []
    for summary in school_summaries:
        summary_dict = summary.model_dump()
        summary_data.append(summary_dict)
    
    # 创建输出目录
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 保存JSON文件
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(summary_data, f, ensure_ascii=False, indent=2)
    
    # 统计信息
    total_courses = sum(summary.total_courses for summary in school_summaries)
    print(f"✅ 已保存 {len(school_summaries)} 所学校的课程汇总数据到 {output_file}")
    print(f"📊 总计课程数量: {total_courses}")


def generate_statistics(school_summaries: List[SchoolCourseSummary]) -> Dict:
    """
    生成统计信息
    
    Args:
        school_summaries: 学校课程汇总列表
        
    Returns:
        Dict: 统计信息字典
    """
    if not school_summaries:
        return {}
    
    total_schools = len(school_summaries)
    total_courses = sum(summary.total_courses for summary in school_summaries)
    
    # 按课程数量排序
    sorted_schools = sorted(school_summaries, key=lambda x: x.total_courses, reverse=True)
    
    # 课程数量分布
    course_counts = [summary.total_courses for summary in school_summaries]
    avg_courses = sum(course_counts) / len(course_counts) if course_counts else 0
    max_courses = max(course_counts) if course_counts else 0
    min_courses = min(course_counts) if course_counts else 0
    
    stats = {
        "total_schools": total_schools,
        "total_courses": total_courses,
        "average_courses_per_school": round(avg_courses, 2),
        "max_courses_school": {
            "name": sorted_schools[0].school if sorted_schools else "",
            "course_count": max_courses
        },
        "min_courses_school": {
            "name": sorted_schools[-1].school if sorted_schools else "",
            "course_count": min_courses
        },
        "top_5_schools": [
            {"name": school.school, "course_count": school.total_courses}
            for school in sorted_schools[:5]
        ]
    }
    
    return stats