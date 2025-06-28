"""AI问答系统主入口"""
import os
import sys
# 🔥 添加项目根目录到Python路径 🔥
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    
from src.AIquest.metric_processor import MetricDataProcessor
from src.AIquest.utils.directory_manager import DirectoryManager
# 🔥 导入别名配置 🔥
from src.AIquest.config import (
    METRIC_ALIASES, resolve_metric_name, get_metric_suggestions,
    is_school_extraction_enabled, enable_school_extraction
)

# 🔥 新增：数据文件管理命令 🔥
def show_data_files_status():
    """显示数据文件状态"""
    try:
        processor = MetricDataProcessor()
        processor.show_data_files_status()
    except Exception as e:
        print(f"❌ 显示数据文件状态时发生错误: {e}")

def switch_processing_mode():
    """切换处理模式"""
    try:
        current_mode = is_school_extraction_enabled()
        new_mode = not current_mode
        
        old_mode_name = "智能截取模式" if current_mode else "传统模式"
        new_mode_name = "智能截取模式" if new_mode else "传统模式"
        
        print(f"🔄 处理模式切换:")
        print(f"  从: {old_mode_name}")
        print(f"  到: {new_mode_name}")
        
        enable_school_extraction(new_mode)
        print(f"✅ 模式切换完成")
        print(f"💡 下次数据处理将使用新模式")
        
        return True
    except Exception as e:
        print(f"❌ 切换处理模式时发生错误: {e}")
        return False

def show_current_mode():
    """显示当前处理模式"""
    try:
        current_mode = is_school_extraction_enabled()
        mode_name = "智能截取模式" if current_mode else "传统模式"
        print(f"🔧 当前附件处理模式: {mode_name}")
        
        # 显示模式说明
        if current_mode:
            print("📍 智能截取模式特点:")
            print("  • 基于学校名称智能截取附件内容")
            print("  • 只提取与目标学校相关的片段")
            print("  • 数据存储在 consolidated_intelligent/ 目录")
        else:
            print("📄 传统模式特点:")
            print("  • 提取附件的完整内容")
            print("  • 保留所有原始信息")
            print("  • 数据存储在 consolidated/ 目录")
        
        return True
    except Exception as e:
        print(f"❌ 显示当前模式时发生错误: {e}")
        return False

def regenerate_data_files():
    """重新生成所有数据文件"""
    try:
        print("🔄 重新生成所有数据文件")
        print("⚠️  这将删除现有数据文件并重新创建")
        
        # 询问用户确认
        confirm = input("是否继续? (y/N): ").lower().strip()
        if confirm not in ['y', 'yes']:
            print("❌ 操作已取消")
            return False
        
        processor = MetricDataProcessor()
        success = processor.regenerate_all_data_files()
        
        if success:
            print("✅ 所有数据文件重新生成完成")
        else:
            print("⚠️  部分数据文件重新生成失败")
        
        return success
    except Exception as e:
        print(f"❌ 重新生成数据文件时发生错误: {e}")
        return False


def get_project_paths():
    """获取项目路径配置"""
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_script_dir))
    
    return {
        'questions_csv': os.path.join(project_root, "ai_evaluation_dataset_long.csv"),
        'output_base': os.path.join(project_root, "ai_evaluation_dataset_long"),
        'config': os.path.join(current_script_dir, "config.ini")
    }


def run_single_metric(metric_name, questions_csv_path, output_base_path):
    """运行单个指标的问答处理"""
    try:
        processor = MetricDataProcessor()
        
        output_path = f"{output_base_path}_{metric_name}_answers.csv"
        success = processor.process_metric_questions(metric_name, questions_csv_path, output_path)
        
        if success:
            print(f"✅ 指标 '{metric_name}' 处理完成: {output_path}")
        else:
            print(f"❌ 指标 '{metric_name}' 处理失败")
        
        return success
    except Exception as e:
        print(f"❌ 处理指标 '{metric_name}' 时发生错误: {e}")
        return False


def run_all_metrics(questions_csv_path, output_base_path):
    """运行所有指标的问答处理"""
    try:
        processor = MetricDataProcessor()
        
        success = processor.process_all_metrics(questions_csv_path, output_base_path)
        
        if success:
            print("✅ 所有指标处理完成")
        else:
            print("❌ 指标处理失败")
        
        return success
    except Exception as e:
        print(f"❌ 处理所有指标时发生错误: {e}")
        return False


