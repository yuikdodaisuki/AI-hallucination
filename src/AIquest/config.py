"""AI问答系统配置"""
import os

# LLM配置
LLM_CONFIG = {
    'model_name': 'qwen-plus-latest',
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
    
    # 双一流学科数据源 - 使用moepolicies存储
    'shuangyiliu_subjects': '../data/moepolicies',
    
    # 软科排名数据源
    'ruanke_subjects': '../data/ruanke_subjects',
    
    # 🔥 学科评估数据源 - 修正路径 🔥
    'subject_evaluation': '../data/subject_evaluation',
    
    # 学校数据 本科专业相关数据源
    'total_majors': '../data/school_data',
    'national_first_class': '../data/school_data',
    'provincial_first_class': '../data/school_data',

    # 🔥 新增学位点数据源 🔥
    'degree_programs': '../data/degree_programs',
    
    # 🔥 新增教学相关数据源 🔥
    'national_teaching_awards': '../data/teaching_achievements/national_awards',
    'provincial_teaching_awards': '../data/teaching_achievements/provincial_awards',
    'youth_teaching_competition': '../data/teaching_achievements/youth_competition',
    'national_courses': '../data/teaching_achievements/national_courses',
    'provincial_courses': '../data/teaching_achievements/provincial_courses',
    'national_smart_platform': '../data/teaching_achievements/national_smart_platform',
    'provincial_smart_platform': '../data/teaching_achievements/provincial_smart_platform',
    
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
        'esi_subjects',              # ESI通用数据
    ],
    'ESI前1‰学科数量': [
        'esi_subjects',              # ESI通用数据
    ],
    
    # 双一流学科指标 - 主要使用moepolicies
    '国家双一流学科数量': [
        'shuangyiliu_subjects',               
    ],
    
    # 🔥 教育部评估A类学科指标 - 仅使用subject_evaluation 🔥
    '教育部评估A类学科数量': [
        'subject_evaluation'         # 唯一数据源：学科评估数据
    ],
    
    # 软科排名指标 - 使用软科专门数据源
    '软科中国最好学科排名前10%学科数量': [
        'ruanke_subjects',           # 软科排名专门数据
    ],
    
    # 本科专业总数 - 使用专业和政策数据
    '本科专业总数': [
        'total_majors',              # 专业总数专门数据
    ],
    
    
    # 国家级一流专业 - 使用专业和政策数据
    '国家级一流本科专业建设点': [
        'national_first_class',      # 国家级一流专业专门数据
    ],
    
    # 省级一流专业 - 使用专业和政策数据
    '省级一流本科专业建设点': [
        'provincial_first_class',    # 省级一流专业专门数据
    ],

    # 🔥 新增学位点指标的数据源映射 🔥
    '学术型硕士学位点': [
        'degree_programs',           # 学位点专门数据
    ],
    
    '专业型硕士学位点': [
        'degree_programs',           # 学位点专门数据
    ],
    
    '学术型博士学位点': [
        'degree_programs',           # 学位点专门数据
    ],
    
    '专业型博士学位点': [
        'degree_programs',           # 学位点专门数据
    ],
    
    # 🔥 新增教学相关指标的数据源映射 🔥
    '国家级教学成果奖': [
        'national_teaching_awards',  # 国家级教学成果奖专门数据
    ],
    
    '省级教学成果奖': [
        'provincial_teaching_awards', # 省级教学成果奖专门数据
    ],
    
    '全国高校青年教师教学竞赛': [
        'youth_teaching_competition', # 青年教师教学竞赛专门数据
    ],
    
    '国家级一流本科课程': [
        'national_courses',          # 国家级一流课程专门数据
    ],
    
    '省级一流本科课程': [
        'provincial_courses',        # 省级一流课程专门数据
    ],
    
    '国家级高等教育智慧平台课程': [
        'national_smart_platform',   # 国家级智慧平台课程专门数据
    ],
    
    '省级高等教育智慧平台课程': [
        'provincial_smart_platform', # 省级智慧平台课程专门数据
    ]
}

