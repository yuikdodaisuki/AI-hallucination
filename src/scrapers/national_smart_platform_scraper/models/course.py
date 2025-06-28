from pydantic import BaseModel
from typing import Optional, List


class Course(BaseModel):
    """
    课程数据模型
    """
    school: str  # 学校名称
    course_name: str  # 课程名称
    teacher: str  # 任课老师


class SchoolCourseSummary(BaseModel):
    """
    学校课程汇总模型
    """
    school: str  # 学校名称
    total_courses: int  # 总课程数量
    courses: List[Course]  # 课程列表