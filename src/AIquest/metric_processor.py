"""指标数据处理器"""
import csv
import os
from src.AIquest.utils.llm_client import LLMClient
from src.AIquest.utils.data_reader import DataReader
from src.AIquest.utils.question_processor import QuestionProcessor
from src.AIquest.utils.file_utils import FileUtils
from src.AIquest.config import METRIC_DATA_MAPPING, OUTPUT_CONFIG, METRIC_CATEGORIES


class MetricDataProcessor:
    """根据指标类型处理数据和问题的主类"""
    
    def __init__(self, config_path=None):
        self.llm_client = LLMClient(config_path)
        self.data_reader = DataReader()
        self.question_processor = QuestionProcessor(self.llm_client, self.data_reader)
        self.file_utils = FileUtils()
    
    def process_metric_questions(self, metric_name, questions_csv_path, output_csv_path):
        """处理特定指标的问题"""
        print(f"\n开始处理指标: {metric_name}")
        
        # 验证指标是否在支持的列表中
        if not self._validate_metric(metric_name):
            return False
        
        # 1. 根据指标获取需要的数据源
        data_sources = METRIC_DATA_MAPPING.get(metric_name, [])
        if not data_sources:
            print(f"警告: 未找到指标 '{metric_name}' 对应的数据源配置")
            return False
        
        # 2. 整合对应的数据
        consolidated_data_path = self.data_reader.consolidate_data_for_metric(metric_name, data_sources)
        if not consolidated_data_path:
            print(f"错误: 未能为指标 '{metric_name}' 整合数据")
            return False
        
        # 3. 筛选出该指标的问题
        metric_questions = self.question_processor.filter_questions_by_metric(questions_csv_path, metric_name)
        if not metric_questions:
            print(f"警告: 未找到指标 '{metric_name}' 的相关问题")
            return False
        
        # 4. 处理问题并获取答案
        return self.question_processor.process_metric_questions(
            metric_questions, consolidated_data_path, output_csv_path, metric_name
        )
    
    def _validate_metric(self, metric_name):
        """验证指标是否在新的支持列表中"""
        all_supported_metrics = (
            METRIC_CATEGORIES['subject_metrics'] + 
            METRIC_CATEGORIES['major_metrics']
        )
        
        if metric_name not in all_supported_metrics:
            print(f"❌ 不支持的指标: {metric_name}")
            print("✅ 支持的指标列表:")
            print("  📚 学科指标:")
            for metric in METRIC_CATEGORIES['subject_metrics']:
                print(f"    - {metric}")
            print("  🎓 专业指标:")
            for metric in METRIC_CATEGORIES['major_metrics']:
                print(f"    - {metric}")
            return False
        
        return True
    
    def process_all_metrics(self, questions_csv_path, output_base_path):
        """处理所有指标的问题"""
        # 获取所有唯一的指标
        all_metrics = set()
        try:
            with open(questions_csv_path, mode='r', encoding=OUTPUT_CONFIG['file_encoding']) as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    metric = row.get('指标名称')
                    if metric and metric != '待填充':
                        all_metrics.add(metric)
        except Exception as e:
            print(f"读取问题文件失败: {e}")
            return False
        
        print(f"发现 {len(all_metrics)} 个不同的指标需要处理")
        
        # 验证所有指标都被支持
        unsupported_metrics = []
        for metric in all_metrics:
            if not self._validate_metric_silent(metric):
                unsupported_metrics.append(metric)
        
        if unsupported_metrics:
            print(f"⚠️  发现 {len(unsupported_metrics)} 个不支持的指标:")
            for metric in unsupported_metrics:
                print(f"    - {metric}")
            print("请检查配置文件或更新指标映射")
        
        # 只处理支持的指标
        supported_metrics = [m for m in all_metrics if self._validate_metric_silent(m)]
        print(f"✅ 将处理 {len(supported_metrics)} 个支持的指标")
        
        # 为每个指标单独处理
        all_results = []
        for metric in supported_metrics:
            output_path = f"{output_base_path}_{metric}_answers.csv"
            success = self.process_metric_questions(metric, questions_csv_path, output_path)
            if success:
                all_results.append(output_path)
        
        # 合并所有结果
        if all_results:
            final_output_path = f"{output_base_path}_all_answers.csv"
            self.file_utils.merge_csv_files(all_results, final_output_path)
        
        return True
    
    def _validate_metric_silent(self, metric_name):
        """静默验证指标（不打印错误信息）"""
        all_supported_metrics = (
            METRIC_CATEGORIES['subject_metrics'] + 
            METRIC_CATEGORIES['major_metrics']
        )
        return metric_name in all_supported_metrics
    
    def get_available_metrics(self):
        """获取所有可用的指标（按类别分组）"""
        return {
            'subject_metrics': METRIC_CATEGORIES['subject_metrics'],
            'major_metrics': METRIC_CATEGORIES['major_metrics'],
            'all_metrics': METRIC_CATEGORIES['subject_metrics'] + METRIC_CATEGORIES['major_metrics']
        }
    
    def validate_data_sources(self):
        """验证数据源是否存在"""
        print("🔍 验证数据源...")
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        for metric, sources in METRIC_DATA_MAPPING.items():
            print(f"  📊 指标: {metric}")
            for source in sources:
                source_path = os.path.join(current_dir, '../../data', 
                                         DATA_SOURCES.get(source, source).replace('../../data/', ''))
                exists = os.path.exists(source_path)
                status = '✅' if exists else '❌'
                print(f"    {status} 数据源 {source}: {source_path}")
    
    def get_metric_statistics(self, questions_csv_path):
        """获取指标统计信息"""
        metric_stats = {}
        school_count = 0
        
        try:
            with open(questions_csv_path, mode='r', encoding=OUTPUT_CONFIG['file_encoding']) as csvfile:
                reader = csv.DictReader(csvfile)
                schools = set()
                
                for row in reader:
                    metric = row.get('指标名称')
                    school = row.get('学校名称')
                    
                    if metric and metric != '待填充':
                        if metric not in metric_stats:
                            metric_stats[metric] = 0
                        metric_stats[metric] += 1
                    
                    if school:
                        schools.add(school)
                
                school_count = len(schools)
        
        except Exception as e:
            print(f"统计指标信息失败: {e}")
            return None
        
        return {
            'total_schools': school_count,
            'total_questions': sum(metric_stats.values()),
            'metrics_distribution': metric_stats,
            'supported_metrics': {k: v for k, v in metric_stats.items() if self._validate_metric_silent(k)},
            'unsupported_metrics': {k: v for k, v in metric_stats.items() if not self._validate_metric_silent(k)}
        }