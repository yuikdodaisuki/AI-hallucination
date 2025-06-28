from pydantic import BaseModel
from typing import List


class ProvincialCourseData(BaseModel):
    """省级一流课程数据模型"""
    school: str
    first: int
    second: int
    third: int
    total: int
    
    def __str__(self):
        return f"{self.school}: 第一批({self.first}) 第二批({self.second}) 第三批({self.third}) 合计({self.total})"