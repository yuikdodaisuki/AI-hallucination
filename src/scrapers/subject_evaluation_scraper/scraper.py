from .data_extrator import SubjectEvaluationExtractor
from .config import OUTPUT_OPTIONS


class SubjectEvaluationScraper:
    """学科评估爬虫"""
    
    def __init__(self):
        self.extractor = SubjectEvaluationExtractor()
    
    def scrape_all_data(self, output_format=None):
        """爬取所有学科评估数据
        
        Args:
            output_format: 'raw', 'processed', 'both'
        """
        return self.extractor.extract_and_convert(output_format)
    
    def scrape_raw_data_only(self):
        """仅爬取原始数据"""
        return self.extractor.extract_raw_data(save_to_file=True)
    
    def scrape_processed_data_only(self):
        """仅爬取并转换为扁平格式"""
        return self.extractor.extract_and_convert(output_format='processed')
    
    def convert_existing_data(self):
        """转换已存在的原始数据"""
        return self.extractor.convert_data_format(save_to_file=True)


def start_scrape(output_format=None):
    """启动爬虫的便捷函数
    
    Args:
        output_format: 'raw', 'processed', 'both'
    """
    scraper = SubjectEvaluationScraper()
    return scraper.scrape_all_data(output_format)


# 🔥 新增：便捷的预设函数 🔥
def scrape_raw_only():
    """只提取原始数据"""
    return start_scrape('raw')


def scrape_processed_only():
    """只提取转换后数据"""
    return start_scrape('processed')


def scrape_both():
    """提取两种格式的数据"""
    return start_scrape('both')