def list_available_metrics():
    """列出所有可用的指标（按类别显示）"""
    try:
        processor = MetricDataProcessor()
        metrics = processor.get_available_metrics()
        
        print("📋 可用指标列表:")
        print("\n📚 学科相关指标:")
        for i, metric in enumerate(metrics['subject_metrics'], 1):
            print(f"  {i:2d}. {metric}")
        
        print("\n🎓 专业相关指标:")
        for i, metric in enumerate(metrics['major_metrics'], len(metrics['subject_metrics']) + 1):
            print(f"  {i:2d}. {metric}")
        
        # 🔥 添加别名显示 🔥
        print("\n🔗 常用别名:")
        print("\n  📚 学科指标别名:")
        subject_aliases = {k: v for k, v in METRIC_ALIASES.items() if v in metrics['subject_metrics']}
        grouped_aliases = {}
        for alias, real_name in subject_aliases.items():
            if real_name not in grouped_aliases:
                grouped_aliases[real_name] = []
            grouped_aliases[real_name].append(alias)
        
        for real_name, aliases in grouped_aliases.items():
            print(f"    • {real_name}:")
            for alias in aliases[:3]:  # 只显示前3个别名
                print(f"      - {alias}")
            if len(aliases) > 3:
                print(f"      - ... 还有 {len(aliases) - 3} 个别名")
        
        print("\n  🎓 专业指标别名:")
        major_aliases = {k: v for k, v in METRIC_ALIASES.items() if v in metrics['major_metrics']}
        grouped_aliases = {}
        for alias, real_name in major_aliases.items():
            if real_name not in grouped_aliases:
                grouped_aliases[real_name] = []
            grouped_aliases[real_name].append(alias)
        
        for real_name, aliases in grouped_aliases.items():
            print(f"    • {real_name}:")
            for alias in aliases[:3]:  # 只显示前3个别名
                print(f"      - {alias}")
            if len(aliases) > 3:
                print(f"      - ... 还有 {len(aliases) - 3} 个别名")
        
        # 🔥 显示数字快捷方式 🔥
        print("\n🔢 数字快捷方式:")
        number_aliases = {k: v for k, v in METRIC_ALIASES.items() if k.isdigit()}
        for num, metric in sorted(number_aliases.items()):
            print(f"  {num}. {metric}")
        
        print(f"\n总计: {len(metrics['all_metrics'])} 个指标，{len(METRIC_ALIASES)} 个别名")
        return metrics
    except Exception as e:
        print(f"❌ 获取指标列表时发生错误: {e}")
        return None


def show_statistics(questions_csv_path):
    """显示指标统计信息"""
    try:
        processor = MetricDataProcessor()
        stats = processor.get_metric_statistics(questions_csv_path)
        
        if not stats:
            print("❌ 无法获取统计信息")
            return
        
        print("📊 数据集统计信息:")
        print(f"  🏫 学校总数: {stats['total_schools']}")
        print(f"  ❓ 问题总数: {stats['total_questions']}")
        print(f"  ✅ 支持的指标: {len(stats['supported_metrics'])} 个")
        print(f"  ❌ 不支持的指标: {len(stats['unsupported_metrics'])} 个")
        
        if stats['supported_metrics']:
            print("\n✅ 支持的指标分布:")
            for metric, count in stats['supported_metrics'].items():
                print(f"  - {metric}: {count} 个问题")
        
        if stats['unsupported_metrics']:
            print("\n❌ 不支持的指标:")
            for metric, count in stats['unsupported_metrics'].items():
                print(f"  - {metric}: {count} 个问题")
    except Exception as e:
        print(f"❌ 显示统计信息时发生错误: {e}")


def validate_system():
    """验证系统状态"""
    try:
        print("🔍 验证系统状态...")
        processor = MetricDataProcessor()
        processor.validate_data_sources()
        
        # 额外验证：检查配置文件
        paths = get_project_paths()
        config_exists = os.path.exists(paths['config'])
        print(f"  📝 配置文件: {'✅ 存在' if config_exists else '❌ 不存在'} ({paths['config']})")
        
        # 检查问题文件
        questions_exists = os.path.exists(paths['questions_csv'])
        print(f"  📋 问题文件: {'✅ 存在' if questions_exists else '❌ 不存在'} ({paths['questions_csv']})")
        
        # 🔥 验证别名配置 🔥
        print(f"  🔗 可用别名: {len(METRIC_ALIASES)} 个")
        
    except Exception as e:
        print(f"❌ 验证系统状态时发生错误: {e}")


def initialize_directories():
    """初始化数据目录结构"""
    try:
        print("🏗️  初始化数据目录结构...")
        dir_manager = DirectoryManager()
        success = dir_manager.initialize_all_directories()
        
        if success:
            print("\n✅ 数据目录初始化完成")
            print("📝 请将相应的数据文件放置到对应的目录中：")
            print("   📊 ESI数据 → data/esi_subjects/")
            print("   🏆 双一流数据 → data/moepolicies/")  # 按您的习惯
            print("   📈 软科数据 → data/ruanke_subjects/")
            print("   📚 学科评估数据 → data/subject_evaluation/")  # 按您的习惯
            print("   🎓 专业数据 → data/undergraduate_majors/")
        else:
            print("\n❌ 数据目录初始化失败")
        
        return success
    except Exception as e:
        print(f"❌ 初始化目录时发生错误: {e}")
        return False


