"""指标数据处理器"""
import csv
import os
from src.AIquest.utils.llm_client import LLMClient
from src.AIquest.utils.data_reader import DataReader
from src.AIquest.utils.question_processor import QuestionProcessor
from src.AIquest.utils.file_utils import FileUtils
from src.AIquest.config import (
    METRIC_DATA_MAPPING, OUTPUT_CONFIG, METRIC_CATEGORIES, DATA_SOURCES,
    is_school_extraction_enabled, get_consolidated_dir_path
)


class MetricDataProcessor:
    """根据指标类型处理数据和问题的主类"""
    
    def __init__(self, config_path=None):
        self.llm_client = LLMClient(config_path)
        self.data_reader = DataReader()
        self.question_processor = QuestionProcessor(self.llm_client, self.data_reader)
        self.file_utils = FileUtils()
        # 🔥 新增：显示当前处理模式 🔥
        mode = "智能截取模式" if is_school_extraction_enabled() else "传统模式"
        print(f"📋 MetricDataProcessor 初始化完成，当前附件处理模式: {mode}")
    
    def process_metric_questions(self, metric_name, questions_csv_path, output_csv_path):
        """处理特定指标的问题 - 支持动态数据文件选择"""
        print(f"\n开始处理指标: {metric_name}")
        
        # 显示当前处理模式
        mode = "智能截取模式" if is_school_extraction_enabled() else "传统模式"
        print(f"📂 当前附件处理模式: {mode}")
        
        # 验证指标是否在支持的列表中
        if not self._validate_metric(metric_name):
            return False
        
        # 🔥 修改：使用新的数据文件获取逻辑 🔥
        # 1. 首先检查是否有对应模式的现成文件
        consolidated_data_path = self._get_or_create_metric_data_file(metric_name)
        if not consolidated_data_path:
            print(f"错误: 未能为指标 '{metric_name}' 获取或创建数据文件")
            return False
        
        # 2. 显示使用的数据文件信息
        self._show_data_file_info(consolidated_data_path)
        
        # 3. 筛选出该指标的问题
        metric_questions = self.question_processor.filter_questions_by_metric(questions_csv_path, metric_name)
        if not metric_questions:
            print(f"警告: 未找到指标 '{metric_name}' 的相关问题")
            return False
        
        # 4. 处理问题并获取答案
        return self.question_processor.process_metric_questions(
            metric_questions, consolidated_data_path, output_csv_path, metric_name
        )
    
    def _get_or_create_metric_data_file(self, metric_name):
        """🔥 新增：获取或创建指标对应的数据文件 🔥"""
        # 首先尝试查找现有文件
        existing_file = self.data_reader.find_existing_consolidated_file(metric_name)
        
        if existing_file:
            # 检查文件是否与当前模式匹配
            file_info = self.data_reader.get_consolidated_file_info(metric_name)
            if file_info:
                current_mode = "intelligent" if is_school_extraction_enabled() else "traditional"
                file_mode = file_info.get('processing_mode', 'unknown')
                
                if file_mode == current_mode:
                    print(f"  ✅ 找到匹配当前模式的数据文件")
                    return existing_file
                else:
                    print(f"  ⚠️  现有文件模式不匹配:")
                    print(f"      文件模式: {file_mode}")
                    print(f"      当前模式: {current_mode}")
                    print(f"  🔄 将重新生成匹配当前模式的数据文件...")
        else:
            print(f"  📝 未找到现有数据文件，将重新生成...")
        
        # 重新生成数据文件
        data_sources = METRIC_DATA_MAPPING.get(metric_name, [])
        if not data_sources:
            print(f"错误: 未找到指标 '{metric_name}' 对应的数据源配置")
            return None
        
        print(f"  🔄 重新整合数据源: {data_sources}")
        return self.data_reader.consolidate_data_for_metric(metric_name, data_sources)
    
    def _show_data_file_info(self, data_file_path):
        """🔥 新增：显示数据文件信息 🔥"""
        if not data_file_path or not os.path.exists(data_file_path):
            print(f"  ❌ 数据文件不存在: {data_file_path}")
            return
        
        try:
            import json
            with open(data_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            file_name = os.path.basename(data_file_path)
            processing_mode = data.get('processing_mode', 'unknown')
            total_items = data.get('total_items', 0)
            status = data.get('status', 'unknown')
            generated_at = data.get('generated_at', 'unknown')
            
            print(f"  📄 使用数据文件: {file_name}")
            print(f"      处理模式: {processing_mode}")
            print(f"      数据条数: {total_items}")
            print(f"      文件状态: {status}")
            print(f"      生成时间: {generated_at}")
            
        except Exception as e:
            print(f"  ⚠️  无法读取数据文件信息: {e}")
    
    def _validate_metric(self, metric_name):
        """验证指标是否在新的支持列表中"""
        all_supported_metrics = (
            METRIC_CATEGORIES['subject_metrics'] + 
            METRIC_CATEGORIES['major_metrics'] + 
            METRIC_CATEGORIES['teaching_metrics']
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
            for metric in METRIC_CATEGORIES['teaching_metrics']:
                print(f"    - {metric}")
            return False
        
        return True
    
    def process_all_metrics(self, questions_csv_path, output_base_path):
        """处理所有指标的问题 - 支持动态数据文件"""
        print(f"\n🚀 开始处理所有指标")
        mode = "智能截取模式" if is_school_extraction_enabled() else "传统模式"
        print(f"📂 当前附件处理模式: {mode}")
        
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
        
        # 🔥 新增：为所有指标预先准备数据文件 🔥
        print(f"\n📊 预先准备所有指标的数据文件...")
        prepared_files = {}
        for i, metric in enumerate(supported_metrics, 1):
            print(f"\n[{i}/{len(supported_metrics)}] 准备指标: {metric}")
            data_file = self._get_or_create_metric_data_file(metric)
            if data_file:
                prepared_files[metric] = data_file
                print(f"  ✅ 数据文件准备完成")
            else:
                print(f"  ❌ 数据文件准备失败")
        
        print(f"\n📈 数据文件准备汇总:")
        print(f"  成功: {len(prepared_files)}/{len(supported_metrics)} 个指标")
        
        # 为每个有数据文件的指标处理问题
        all_results = []
        for i, metric in enumerate(supported_metrics, 1):
            if metric in prepared_files:
                print(f"\n[{i}/{len(supported_metrics)}] 🔄 处理指标: {metric}")
                output_path = f"{output_base_path}_{metric}_answers.csv"
                success = self.process_metric_questions(metric, questions_csv_path, output_path)
                if success:
                    all_results.append(output_path)
                    print(f"  ✅ 指标 '{metric}' 处理完成")
                else:
                    print(f"  ❌ 指标 '{metric}' 处理失败")
            else:
                print(f"\n[{i}/{len(supported_metrics)}] ⏭️  跳过指标 '{metric}' (无可用数据)")
        
        # 合并所有结果
        if all_results:
            final_output_path = f"{output_base_path}_all_answers.csv"
            print(f"\n📋 合并所有结果到: {final_output_path}")
            self.file_utils.merge_csv_files(all_results, final_output_path)
            print(f"✅ 所有指标处理完成，共生成 {len(all_results)} 个结果文件")
        else:
            print(f"\n❌ 未生成任何结果文件")
        
        return len(all_results) > 0
    
    # 🔥 新增：数据文件管理方法 🔥
    def show_data_files_status(self):
        """显示所有指标的数据文件状态"""
        print("📂 数据文件状态汇总")
        print("=" * 60)
        
        current_mode = "intelligent" if is_school_extraction_enabled() else "traditional"
        mode_name = "智能截取模式" if current_mode == "intelligent" else "传统模式"
        print(f"🔧 当前模式: {mode_name}")
        print()
        
        all_files = self.data_reader.list_all_consolidated_files()
        
        if not all_files:
            print("❌ 未找到任何数据文件")
            return
        
        # 按指标显示
        for metric_name, modes in all_files.items():
            print(f"📊 {metric_name}:")
            
            # 当前模式的文件
            if current_mode in modes:
                info = modes[current_mode]
                if 'error' in info:
                    print(f"  ✅ 当前模式: ❌ {info['error']}")
                else:
                    print(f"  ✅ 当前模式: {info['total_items']} 条记录 (修改: {info['modified_time']})")
            else:
                print(f"  ⚪ 当前模式: 无数据文件")
            
            # 其他模式的文件
            other_mode = "traditional" if current_mode == "intelligent" else "intelligent"
            if other_mode in modes:
                info = modes[other_mode]
                other_mode_name = "传统模式" if other_mode == "traditional" else "智能模式"
                if 'error' in info:
                    print(f"  📋 {other_mode_name}: ❌ {info['error']}")
                else:
                    print(f"  📋 {other_mode_name}: {info['total_items']} 条记录 (修改: {info['modified_time']})")
            
            print()
    
    def regenerate_all_data_files(self):
        """🔥 新增：重新生成所有数据文件 🔥"""
        print("🔄 重新生成所有指标的数据文件")
        mode = "智能截取模式" if is_school_extraction_enabled() else "传统模式"
        print(f"📂 当前模式: {mode}")
        print()
        
        success_count = 0
        total_count = len(METRIC_DATA_MAPPING)
        
        for i, metric_name in enumerate(METRIC_DATA_MAPPING.keys(), 1):
            print(f"[{i}/{total_count}] 🔄 重新生成: {metric_name}")
            
            data_sources = METRIC_DATA_MAPPING[metric_name]
            consolidated_file = self.data_reader.consolidate_data_for_metric(metric_name, data_sources)
            
            if consolidated_file:
                print(f"  ✅ 生成成功")
                success_count += 1
            else:
                print(f"  ❌ 生成失败")
            print()
        
        print(f"📈 重新生成完成: {success_count}/{total_count} 个指标")
        return success_count == total_count
    
    def _validate_metric_silent(self, metric_name):
        """静默验证指标（不打印错误信息）"""
        all_supported_metrics = (
            METRIC_CATEGORIES['subject_metrics'] + 
            METRIC_CATEGORIES['major_metrics'] +
            METRIC_CATEGORIES['teaching_metrics']
        )
        return metric_name in all_supported_metrics
    
    def get_available_metrics(self):
        """获取所有可用的指标（按类别分组）"""
        return {
            'subject_metrics': METRIC_CATEGORIES['subject_metrics'],
            'major_metrics': METRIC_CATEGORIES['major_metrics'],
            'teaching_metrics': METRIC_CATEGORIES['teaching_metrics'],
            'all_metrics': METRIC_CATEGORIES['subject_metrics'] + METRIC_CATEGORIES['major_metrics'] + METRIC_CATEGORIES['teaching_metrics']
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