# 数据源类型配置
DATA_SOURCE_TYPES = {
    # ESI类型数据源
    'esi_sources': ['esi_subjects'],
    
    # 学科类型数据源
    'subject_sources': ['esi_subjects', 'ruanke_subjects', 'subject_evaluation', 'shuangyiliu_subjects'],
    
    # 专业类型数据源
    'major_sources': ['total_majors', 
                     'national_first_class', 'provincial_first_class', 'degree_programs'],
    
    # 🔥 新增教学类型数据源 🔥
    'teaching_sources': ['teaching_achievements', 'national_teaching_awards', 'provincial_teaching_awards',
                         'youth_teaching_competition', 'national_courses', 'provincial_courses',
                         'national_smart_platform', 'provincial_smart_platform'],
    
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
    'first_class_major': "查找{school_name}的一流本科专业建设点，统计{metric_name}",

    # 🔥 新增学位点相关指标的特定模板 🔥
    'degree_program': "查找{school_name}获得授权的学位点，统计{metric_name}",
    'master_degree': "查找{school_name}的硕士学位授权点，统计{metric_name}",
    'doctoral_degree': "查找{school_name}的博士学位授权点，统计{metric_name}",
    'academic_degree': "查找{school_name}的学术型学位授权点，统计{metric_name}",
    'professional_degree': "查找{school_name}的专业型学位授权点，统计{metric_name}",
    
    # 🔥 新增教学相关指标的特定模板 🔥
    'teaching_awards': "查找{school_name}获得的教学成果奖，统计{metric_name}",
    'teaching_competition': "查找{school_name}在全国高校青年教师教学竞赛中的获奖情况，统计{metric_name}",
    'first_class_course': "查找{school_name}的一流本科课程，统计{metric_name}",
    'smart_platform_course': "查找{school_name}在高等教育智慧平台的课程，统计{metric_name}"
}