def check_directories():
    """检查目录状态"""
    try:
        dir_manager = DirectoryManager()
        dir_manager.check_directory_status()
    except Exception as e:
        print(f"❌ 检查目录状态时发生错误: {e}")


def migrate_data():
    """数据迁移工具"""
    try:
        dir_manager = DirectoryManager()
        dir_manager.migrate_existing_data()
    except Exception as e:
        print(f"❌ 数据迁移时发生错误: {e}")


def run_compatibility_mode():
    """🔥 运行兼容模式 - 使用原有的quest.py逻辑 🔥"""
    try:
        print("🔄 启动兼容模式...")
        print("使用原有的quest.py逻辑处理问题...")
        
        # 动态导入quest.py的主逻辑
        from . import quest
        
        # 这里可以调用quest.py中的主要逻辑
        # 您可以根据需要调整这部分
        print("✅ 兼容模式执行完成")
        return True
    except Exception as e:
        print(f"❌ 兼容模式执行失败: {e}")
        return False


def print_usage():
    """打印使用说明"""
    print("🔧 AI问答系统使用说明:")
    print("   python -m src.AIquest.main                    # 处理所有指标")
    print("   python -m src.AIquest.main list               # 列出可用指标")
    print("   python -m src.AIquest.main stats              # 显示统计信息")
    print("   python -m src.AIquest.main validate           # 验证系统状态")
    print("   python -m src.AIquest.main init               # 初始化数据目录")
    print("   python -m src.AIquest.main check              # 检查目录状态")
    print("   python -m src.AIquest.main migrate            # 迁移现有数据")
    print("   python -m src.AIquest.main compat             # 兼容模式（使用原quest.py）")
    print("   python -m src.AIquest.main <指标名称或别名>    # 处理特定指标")
    # 🔥 新增：处理模式说明 🔥
    print("\n🔧 处理模式说明:")
    print("   📍 智能截取模式: 基于学校名称智能提取附件相关内容")
    print("      • 只截取与目标学校相关的片段")
    print("      • 数据存储在 consolidated_intelligent/ 目录")
    print("      • 适合大文件和多学校混合数据")
    
    print("   📄 传统模式: 提取附件完整内容")
    print("      • 保留附件的所有原始信息")
    print("      • 数据存储在 consolidated/ 目录")
    print("      • 适合单一学校或小文件数据")
    print("\n🏗️  目录管理:")
    print("   init    - 创建所有必需的数据目录")
    print("   check   - 检查目录状态和文件数量")
    print("   migrate - 迁移现有数据到新目录结构")
    print("   compat  - 使用原有quest.py的处理逻辑")
    print("\n📊 支持的16个指标:")
    print("   🔬 学科指标: ESI前1%、ESI前1‰、双一流、教育部评估A类、软科前10%")
    print("   🎓 专业指标: 专业总数、专业认证、国家级一流专业、省级一流专业")
    print("   🏆 教学指标: 国家级教学成果奖、省级教学成果奖、青年教师竞赛")
    print("   📚 课程指标: 国家级一流课程、省级一流课程、国家级智慧平台、省级智慧平台")
    print("\n🔗 使用别名简化输入:")
    print("   python -m src.AIquest.main 1                  # ESI前1%学科数量")
    print("   python -m src.AIquest.main shuangyiliu        # 双一流学科")
    print("   python -m src.AIquest.main moe_eval           # 教育部评估A类")
    print("   python -m src.AIquest.main esi1%              # ESI前1%")
    print("   python -m src.AIquest.main ruanke             # 软科前10%")
    print("   python -m src.AIquest.main majors_total       # 专业总数")
    print("   python -m src.AIquest.main shuangyiliu        # 双一流学科")
    print("   python -m src.AIquest.main 10                 # 国家级教学成果奖")
    print("   python -m src.AIquest.main national_award     # 国家级教学成果奖")
    print("   python -m src.AIquest.main 12                 # 青年教师竞赛")
    print("   python -m src.AIquest.main youth_competition  # 青年教师竞赛")
    print("   python -m src.AIquest.main 13                 # 国家级一流课程")
    print("   python -m src.AIquest.main national_course    # 国家级一流课程")
    print("\n💡 处理带引号的指标名称:")
    print("   方法1: python -m src.AIquest.main shuangyiliu      # 使用别名（推荐）")
    print("   方法2: python -m src.AIquest.main '国家\"双一流\"学科数量'  # 单引号包围")
    print("   方法3: python -m src.AIquest.main \"国家\\\"双一流\\\"学科数量\"  # 转义字符")

