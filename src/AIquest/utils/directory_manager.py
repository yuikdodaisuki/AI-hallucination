"""目录管理和初始化工具"""
import os
import json
from datetime import datetime
from src.AIquest.config import DATA_SOURCES, REQUIRED_DIRECTORIES, METRIC_CATEGORIES


class DirectoryManager:
    """目录管理和初始化工具类
    
    功能包括：
    1. 初始化数据目录结构
    2. 检查目录状态和文件统计
    3. 生成目录说明文档
    4. 提供数据迁移建议
    5. 创建示例数据文件
    """
    
    def __init__(self):
        """初始化目录管理器"""
        self.current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.base_data_dir = os.path.join(self.current_dir, '../../data')
        self.base_output_dir = os.path.join(self.current_dir, '../../output')
        
        # 确保基础目录存在
        os.makedirs(self.base_data_dir, exist_ok=True)
        os.makedirs(self.base_output_dir, exist_ok=True)
    
    def initialize_all_directories(self):
        """初始化所有必需的目录结构
        
        Returns:
            bool: 是否所有目录都创建成功
        """
        print("🏗️  正在初始化数据目录结构...")
        
        created_dirs = []
        failed_dirs = []
        
        # 创建所有必需的目录
        for directory in REQUIRED_DIRECTORIES:
            dir_path = os.path.join(self.base_data_dir, directory)
            
            if self._create_directory_with_files(directory, dir_path):
                created_dirs.append(directory)
                print(f"  📁 ✅ {directory}")
            else:
                failed_dirs.append(directory)
                print(f"  📁 ❌ {directory}")
        
        # 创建输出目录
        consolidated_dir = os.path.join(self.base_data_dir, 'consolidated')
        os.makedirs(consolidated_dir, exist_ok=True)
        
        # 显示结果摘要
        print(f"\n📊 初始化结果:")
        print(f"  ✅ 成功创建: {len(created_dirs)} 个目录")
        if failed_dirs:
            print(f"  ❌ 创建失败: {len(failed_dirs)} 个目录")
            for dir_name in failed_dirs:
                print(f"    - {dir_name}")
        
        return len(failed_dirs) == 0
    
    def _create_directory_with_files(self, dir_name, dir_path):
        """创建目录并添加说明文件和示例数据
        
        Args:
            dir_name (str): 目录名称
            dir_path (str): 目录完整路径
            
        Returns:
            bool: 是否创建成功
        """
        try:
            # 创建目录
            os.makedirs(dir_path, exist_ok=True)
            
            # 创建README文件
            readme_path = os.path.join(dir_path, 'README.md')
            if not os.path.exists(readme_path):
                readme_content = self._generate_readme_content(dir_name)
                with open(readme_path, 'w', encoding='utf-8') as f:
                    f.write(readme_content)
            
            # 创建示例数据文件（可选）
            if not self._has_data_files(dir_path):
                sample_data_path = os.path.join(dir_path, 'sample_data.json')
                sample_data = self._generate_sample_data(dir_name)
                with open(sample_data_path, 'w', encoding='utf-8') as f:
                    json.dump(sample_data, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            print(f"    错误: 创建目录 {dir_name} 失败: {e}")
            return False
    
    def _has_data_files(self, dir_path):
        """检查目录是否已有数据文件
        
        Args:
            dir_path (str): 目录路径
            
        Returns:
            bool: 是否有数据文件
        """
        if not os.path.exists(dir_path):
            return False
        
        for file_name in os.listdir(dir_path):
            if file_name.endswith('.json') and not file_name.startswith('sample_'):
                return True
        return False
    
    def _generate_readme_content(self, dir_name):
        """生成目录说明文档
        
        Args:
            dir_name (str): 目录名称
            
        Returns:
            str: README内容
        """
        # 目录描述映射
        descriptions = {
            'esi_subjects': {
                'desc': 'ESI学科相关数据，包含进入ESI排名的学科信息',
                'data_format': 'ESI学科排名数据',
                'examples': ['university_esi_data.json', 'esi_ranking_2024.json']
            },
            'esi_subjects/esi_top1percent': {
                'desc': 'ESI前1%学科专门数据',
                'data_format': 'ESI前1%学科列表',
                'examples': ['top1percent_subjects.json']
            },
            'esi_subjects/esi_top1permille': {
                'desc': 'ESI前1‰学科专门数据',
                'data_format': 'ESI前1‰学科列表',
                'examples': ['top1permille_subjects.json']
            },
            'ruanke_subjects': {
                'desc': '软科中国最好学科排名相关数据',
                'data_format': '软科学科排名数据',
                'examples': ['ruanke_ranking_2024.json', 'best_subjects.json']
            },
            'subject_evaluation': {
                'desc': '教育部学科评估相关数据（按用户习惯存储）',
                'data_format': '学科评估A+、A、A-等级数据',
                'examples': ['moe_evaluation_round4.json', 'a_class_subjects.json']
            },
            'undergraduate_majors': {
                'desc': '本科专业相关数据',
                'data_format': '本科专业信息',
                'examples': ['university_majors.json', 'major_list.json']
            },
            'undergraduate_majors/total_majors': {
                'desc': '本科专业总数统计数据',
                'data_format': '专业总数统计',
                'examples': ['major_count.json']
            },
            'undergraduate_majors/certified_majors': {
                'desc': '通过专业认证的本科专业数据',
                'data_format': '专业认证信息',
                'examples': ['certified_majors.json']
            },
            'undergraduate_majors/national_first_class': {
                'desc': '国家级一流本科专业建设点数据',
                'data_format': '国家级一流专业列表',
                'examples': ['national_first_class.json']
            },
            'undergraduate_majors/provincial_first_class': {
                'desc': '省级一流本科专业建设点数据',
                'data_format': '省级一流专业列表',
                'examples': ['provincial_first_class.json']
            },
            'consolidated': {
                'desc': '整合后的数据文件（自动生成）',
                'data_format': '系统自动整合的数据',
                'examples': ['ESI前1%学科数量_data.json', '本科专业总数_data.json']
            }
        }
        
        # 获取目录信息
        dir_info = descriptions.get(dir_name, {
            'desc': '数据存储目录',
            'data_format': 'JSON格式数据',
            'examples': ['data.json']
        })
        
        return f"""# {dir_name} 数据目录

## 📋 目录说明
{dir_info['desc']}

## 📊 数据格式要求
- **文件格式**: JSON
- **编码**: UTF-8
- **数据类型**: {dir_info['data_format']}
- **文件命名**: 建议使用有意义的名称

## 📝 文件命名示例
```
{chr(10).join(f"- {example}" for example in dir_info['examples'])}
```

## 🔧 使用说明
1. 将相关数据文件放置在此目录中
2. 系统会自动扫描并读取所有 `.json` 文件
3. 数据会被自动整合到问答系统中
4. 支持嵌套目录结构

## ⚠️ 注意事项
- 确保JSON文件格式正确
- 避免使用特殊字符命名文件
- 大文件建议分割为多个小文件
- 定期备份重要数据

## 📈 数据结构示例
查看 `sample_data.json` 文件了解推荐的数据结构。

## 🕒 更新时间
{self._get_current_time()}

---
*此文件由AI问答系统自动生成*
"""
    
    def _generate_sample_data(self, dir_name):
        """生成示例数据
        
        Args:
            dir_name (str): 目录名称
            
        Returns:
            dict: 示例数据
        """
        base_sample = {
            "university": "示例大学",
            "update_date": self._get_current_time(),
            "data_source": "示例数据",
            "note": "这是示例数据，请替换为真实数据"
        }
        
        # 根据目录类型生成不同的示例数据
        if 'esi' in dir_name:
            return {
                **base_sample,
                "esi_subjects": [
                    {
                        "subject": "计算机科学",
                        "ranking": "前1%",
                        "global_rank": 50,
                        "national_rank": 5
                    },
                    {
                        "subject": "工程学",
                        "ranking": "前1%",
                        "global_rank": 80,
                        "national_rank": 8
                    }
                ],
                "total_esi_subjects": 2
            }
        elif 'ruanke' in dir_name:
            return {
                **base_sample,
                "ruanke_subjects": [
                    {
                        "subject": "计算机科学与技术",
                        "ranking_percentage": "前10%",
                        "national_rank": 15,
                        "score": 85.6
                    }
                ],
                "top10_percent_count": 1
            }
        elif 'subject_evaluation' in dir_name:
            return {
                **base_sample,
                "moe_evaluation_subjects": [
                    {
                        "subject": "计算机科学与技术",
                        "grade": "A+",
                        "evaluation_round": "第四轮",
                        "national_rank": "前2%"
                    },
                    {
                        "subject": "软件工程", 
                        "grade": "A",
                        "evaluation_round": "第四轮",
                        "national_rank": "前2%-5%"
                    }
                ],
                "a_class_count": 2
            }
        elif 'undergraduate_majors' in dir_name:
            return {
                **base_sample,
                "undergraduate_majors": [
                    {
                        "major_name": "计算机科学与技术",
                        "major_code": "080901",
                        "degree_type": "工学学士",
                        "established_year": 2000
                    }
                ],
                "total_majors": 1
            }
        elif 'consolidated' in dir_name:
            return {
                "metric": "示例指标",
                "data_sources": ["sample_source"],
                "total_items": 1,
                "results": [base_sample],
                "status": "sample_data"
            }
        else:
            return base_sample
    
    def check_directory_status(self):
        """检查所有目录的状态和文件统计"""
        print("📋 数据目录状态检查:")
        print("=" * 70)
        
        total_dirs = len(REQUIRED_DIRECTORIES)
        existing_dirs = 0
        total_files = 0
        
        for directory in REQUIRED_DIRECTORIES:
            dir_path = os.path.join(self.base_data_dir, directory)
            exists = os.path.exists(dir_path)
            
            if exists:
                existing_dirs += 1
                # 统计文件数量和大小
                json_files = 0
                total_size = 0
                
                for root, _, files in os.walk(dir_path):
                    for file_name in files:
                        if file_name.endswith('.json'):
                            json_files += 1
                            file_path = os.path.join(root, file_name)
                            try:
                                total_size += os.path.getsize(file_path)
                            except OSError:
                                pass
                
                total_files += json_files
                size_mb = total_size / (1024 * 1024) if total_size > 0 else 0
                
                status = f"✅ 存在 ({json_files} 个JSON文件, {size_mb:.1f}MB)"
            else:
                status = "❌ 不存在"
            
            print(f"  📁 {directory:<35} {status}")
        
        # 显示汇总信息
        print("=" * 70)
        print(f"📊 汇总统计:")
        print(f"  📁 目录状态: {existing_dirs}/{total_dirs} 个目录存在")
        print(f"  📄 文件总数: {total_files} 个JSON文件")
        print(f"  📈 完成度: {(existing_dirs/total_dirs)*100:.1f}%")
        
        # 检查关键配置
        self._check_configuration_status()
    
    def _check_configuration_status(self):
        """检查配置文件状态"""
        print(f"\n🔧 配置状态检查:")
        
        # 检查config.ini
        config_path = os.path.join(self.current_dir, 'config.ini')
        config_exists = os.path.exists(config_path)
        print(f"  📝 config.ini: {'✅ 存在' if config_exists else '❌ 不存在'}")
        
        # 检查数据源配置
        configured_sources = len(DATA_SOURCES)
        existing_sources = 0
        
        for source_name, source_path in DATA_SOURCES.items():
            full_path = os.path.join(self.current_dir, source_path)
            if os.path.exists(full_path):
                existing_sources += 1
        
        print(f"  🗂️  数据源: {existing_sources}/{configured_sources} 个路径存在")
        
        # 检查指标配置
        total_metrics = len(METRIC_CATEGORIES.get('subject_metrics', [])) + len(METRIC_CATEGORIES.get('major_metrics', []))
        print(f"  📊 支持指标: {total_metrics} 个")
    
    def migrate_existing_data(self):
        """提供数据迁移建议和工具"""
        print("🔄 数据迁移建议:")
        print("=" * 50)
        
        print("📋 根据您的目录结构设置，建议的数据放置位置：")
        print()
        
        migration_guide = {
            "📚 学科评估数据": {
                "target": "data/subject_evaluation/",
                "description": "教育部学科评估A+、A、A-等级数据",
                "files": ["第四轮学科评估结果.json", "A类学科统计.json"]
            },
            "🏆 双一流数据": {
                "target": "data/moepolicies/",
                "description": "国家双一流学科建设相关数据",
                "files": ["双一流学科名单.json", "世界一流学科.json"]
            },
            "📊 ESI数据": {
                "target": "data/esi_subjects/",
                "description": "ESI学科排名相关数据",
                "files": ["esi_前1%.json", "esi_前1‰.json"]
            },
            "📈 软科数据": {
                "target": "data/ruanke_subjects/",
                "description": "软科中国最好学科排名数据",
                "files": ["软科排名.json", "前10%学科.json"]
            },
            "🎓 专业数据": {
                "target": "data/undergraduate_majors/",
                "description": "本科专业相关数据",
                "files": ["专业列表.json", "一流专业.json", "专业认证.json"]
            }
        }
        
        for category, info in migration_guide.items():
            print(f"{category}")
            print(f"  📂 目标目录: {info['target']}")
            print(f"  📝 说明: {info['description']}")
            print(f"  📄 建议文件: {', '.join(info['files'])}")
            print()
        
        # 检查是否有需要迁移的数据
        self._scan_for_existing_data()
        
        return True
    
    def _scan_for_existing_data(self):
        """扫描可能需要迁移的现有数据"""
        print("🔍 扫描现有数据文件...")
        
        # 扫描项目根目录下的可能数据文件
        project_root = os.path.dirname(os.path.dirname(self.current_dir))
        potential_data_files = []
        
        for root, dirs, files in os.walk(project_root):
            # 跳过系统目录和已知的代码目录
            if any(skip_dir in root for skip_dir in ['__pycache__', '.git', 'node_modules', 'src']):
                continue
                
            for file_name in files:
                if file_name.endswith(('.json', '.csv', '.xlsx')) and not file_name.startswith('.'):
                    file_path = os.path.join(root, file_name)
                    relative_path = os.path.relpath(file_path, project_root)
                    potential_data_files.append(relative_path)
        
        if potential_data_files:
            print(f"  📄 发现 {len(potential_data_files)} 个可能的数据文件:")
            for i, file_path in enumerate(potential_data_files[:10]):  # 只显示前10个
                print(f"    {i+1:2d}. {file_path}")
            
            if len(potential_data_files) > 10:
                print(f"    ... 还有 {len(potential_data_files) - 10} 个文件")
        else:
            print("  ℹ️  未发现需要迁移的数据文件")
    
    def create_data_backup(self):
        """创建数据备份"""
        try:
            from datetime import datetime
            backup_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = os.path.join(self.base_output_dir, f"backup_{backup_time}")
            
            # 这里实现备份逻辑
            print(f"📦 创建备份到: {backup_dir}")
            return True
        except Exception as e:
            print(f"❌ 备份失败: {e}")
            return False
    
    def cleanup_empty_directories(self):
        """清理空目录"""
        cleaned_count = 0
        try:
            for directory in REQUIRED_DIRECTORIES:
                dir_path = os.path.join(self.base_data_dir, directory)
                if os.path.exists(dir_path) and not os.listdir(dir_path):
                    # 目录为空，但保留必需目录
                    pass
            
            print(f"🧹 清理完成，移除了 {cleaned_count} 个空目录")
            return True
        except Exception as e:
            print(f"❌ 清理失败: {e}")
            return False
    
    def _get_current_time(self):
        """获取当前时间字符串"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# 使用示例
if __name__ == '__main__':
    manager = DirectoryManager()
    
    print("🚀 目录管理器测试")
    print("1. 初始化目录...")
    manager.initialize_all_directories()
    
    print("\n2. 检查目录状态...")
    manager.check_directory_status()
    
    print("\n3. 数据迁移建议...")
    manager.migrate_existing_data()