# 指标分类配置
METRIC_CATEGORIES = {
    'subject_metrics': [
        'ESI前1%学科数量',
        'ESI前1‰学科数量', 
        '国家双一流学科数量',
        '教育部评估A类学科数量',
        '软科中国最好学科排名前10%学科数量'
    ],
    'major_metrics': [
        '本科专业总数',
        '国家级一流本科专业建设点',
        '省级一流本科专业建设点',
        '学术型硕士学位点',
        '专业型硕士学位点',
        '学术型博士学位点',
        '专业型博士学位点'
    ],
    # 🔥 新增教学相关指标分类 🔥
    'teaching_metrics': [
        '国家级教学成果奖',
        '省级教学成果奖',
        '全国高校青年教师教学竞赛',
        '国家级一流本科课程',
        '省级一流本科课程',
        '国家级高等教育智慧平台课程',
        '省级高等教育智慧平台课程'
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

    # 🔥 新增学位点指标别名 🔥
    # 学术型硕士学位点别名
    'academic_master': '学术型硕士学位点',
    '学硕': '学术型硕士学位点',
    'xueshuo': '学术型硕士学位点',
    'academic_master_degree': '学术型硕士学位点',
    'master_academic': '学术型硕士学位点',
    'xueshuxing_shuoshi': '学术型硕士学位点',
    
    # 专业型硕士学位点别名
    'professional_master': '专业型硕士学位点',
    '专硕': '专业型硕士学位点',
    'zhuanshuo': '专业型硕士学位点',
    'professional_master_degree': '专业型硕士学位点',
    'master_professional': '专业型硕士学位点',
    'zhuanyexing_shuoshi': '专业型硕士学位点',
    'mba': '专业型硕士学位点',  # MBA是专业型硕士的典型代表
    'mpa': '专业型硕士学位点',  # MPA也是专业型硕士
    
    # 学术型博士学位点别名
    'academic_doctoral': '学术型博士学位点',
    'academic_phd': '学术型博士学位点',
    '学博': '学术型博士学位点',
    'xuebo': '学术型博士学位点',
    'academic_doctor_degree': '学术型博士学位点',
    'doctoral_academic': '学术型博士学位点',
    'xueshuxing_boshi': '学术型博士学位点',
    
    # 专业型博士学位点别名
    'professional_doctoral': '专业型博士学位点',
    'professional_phd': '专业型博士学位点',
    '专博': '专业型博士学位点',
    'zhuanbo': '专业型博士学位点',
    'professional_doctor_degree': '专业型博士学位点',
    'doctoral_professional': '专业型博士学位点',
    'zhuanyexing_boshi': '专业型博士学位点',

    
    # 🔥 新增教学相关指标别名 🔥
    # 国家级教学成果奖别名
    'national_teaching_award': '国家级教学成果奖',
    '国家教学成果奖': '国家级教学成果奖',
    'national_award': '国家级教学成果奖',
    'teaching_award_national': '国家级教学成果奖',
    'guojia_jiaoxue': '国家级教学成果奖',
    
    # 省级教学成果奖别名
    'provincial_teaching_award': '省级教学成果奖',
    '省教学成果奖': '省级教学成果奖',
    'provincial_award': '省级教学成果奖',
    'teaching_award_provincial': '省级教学成果奖',
    'sheng_jiaoxue': '省级教学成果奖',
    
    # 全国高校青年教师教学竞赛别名
    'youth_teaching_competition': '全国高校青年教师教学竞赛',
    '青年教师竞赛': '全国高校青年教师教学竞赛',
    'youth_competition': '全国高校青年教师教学竞赛',
    'teaching_competition': '全国高校青年教师教学竞赛',
    'qingnian_jingsai': '全国高校青年教师教学竞赛',
    
    # 国家级一流本科课程别名
    'national_course': '国家级一流本科课程',
    '国家一流课程': '国家级一流本科课程',
    'national_first_class_course': '国家级一流本科课程',
    'guojia_kecheng': '国家级一流本科课程',
    'first_class_course_national': '国家级一流本科课程',
    
    # 省级一流本科课程别名
    'provincial_course': '省级一流本科课程',
    '省一流课程': '省级一流本科课程',
    'provincial_first_class_course': '省级一流本科课程',
    'sheng_kecheng': '省级一流本科课程',
    'first_class_course_provincial': '省级一流本科课程',
    
    # 国家级高等教育智慧平台课程别名
    'national_smart_course': '国家级高等教育智慧平台课程',
    '国家智慧平台': '国家级高等教育智慧平台课程',
    'smart_platform_national': '国家级高等教育智慧平台课程',
    'national_smart_platform': '国家级高等教育智慧平台课程',
    'zhihui_pingtai_guojia': '国家级高等教育智慧平台课程',
    
    # 省级高等教育智慧平台课程别名
    'provincial_smart_course': '省级高等教育智慧平台课程',
    '省智慧平台': '省级高等教育智慧平台课程',
    'smart_platform_provincial': '省级高等教育智慧平台课程',
    'provincial_smart_platform': '省级高等教育智慧平台课程',
    'zhihui_pingtai_sheng': '省级高等教育智慧平台课程',
    
    # 🔥 更新数字别名（便于快速选择）🔥
    '1': 'ESI前1%学科数量',
    '2': 'ESI前1‰学科数量',
    '3': '国家双一流学科数量',
    '4': '教育部评估A类学科数量',
    '5': '软科中国最好学科排名前10%学科数量',
    '6': '本科专业总数',
    '7': '国家级一流本科专业建设点',
    '8': '省级一流本科专业建设点',
    '9': '国家级教学成果奖',
    '10': '省级教学成果奖',
    '11': '全国高校青年教师教学竞赛',
    '12': '国家级一流本科课程',
    '13': '省级一流本科课程',
    '14': '国家级高等教育智慧平台课程',
    '15': '省级高等教育智慧平台课程',
    '16': '学术型硕士学位点',
    '17': '专业型硕士学位点',
    '18': '学术型博士学位点',
    '19': '专业型博士学位点',
}

# 获取所有可用指标（包括别名）
def get_available_metrics():
    """获取所有可用指标，包括别名"""
    all_metrics = (METRIC_CATEGORIES['subject_metrics'] + 
                  METRIC_CATEGORIES['major_metrics'] + 
                  METRIC_CATEGORIES['teaching_metrics'])
    return {
        'all_metrics': all_metrics,
        'subject_metrics': METRIC_CATEGORIES['subject_metrics'],
        'major_metrics': METRIC_CATEGORIES['major_metrics'],
        'teaching_metrics': METRIC_CATEGORIES['teaching_metrics'],
        'aliases': METRIC_ALIASES
    }

def resolve_metric_name(input_name):
    """解析指标名称，支持别名和模糊匹配"""
    # 直接匹配
    all_metrics = (METRIC_CATEGORIES['subject_metrics'] + 
                  METRIC_CATEGORIES['major_metrics'] + 
                  METRIC_CATEGORIES['teaching_metrics'])
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
    all_metrics = (METRIC_CATEGORIES['subject_metrics'] + 
                  METRIC_CATEGORIES['major_metrics'] + 
                  METRIC_CATEGORIES['teaching_metrics'])
    
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
    '国家级一流本科专业建设点': ['国家级', '一流本科专业', '专业建设点'],
    '省级一流本科专业建设点': ['省级', '一流本科专业', '专业建设点', '省一流'],

    # 🔥 新增学位点相关指标关键词 🔥
    '学术型硕士学位点': ['学术型', '硕士学位点', '学硕', '硕士学位授权点', '学术硕士'],
    '专业型硕士学位点': ['专业型', '硕士学位点', '专硕', '专业硕士', 'MBA', 'MPA', 'MPAcc'],
    '学术型博士学位点': ['学术型', '博士学位点', '学博', '博士学位授权点', '学术博士'],
    '专业型博士学位点': ['专业型', '博士学位点', '专博', '专业博士', 'DBA', 'Ed.D'],
    
    # 🔥 新增教学相关指标关键词 🔥
    '国家级教学成果奖': ['国家级', '教学成果奖', '教学成果', '国家奖'],
    '省级教学成果奖': ['省级', '教学成果奖', '教学成果', '省奖'],
    '全国高校青年教师教学竞赛': ['青年教师', '教学竞赛', '青教赛', '全国竞赛'],
    '国家级一流本科课程': ['国家级', '一流课程', '本科课程', '金课'],
    '省级一流本科课程': ['省级', '一流课程', '本科课程', '省级金课'],
    '国家级高等教育智慧平台课程': ['国家级', '智慧平台', '在线课程', '慕课'],
    '省级高等教育智慧平台课程': ['省级', '智慧平台', '在线课程', '省级慕课']
}

