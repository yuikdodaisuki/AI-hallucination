"""AI问答系统配置"""
import os

# LLM配置
LLM_CONFIG = {
    'model_name': 'qwen-turbo-1101',
    'api_key': 'sk-8118a660643e4625805b7e8ca179aa28',  # 添加你的API密钥
    'max_doc_length': 900000,
    'base_url': 'https://dashscope.aliyuncs.com/compatible-mode/v1',
    'timeout': 60,
    'max_retries': 3
}

# 🔥 修正数据源路径 - data目录和AIquest同级 🔥
DATA_SOURCES = {
    # ESI相关数据源
    'esi_subjects': '../data/esi_subjects',
    'esi_top1percent': '../data/esi_subjects/esi_top1percent',
    'esi_top1permille': '../data/esi_subjects/esi_top1permille',
    
    # 双一流学科数据源 - 使用moepolicies存储
    'shuangyiliu_subjects': '../data/moepolicies',
    
    # 软科排名数据源
    'ruanke_subjects': '../data/ruanke_subjects',
    
    # 🔥 学科评估数据源 - 修正路径 🔥
    'subject_evaluation': '../data/subject_evaluation',
    
    # 本科专业相关数据源
    'undergraduate_majors': '../data/undergraduate_majors',
    'total_majors': '../data/undergraduate_majors/total_majors',
    'certified_majors': '../data/undergraduate_majors/certified_majors',
    'national_first_class': '../data/undergraduate_majors/national_first_class',
    'provincial_first_class': '../data/undergraduate_majors/provincial_first_class',
    
    # 教育部政策数据源
    'moepolicies': '../data/moepolicies',
    
    # 整合数据目录
    'consolidated': '../data/consolidated'
}

# 输出配置
OUTPUT_CONFIG = {
    'base_dir': '../../output',
    'consolidated_dir': '../data/consolidated',  # 🔥 修正路径 🔥
    'file_encoding': 'utf-8-sig',
    'json_indent': 2
}

# 🔥 修正教育部评估A类学科数量的数据源映射 🔥
METRIC_DATA_MAPPING = {
    # ESI学科指标 - 使用ESI专门数据源
    'ESI前1%学科数量': [
        'esi_top1percent',           # ESI前1%专门数据
        'esi_subjects',              # ESI通用数据
        'subject_evaluation',        # 备用：学科评估可能包含ESI信息
        'moepolicies'                # 备用：教育部政策数据
    ],
    'ESI前1‰学科数量': [
        'esi_top1permille',          # ESI前1‰专门数据
        'esi_subjects',              # ESI通用数据
        'subject_evaluation',        # 备用：学科评估可能包含ESI信息
        'moepolicies'                # 备用：教育部政策数据
    ],
    
    # 双一流学科指标 - 主要使用moepolicies
    '国家双一流学科数量': [
        'moepolicies',               # 主要：双一流数据在moepolicies中
    ],
    
    # 🔥 教育部评估A类学科指标 - 仅使用subject_evaluation 🔥
    '教育部评估A类学科数量': [
        'subject_evaluation'         # 唯一数据源：学科评估数据
    ],
    
    # 软科排名指标 - 使用软科专门数据源
    '软科中国最好学科排名前10%学科数量': [
        'ruanke_subjects',           # 软科排名专门数据
        'subject_evaluation',        # 备用：学科评估可能包含软科信息
        'moepolicies'                # 备用：教育部数据
    ],
    
    # 本科专业总数 - 使用专业和政策数据
    '本科专业总数': [
        'total_majors',              # 专业总数专门数据
        'undergraduate_majors',      # 本科专业通用数据
        'moepolicies'                # 教育部政策数据（可能包含专业信息）
    ],
    
    # 专业认证 - 使用专业和政策数据
    '本科专业认证通过数': [
        'certified_majors',          # 专业认证专门数据
        'undergraduate_majors',      # 本科专业通用数据
        'moepolicies'                # 教育部政策数据
    ],
    
    # 国家级一流专业 - 使用专业和政策数据
    '国家级一流本科专业建设点': [
        'national_first_class',      # 国家级一流专业专门数据
        'undergraduate_majors',      # 本科专业通用数据
        'moepolicies'                # 教育部政策数据（主要来源）
    ],
    
    # 省级一流专业 - 使用专业和政策数据
    '省级一流本科专业建设点': [
        'provincial_first_class',    # 省级一流专业专门数据
        'undergraduate_majors',      # 本科专业通用数据
        'moepolicies'                # 教育部政策数据
    ]
}