def reprocess_data_with_attachments():
    """重新处理数据，确保包含附件内容"""
    print("🔄 重新处理数据以包含附件内容...")
    
    try:
        from src.AIquest.utils.data_reader import DataReader
        from src.AIquest.config import METRIC_DATA_MAPPING
        
        # 初始化组件
        data_reader = DataReader()
        
        # 重新整合所有已配置的指标数据
        for metric_name in METRIC_DATA_MAPPING.keys():
            print(f"🔄 重新整合指标: {metric_name}")
            consolidated_file = data_reader.consolidate_data_for_metric(metric_name)
            if consolidated_file:
                print(f"  ✅ 成功重新整合: {consolidated_file}")
            else:
                print(f"  ❌ 重新整合失败: {metric_name}")
        
        print("\n✅ 数据重新处理完成")
        
    except Exception as e:
        print(f"❌ 重新处理数据时发生错误: {e}")

def main():
    """主函数"""
    try:
        paths = get_project_paths()
        
        # 处理命令行参数
        if len(sys.argv) == 1:
            # 默认处理所有指标
            if not os.path.exists(paths['questions_csv']):
                print(f"❌ 问题文件不存在: {paths['questions_csv']}")
                print("💡 请先确保问题文件存在，或使用 'init' 命令初始化目录结构")
                return 1
            
            print("🚀 开始处理所有指标...")
            success = run_all_metrics(paths['questions_csv'], paths['output_base'])
            return 0 if success else 1
        
        command = sys.argv[1]
        
        if command == 'init':
            return 0 if initialize_directories() else 1
        elif command == 'check':
            check_directories()
            return 0
        elif command == 'migrate':
            migrate_data()
            return 0
        elif command == 'compat':
            return 0 if run_compatibility_mode() else 1
        elif command == 'list':
            metrics = list_available_metrics()
            return 0 if metrics else 1
        elif command == 'stats':
            if os.path.exists(paths['questions_csv']):
                show_statistics(paths['questions_csv'])
            else:
                print(f"❌ 问题文件不存在: {paths['questions_csv']}")
                print("💡 请先确保问题文件存在")
            return 0
        elif command == 'validate':
            validate_system()
            return 0
        elif command == 'reprocess':  # 🔥 新增重新处理数据命令 🔥
            reprocess_data_with_attachments()
            return 0
        elif command in ['help', '-h', '--help']:
            print_usage()
            return 0
        # 🔥 新增：数据文件管理命令 🔥
        elif command == 'files':
            show_data_files_status()
            return 0
        elif command == 'mode':
            return 0 if show_current_mode() else 1
        elif command == 'switch':
            return 0 if switch_processing_mode() else 1
        elif command == 'regen':
            return 0 if regenerate_data_files() else 1
        else:
            # 🔥 处理特定指标，支持别名解析 🔥
            if not os.path.exists(paths['questions_csv']):
                print(f"❌ 问题文件不存在: {paths['questions_csv']}")
                return 1
            
            input_metric_name = command
            # 🔥 使用别名解析功能 🔥
            metric_name = resolve_metric_name(input_metric_name)
            
            if not metric_name:
                print(f"❌ 不支持的指标: '{input_metric_name}'")
                
                # 🔥 提供建议 🔥
                suggestions = get_metric_suggestions(input_metric_name)
                if suggestions:
                    print(f"\n💡 您可能想要的是:")
                    for suggestion in suggestions[:5]:
                        print(f"  • {suggestion}")
                
                print(f"\n✅ 查看所有支持的指标和别名:")
                print(f"   python -m src.AIquest.main list")
                return 1
            
            # 🔥 显示别名映射信息 🔥
            print(f"🚀 开始处理指标: {metric_name}")
            if input_metric_name != metric_name:
                print(f"   (别名 '{input_metric_name}' → '{metric_name}')")
            
            try:
                processor = MetricDataProcessor()
                available_metrics = processor.get_available_metrics()['all_metrics']
                
                if metric_name not in available_metrics:
                    print(f"❌ 解析后的指标不在可用列表中: {metric_name}")
                    print("\n✅ 支持的指标:")
                    for metric in available_metrics:
                        print(f"  - {metric}")
                    return 1
                
                success = run_single_metric(metric_name, paths['questions_csv'], paths['output_base'])
                return 0 if success else 1
            except Exception as e:
                print(f"❌ 处理指标时发生错误: {e}")
                return 1
    
    except KeyboardInterrupt:
        print("\n⏹️  用户中断操作")
        return 1
    except Exception as e:
        print(f"❌ 程序执行时发生未预期的错误: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())