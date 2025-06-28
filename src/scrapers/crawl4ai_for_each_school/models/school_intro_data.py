from dataclasses import dataclass
from typing import Optional
import json


@dataclass
class SchoolIntroData:
    """学校简介核心信息数据模型"""
    school_name: str  # 学校名称
    undergraduate_majors: int  # 本科专业总数
    national_first_class_majors: int  # 国家级一流本科专业建设点
    provincial_first_class_majors: int  # 省级一流本科专业建设点
    source_url: str  # 数据来源URL
    crawl_timestamp: Optional[str] = None  # 爬取时间戳
    
    def __str__(self):
        return (f"🏫 {self.school_name}\n"
                f"   📚 本科专业: {self.undergraduate_majors}个\n"
                f"   🥇 国家级一流专业: {self.national_first_class_majors}个\n"
                f"   🥈 省级一流专业: {self.provincial_first_class_majors}个\n")
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'school_name': self.school_name,
            'undergraduate_majors': self.undergraduate_majors,
            'national_first_class_majors': self.national_first_class_majors,
            'provincial_first_class_majors': self.provincial_first_class_majors,
            'source_url': self.source_url,
            'crawl_timestamp': self.crawl_timestamp
        }
    
    def to_json(self):
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
    
    @property
    def total_first_class_majors(self):
        """一流专业总数"""
        return self.national_first_class_majors + self.provincial_first_class_majors
    
    
    @property
    def first_class_major_ratio(self):
        """一流专业占比"""
        if self.undergraduate_majors == 0:
            return 0.0
        return (self.total_first_class_majors / self.undergraduate_majors) * 100


@dataclass
class CrawlResult:
    """爬取结果数据模型"""
    success: bool
    school_name: str
    data: Optional[SchoolIntroData] = None
    error_message: Optional[str] = None
    url: str = ""
    
    def __str__(self):
        if self.success:
            return f"✅ {self.school_name}: 爬取成功"
        else:
            return f"❌ {self.school_name}: {self.error_message}"