# 🔥 修正数据源优先级配置 🔥
DATA_SOURCE_PRIORITY = {
    'ESI前1%学科数量': ['esi_top1percent', 'esi_subjects', 'subject_evaluation'],
    'ESI前1‰学科数量': ['esi_top1permille', 'esi_subjects', 'subject_evaluation'],
    '国家"双一流"学科数量': ['moepolicies', 'subject_evaluation'],
    '教育部评估A类学科数量': ['subject_evaluation'],  # 🔥 仅使用subject_evaluation 🔥
    '软科"中国最好学科"排名前10%学科数量': ['ruanke_subjects', 'subject_evaluation'],
    '本科专业总数': ['total_majors', 'undergraduate_majors', 'moepolicies'],
    '本科专业认证通过数': ['certified_majors', 'undergraduate_majors', 'moepolicies'],
    '国家级一流本科专业建设点': ['national_first_class', 'moepolicies', 'undergraduate_majors'],
    '省级一流本科专业建设点': ['provincial_first_class', 'moepolicies', 'undergraduate_majors']
}

# 数据源类型配置
DATA_SOURCE_TYPES = {
    # ESI类型数据源
    'esi_sources': ['esi_subjects', 'esi_top1percent', 'esi_top1permille'],
    
    # 学科类型数据源
    'subject_sources': ['esi_subjects', 'ruanke_subjects', 'subject_evaluation', 'moepolicies'],
    
    # 专业类型数据源
    'major_sources': ['undergraduate_majors', 'total_majors', 'certified_majors', 
                     'national_first_class', 'provincial_first_class'],
    
    # 政策类型数据源
    'policy_sources': ['moepolicies']
}

# 问题模板配置
QUESTION_TEMPLATES = {
    'default': "{school_name}的{metric_name}是多少？",
    'count': "统计{school_name}的{metric_name}数量",
    'list': "列出{school_name}的{metric_name}",
    
    # 学科相关指标的特定模板
    'esi_subject': "查找{school_name}进入ESI排名的学科，并统计{metric_name}",
    'double_first_class': "查找{school_name}入选国家双一流计划的学科，统计{metric_name}",
    'subject_ranking': "查找{school_name}在各学科排名中的表现，统计{metric_name}",
    'moe_evaluation': "查找{school_name}在教育部学科评估中获得A类（A+、A、A-）的学科，统计{metric_name}",
    
    # 专业相关指标的特定模板
    'major_count': "统计{school_name}的{metric_name}，包括所有本科专业",
    'major_certification': "查找{school_name}通过专业认证的本科专业，统计{metric_name}",
    'first_class_major': "查找{school_name}的一流本科专业建设点，统计{metric_name}"
}

# 指标分类配置
METRIC_CATEGORIES = {
    'subject_metrics': [
        'ESI前1%学科数量',
        'ESI前1‰学科数量', 
        '国家双一流学科数量',
        '教育部评估A类学科数量',
        '软科"中国最好学科"排名前10%学科数量'
    ],
    'major_metrics': [
        '本科专业总数',
        '本科专业认证通过数',
        '国家级一流本科专业建设点',
        '省级一流本科专业建设点'
    ]
}

