import json
import os
from datetime import datetime
from typing import List
from pathlib import Path

from models.course_data import ProvincialCourseData


def save_provincial_course_data(
    courses: List[ProvincialCourseData], 
    output_file: str,
    source_url: str
) -> None:
    """
    保存省级一流课程数据到JSON文件
    """
    print(f"💾 保存数据到: {output_file}")
    
    # 准备保存的数据
    save_data = {
        "extraction_info": {
            "timestamp": datetime.now().isoformat(),
            "source_url": source_url,
            "total_schools": len(courses),
            "total_courses_all_batches": sum(course.total for course in courses)
        },
        "schools": [course.dict() for course in courses]
    }
    
    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # 保存到JSON文件
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(save_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 数据保存成功!")
    print(f"  📊 学校总数: {len(courses)}")
    print(f"  📚 课程总数: {sum(course.total for course in courses)}")
    print(f"  📁 文件路径: {output_file}")


def generate_statistics(courses: List[ProvincialCourseData]) -> dict:
    """
    生成统计信息
    """
    if not courses:
        return {"error": "没有数据可统计"}
    
    # 计算各批次总数
    total_first = sum(course.first for course in courses)
    total_second = sum(course.second for course in courses)
    total_third = sum(course.third for course in courses)
    total_all = sum(course.total for course in courses)
    
    # 找出课程最多的学校
    top_schools = sorted(courses, key=lambda x: x.total, reverse=True)[:10]
    
    stats = {
        "overview": {
            "total_schools": len(courses),
            "total_first_batch": total_first,
            "total_second_batch": total_second,
            "total_third_batch": total_third,
            "total_all_batches": total_all,
            "average_per_school": round(total_all / len(courses), 2)
        },
        "top_10_schools": [
            {
                "rank": i + 1,
                "school": school.school,
                "first": school.first,
                "second": school.second,
                "third": school.third,
                "total": school.total
            }
            for i, school in enumerate(top_schools)
        ]
    }
    
    return stats