# 🔥 修正必需目录配置 - 相对于src/data 🔥
REQUIRED_DIRECTORIES = [
    'esi_subjects',
    'ruanke_subjects',
    'subject_evaluation',  # 学科评估数据目录
    'school_data',  # 包含本科专业数据
    'degree_programs',  #  新增学位点数据目录 
    # 🔥 新增教学相关目录 🔥
    'teaching_achievements',
    'teaching_achievements/national_awards',
    'teaching_achievements/provincial_awards',
    'teaching_achievements/youth_competition',
    'teaching_achievements/national_courses',
    'teaching_achievements/provincial_courses',
    'teaching_achievements/national_smart_platform',
    'teaching_achievements/provincial_smart_platform',
    'consolidated'
    'consolidated_intelligent',  # 智能截取模式目录
    # 注意：moepolicies已存在，不需要创建
]



# 🔥 新增：附件内容处理配置 🔥
ATTACHMENT_PROCESSING_CONFIG = {
    # 是否启用基于学校名称的智能截取
    'enable_school_based_extraction': True,  # 默认启用
    
    # 智能截取配置
    'school_extraction_config': {
        'characters_after_school': 100,  # 学校名称后读取的字符数
        'characters_before_school': 0,   # 学校名称前读取的字符数（当前为0，即只往后读取）
        'max_segments_per_school': 10,   # 每个学校最多提取的片段数
        'min_segment_length': 10,        # 片段最小长度
        'school_list_source': 'csv',     # 学校列表来源：'csv'、'predefined'、'auto'
    },
    
    # 传统附件处理配置
    'traditional_extraction_config': {
        'max_content_length': 1000000,     # 传统模式下的最大内容长度
        'clean_html_tags': False,         # 是否清理HTML标签
        'remove_extra_whitespace': False, # 是否移除多余空白
    },
    
    # 通用配置
    'supported_formats': ['.pdf', '.docx', '.doc', '.txt'],  # 支持的附件格式
    'max_attachment_size': 50 * 1024 * 1024,  # 最大附件大小（50MB）
    'enable_attachment_processing': True,       # 是否启用附件处理
}