# 🔥 添加指标别名配置，便于命令行使用 🔥
METRIC_ALIASES = {
    # ESI学科指标别名
    'esi1%': 'ESI前1%学科数量',
    'esi1‰': 'ESI前1‰学科数量',
    'esi前1%': 'ESI前1%学科数量',
    'esi前1‰': 'ESI前1‰学科数量',
    'esi_1percent': 'ESI前1%学科数量',
    'esi_1permille': 'ESI前1‰学科数量',
    'esi_top1': 'ESI前1%学科数量',
    'esi_top1000': 'ESI前1‰学科数量',
    'esi': 'ESI前1%学科数量',  # 默认指向1%
    
    # 双一流学科别名
    'shuangyiliu': '国家双一流学科数量',
    '双一流': '国家双一流学科数量',
    'double_first': '国家双一流学科数量',
    'world_class': '国家双一流学科数量',
    'first_class_discipline': '国家双一流学科数量',
    'syl': '国家双一流学科数量',
    'worldclass': '国家双一流学科数量',
    
    # 教育部学科评估别名
    'moe_eval': '教育部评估A类学科数量',
    'a_class': '教育部评估A类学科数量',
    '学科评估': '教育部评估A类学科数量',
    '教育部评估': '教育部评估A类学科数量',
    'subject_eval': '教育部评估A类学科数量',
    'moe_assessment': '教育部评估A类学科数量',
    'evaluation': '教育部评估A类学科数量',
    'aclass': '教育部评估A类学科数量',
    
    # 软科排名别名
    'ruanke': '软科中国最好学科排名前10%学科数量',
    'shanghairanking': '软科中国最好学科排名前10%学科数量',
    '软科前10%': '软科中国最好学科排名前10%学科数量',
    'best_subjects': '软科中国最好学科排名前10%学科数量',
    'shanghai_ranking': '软科中国最好学科排名前10%学科数量',
    'ranking': '软科中国最好学科排名前10%学科数量',
    'top10': '软科中国最好学科排名前10%学科数量',
    
    # 本科专业总数别名
    'majors_total': '本科专业总数',
    '专业总数': '本科专业总数',
    'total_majors': '本科专业总数',
    'undergraduate_total': '本科专业总数',
    'majors': '本科专业总数',
    'total': '本科专业总数',
    'major_count': '本科专业总数',
    
    # 专业认证别名
    'majors_certified': '本科专业认证通过数',
    '专业认证': '本科专业认证通过数',
    'certified': '本科专业认证通过数',
    'certification': '本科专业认证通过数',
    'accreditation': '本科专业认证通过数',
    'certified_majors': '本科专业认证通过数',
    'accredited': '本科专业认证通过数',
    
    # 国家级一流专业别名
    'national_majors': '国家级一流本科专业建设点',
    '国家一流专业': '国家级一流本科专业建设点',
    'national_first_class': '国家级一流本科专业建设点',
    'national_excellence': '国家级一流本科专业建设点',
    'national': '国家级一流本科专业建设点',
    'guojia': '国家级一流本科专业建设点',
    'first_class_national': '国家级一流本科专业建设点',
    
    # 省级一流专业别名
    'provincial_majors': '省级一流本科专业建设点',
    '省级一流专业': '省级一流本科专业建设点',
    'provincial_first_class': '省级一流本科专业建设点',
    'provincial': '省级一流本科专业建设点',
    'sheng': '省级一流本科专业建设点',
    'provincial_excellence': '省级一流本科专业建设点',
    'first_class_provincial': '省级一流本科专业建设点',
    
    # 数字别名（便于快速选择）
    '1': 'ESI前1%学科数量',
    '2': 'ESI前1‰学科数量',
    '3': '国家双一流学科数量',
    '4': '教育部评估A类学科数量',
    '5': '软科中国最好学科排名前10%学科数量',
    '6': '本科专业总数',
    '7': '本科专业认证通过数',
    '8': '国家级一流本科专业建设点',
    '9': '省级一流本科专业建设点',
}

