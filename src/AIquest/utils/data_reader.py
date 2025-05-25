"""数据读取和整合功能"""
import os
import json
from src.AIquest.config import DATA_SOURCES, OUTPUT_CONFIG, DATA_SOURCE_PRIORITY, REQUIRED_DIRECTORIES


class DataReader:
    """数据读取和整合功能"""
    
    def __init__(self):
        # 🔥 修正路径计算 - data目录和AIquest同级 🔥
        self.current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # src/AIquest
        self.src_dir = os.path.dirname(self.current_dir)  # src
        self.data_dir = os.path.join(self.src_dir, 'data')  # src/data
        self._ensure_directories_exist()
        
        print(f"📁 DataReader路径信息:")
        print(f"  AIquest目录: {self.current_dir}")
        print(f"  src目录: {self.src_dir}")
        print(f"  data目录: {self.data_dir}")
    
    def _ensure_directories_exist(self):
        """确保所有必需的目录存在（跳过已存在的moepolicies）"""
        for directory in REQUIRED_DIRECTORIES:
            dir_path = os.path.join(self.data_dir, directory)
            if not os.path.exists(dir_path):
                try:
                    os.makedirs(dir_path, exist_ok=True)
                    print(f"  📁 创建目录: {dir_path}")
                    
                    # 为新创建的目录添加README文件
                    readme_path = os.path.join(dir_path, 'README.md')
                    readme_content = self._generate_readme_content(directory)
                    with open(readme_path, 'w', encoding='utf-8') as f:
                        f.write(readme_content)
                        
                except Exception as e:
                    print(f"  ❌ 创建目录失败 {dir_path}: {e}")
    
    def _generate_readme_content(self, dir_name):
        """生成目录说明文档"""
        descriptions = {
            'esi_subjects': 'ESI学科相关数据，包含进入ESI排名的学科信息',
            'esi_subjects/esi_top1percent': 'ESI前1%学科专门数据',
            'esi_subjects/esi_top1permille': 'ESI前1‰学科专门数据',
            'ruanke_subjects': '软科中国最好学科排名相关数据',
            'subject_evaluation': '教育部学科评估相关数据，包含A+、A、A-等评级信息',
            'undergraduate_majors': '本科专业相关数据',
            'undergraduate_majors/total_majors': '本科专业总数统计数据',
            'undergraduate_majors/certified_majors': '通过专业认证的本科专业数据',
            'undergraduate_majors/national_first_class': '国家级一流本科专业建设点数据',
            'undergraduate_majors/provincial_first_class': '省级一流本科专业建设点数据',
            'consolidated': '整合后的数据文件'
        }
        
        description = descriptions.get(dir_name, '数据存储目录')
        
        return f"""# {dir_name} 数据目录

## 目录说明
{description}

## 数据格式要求
- 文件格式：JSON
- 编码：UTF-8
- 文件命名：建议使用有意义的名称，如 `university_name.json`

## 使用说明
1. 将相关数据文件放置在此目录中
2. 系统会自动扫描并读取所有 `.json` 文件
3. 数据会被自动整合到问答系统中

## 更新时间
{self._get_current_time()}
"""
    
    def _get_current_time(self):
        """获取当前时间字符串"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def read_data_from_source(self, source_name):
        """从指定数据源读取数据"""
        if source_name not in DATA_SOURCES:
            print(f"警告: 未知的数据源: {source_name}")
            return []
        
        # 🔥 修正路径计算 - 基于src/data目录 🔥
        source_relative_path = DATA_SOURCES[source_name]
        
        # 移除路径前缀并计算正确路径
        if source_relative_path.startswith('../data/'):
            clean_path = source_relative_path.replace('../data/', '')
        else:
            clean_path = source_relative_path
        
        source_path = os.path.join(self.data_dir, clean_path)
        print(f"    正在读取数据源: {source_path}")
        
        all_data = []
        
        if not os.path.exists(source_path):
            print(f"    警告: 数据源路径不存在: {source_path}")
            # 🔥 添加调试信息 🔥
            print(f"    调试信息:")
            print(f"      配置的源路径: {source_relative_path}")
            print(f"      清理后的路径: {clean_path}")
            print(f"      data目录: {self.data_dir}")
            print(f"      最终路径: {source_path}")
            print(f"      目录是否存在: {os.path.exists(source_path)}")
            
            # 🔥 列出data目录内容 🔥
            if os.path.exists(self.data_dir):
                print(f"    data目录内容:")
                for item in os.listdir(self.data_dir):
                    item_path = os.path.join(self.data_dir, item)
                    if os.path.isdir(item_path):
                        print(f"      📁 {item}/")
                        # 如果是subject_evaluation目录，列出其内容
                        if item == 'subject_evaluation':
                            try:
                                sub_items = os.listdir(item_path)
                                json_files = [f for f in sub_items if f.endswith('.json')]
                                print(f"        📄 JSON文件: {len(json_files)} 个")
                                for json_file in json_files[:3]:
                                    print(f"          - {json_file}")
                            except Exception as e:
                                print(f"        ❌ 无法读取目录内容: {e}")
                    else:
                        print(f"      📄 {item}")
            else:
                print(f"    ❌ data目录不存在: {self.data_dir}")
            
            return all_data
        
        # 递归读取所有JSON文件
        file_count = 0
        for root, _, files in os.walk(source_path):
            for file_name in files:
                if file_name.endswith('.json') and not file_name.startswith('combined_'):
                    file_path = os.path.join(root, file_name)
                    print(f"      读取文件: {file_path}")
                    data = self._read_json_file(file_path)
                    if data:
                        normalized_data = self._normalize_json_data(data, file_path)
                        all_data.extend(normalized_data)
                        file_count += 1
        
        print(f"    从 {source_path} 读取到 {len(all_data)} 条数据，处理了 {file_count} 个JSON文件")
        return all_data
    
    def _read_json_file(self, file_path):
        """读取单个JSON文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print(f"      警告: {file_path} 不是有效的JSON文件: {e}")
            return None
        except Exception as e:
            print(f"      错误: 读取 {file_path} 失败: {e}")
            return None
    
    def _normalize_json_data(self, data, file_path):
        """标准化JSON数据格式"""
        if isinstance(data, list):
            return [{**item, "__file_source": file_path} if isinstance(item, dict) 
                   else {"__file_source": file_path, "value": item} for item in data]
        elif isinstance(data, dict):
            return [{**data, "__file_source": file_path}]
        else:
            return [{"__file_source": file_path, "value": data}]
    
    def consolidate_data_for_metric(self, metric_name, data_sources=None):
        """为特定指标整合数据，支持优先级"""
        # 如果没有指定数据源，使用配置中的优先级列表
        if data_sources is None:
            data_sources = DATA_SOURCE_PRIORITY.get(metric_name, [])
        
        print(f"  正在为指标 '{metric_name}' 整合数据源: {data_sources}")
        
        # 🔥 修正consolidated目录路径 🔥
        consolidated_dir = os.path.join(self.data_dir, 'consolidated')
        os.makedirs(consolidated_dir, exist_ok=True)
        
        metric_data_file = os.path.join(consolidated_dir, f"{metric_name}_data.json")
        
        # 按优先级收集数据
        all_metric_data = []
        successful_sources = []
        
        for data_source in data_sources:
            source_data = self.read_data_from_source(data_source)
            if source_data:
                all_metric_data.extend(source_data)
                successful_sources.append(data_source)
                print(f"    ✅ 成功从 {data_source} 获取 {len(source_data)} 条数据")
            else:
                print(f"    ⚠️  数据源 {data_source} 暂无数据")
        
        if not all_metric_data:
            print(f"  警告: 未能从任何数据源 {data_sources} 中读取到数据")
            # 创建空的数据文件，避免后续处理失败
            empty_data = {
                "metric": metric_name,
                "data_sources": data_sources,
                "successful_sources": successful_sources,
                "total_items": 0,
                "results": [],
                "status": "no_data_found"
            }
            try:
                with open(metric_data_file, 'w', encoding='utf-8') as f:
                    json.dump(empty_data, f, ensure_ascii=False, indent=OUTPUT_CONFIG['json_indent'])
                return metric_data_file
            except Exception as e:
                print(f"  保存空数据文件失败: {e}")
                return None
        
        # 保存整合后的数据
        consolidated_data = {
            "metric": metric_name,
            "data_sources": data_sources,
            "successful_sources": successful_sources,
            "total_items": len(all_metric_data),
            "results": all_metric_data,
            "status": "success"
        }
        
        try:
            with open(metric_data_file, 'w', encoding='utf-8') as f:
                json.dump(consolidated_data, f, ensure_ascii=False, indent=OUTPUT_CONFIG['json_indent'])
            print(f"  成功整合数据到: {metric_data_file}")
            return metric_data_file
        except Exception as e:
            print(f"  保存整合数据失败: {e}")
            return None
    
    def extract_text_content(self, data_file_path):
        """从JSON文件中提取文本内容供LLM使用"""
        try:
            with open(data_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            text_list = []
            
            def extract_strings(value):
                if isinstance(value, str):
                    text_list.append(value)
                elif isinstance(value, list):
                    for item in value:
                        extract_strings(item)
                elif isinstance(value, dict):
                    for v in value.values():
                        extract_strings(v)
            
            if 'results' in data:
                extract_strings(data['results'])
            else:
                extract_strings(data)
            
            return "\n".join(text_list)
            
        except Exception as e:
            print(f"提取文本内容失败: {e}")
            return ""
    
    def get_data_source_info(self):
        """获取数据源信息和状态"""
        info = {
            'configured_sources': len(DATA_SOURCES),
            'existing_sources': 0,
            'missing_sources': [],
            'source_details': {}
        }
        
        for source_name, source_path in DATA_SOURCES.items():
            # 🔥 修正路径计算 🔥
            if source_path.startswith('../data/'):
                clean_path = source_path.replace('../data/', '')
            else:
                clean_path = source_path
            
            full_path = os.path.join(self.data_dir, clean_path)
            exists = os.path.exists(full_path)
            
            if exists:
                info['existing_sources'] += 1
                # 统计该数据源中的文件数量
                file_count = 0
                if os.path.isdir(full_path):
                    for root, _, files in os.walk(full_path):
                        file_count += len([f for f in files if f.endswith('.json')])
                
                info['source_details'][source_name] = {
                    'path': full_path,
                    'exists': True,
                    'file_count': file_count
                }
            else:
                info['missing_sources'].append(source_name)
                info['source_details'][source_name] = {
                    'path': full_path,
                    'exists': False,
                    'file_count': 0
                }
        
        return info