# 🔥 在现有配置末尾添加获取附件配置的函数 🔥
def get_attachment_config():
    """获取附件处理配置"""
    return ATTACHMENT_PROCESSING_CONFIG

def is_school_extraction_enabled():
    """检查是否启用学校名称智能截取"""
    return ATTACHMENT_PROCESSING_CONFIG.get('enable_school_based_extraction', False)

def get_school_extraction_config():
    """获取学校名称智能截取配置"""
    return ATTACHMENT_PROCESSING_CONFIG.get('school_extraction_config', {})

def get_traditional_extraction_config():
    """获取传统附件处理配置"""
    return ATTACHMENT_PROCESSING_CONFIG.get('traditional_extraction_config', {})

def get_consolidated_dir_name():
    """根据智能截取模式获取整合数据目录名称"""
    if is_school_extraction_enabled():
        return 'consolidated_intelligent'  # 智能模式目录
    else:
        return 'consolidated'              # 传统模式目录

def get_consolidated_dir_path(base_data_dir):
    """获取完整的整合数据目录路径"""
    dir_name = get_consolidated_dir_name()
    return os.path.join(base_data_dir, dir_name)


# 🔥 更新 OUTPUT_CONFIG，使其动态获取目录 🔥
def get_output_config(base_data_dir):
    """获取动态的输出配置"""
    return {
        'base_dir': '../../output',
        'consolidated_dir': get_consolidated_dir_path(base_data_dir),
        'file_encoding': 'utf-8-sig',
        'json_indent': 2
    }

def enable_school_extraction(enable=True):
    """启用或禁用学校名称智能截取"""
    ATTACHMENT_PROCESSING_CONFIG['enable_school_based_extraction'] = enable
    print(f"📍 学校名称智能截取已{'启用' if enable else '禁用'}")

def set_extraction_length(chars_after=100, chars_before=0):
    """设置截取长度"""
    ATTACHMENT_PROCESSING_CONFIG['school_extraction_config']['characters_after_school'] = chars_after
    ATTACHMENT_PROCESSING_CONFIG['school_extraction_config']['characters_before_school'] = chars_before
    print(f"✂️  截取长度设置：前{chars_before}字符，后{chars_after}字符")

def set_traditional_mode_length(max_length=10000):
    """设置传统模式的最大内容长度"""
    ATTACHMENT_PROCESSING_CONFIG['traditional_extraction_config']['max_content_length'] = max_length
    print(f"📄 传统模式最大长度设置为：{max_length}字符")

def print_attachment_config():
    """打印当前附件处理配置"""
    config = ATTACHMENT_PROCESSING_CONFIG
    print("📋 当前附件处理配置:")
    print(f"  📍 智能截取模式: {'启用' if config['enable_school_based_extraction'] else '禁用'}")
    print(f"  ✂️  截取长度: 前{config['school_extraction_config']['characters_before_school']}字符，后{config['school_extraction_config']['characters_after_school']}字符")
    print(f"  📄 传统模式长度限制: {config['traditional_extraction_config']['max_content_length']}字符")
    print(f"  📎 支持的文件格式: {', '.join(config['supported_formats'])}")
    print(f"  🔧 附件处理: {'启用' if config['enable_attachment_processing'] else '禁用'}")

# 调试配置
DEBUG_CONFIG = {
    'save_debug_files': True,
    'debug_dir': '../../debug',
    'log_level': 'INFO'
}