# 获取所有可用指标（包括别名）
def get_available_metrics():
    """获取所有可用指标，包括别名"""
    all_metrics = METRIC_CATEGORIES['subject_metrics'] + METRIC_CATEGORIES['major_metrics']
    return {
        'all_metrics': all_metrics,
        'subject_metrics': METRIC_CATEGORIES['subject_metrics'],
        'major_metrics': METRIC_CATEGORIES['major_metrics'],
        'aliases': METRIC_ALIASES
    }

def resolve_metric_name(input_name):
    """解析指标名称，支持别名和模糊匹配"""
    # 直接匹配
    all_metrics = METRIC_CATEGORIES['subject_metrics'] + METRIC_CATEGORIES['major_metrics']
    if input_name in all_metrics:
        return input_name
    
    # 别名匹配（精确匹配）
    if input_name in METRIC_ALIASES:
        return METRIC_ALIASES[input_name]
    
    # 别名匹配（不区分大小写）
    for alias, real_name in METRIC_ALIASES.items():
        if input_name.lower() == alias.lower():
            return real_name
    
    # 部分匹配（在真实指标名中查找）
    for metric in all_metrics:
        # 移除标点符号进行模糊匹配
        clean_metric = metric.replace('"', '').replace('""', '').replace('（', '').replace('）', '')
        clean_input = input_name.replace('"', '').replace('""', '').replace('（', '').replace('）', '')
        
        if clean_input in clean_metric or clean_metric in clean_input:
            return metric
    
    return None

def get_metric_suggestions(input_name):
    """获取指标建议（当输入不匹配时）"""
    suggestions = []
    all_metrics = METRIC_CATEGORIES['subject_metrics'] + METRIC_CATEGORIES['major_metrics']
    
    # 基于关键词匹配
    input_lower = input_name.lower()
    
    # 检查别名
    for alias, real_name in METRIC_ALIASES.items():
        if input_lower in alias.lower() or alias.lower() in input_lower:
            if real_name not in suggestions:
                suggestions.append(f"{alias} → {real_name}")
    
    # 检查指标名
    for metric in all_metrics:
        metric_lower = metric.lower()
        if input_lower in metric_lower or any(word in metric_lower for word in input_lower.split()):
            if metric not in [s.split(' → ')[-1] for s in suggestions]:
                suggestions.append(metric)
    
    return suggestions

# 指标关键词配置
METRIC_KEYWORDS = {
    'ESI前1%学科数量': ['ESI', '前1%', '学科', 'Essential Science Indicators'],
    'ESI前1‰学科数量': ['ESI', '前1‰', '学科', 'Essential Science Indicators'],
    '国家双一流学科数量': ['双一流', '世界一流学科', '国家', '学科建设'],
    '教育部评估A类学科数量': ['教育部', '学科评估', 'A类', 'A+', 'A', 'A-', '第四轮', '第五轮'],
    '软科中国最好学科排名前10%学科数量': ['软科', '中国最好学科', '前10%', '排名'],
    '本科专业总数': ['本科专业', '专业总数', '专业数量'],
    '本科专业认证通过数': ['专业认证', '认证通过', '工程教育认证', '师范类专业认证'],
    '国家级一流本科专业建设点': ['国家级', '一流本科专业', '专业建设点'],
    '省级一流本科专业建设点': ['省级', '一流本科专业', '专业建设点', '省一流']
}

# 🔥 修正必需目录配置 - 相对于src/data 🔥
REQUIRED_DIRECTORIES = [
    'esi_subjects',
    'esi_subjects/esi_top1percent',
    'esi_subjects/esi_top1permille',
    'ruanke_subjects',
    'subject_evaluation',  # 学科评估数据目录
    'undergraduate_majors',
    'undergraduate_majors/total_majors',
    'undergraduate_majors/certified_majors',
    'undergraduate_majors/national_first_class',
    'undergraduate_majors/provincial_first_class',
    'consolidated'
    # 注意：moepolicies已存在，不需要创建
]



# 调试配置
DEBUG_CONFIG = {
    'save_debug_files': True,
    'debug_dir': '../../debug',
    'log_level': 'INFO'
}