"""
教育数据搜索配置模块
- 提供各类教育指标的搜索配置
- 支持多源权威搜索策略
- 包含学校别名映射和官网信息
"""
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime
import pandas as pd

# =============================================================================
# 🔥 数据源配置 🔥
# =============================================================================

# 权威数据源配置
AUTHORITATIVE_DATA_SOURCES = {
    'esi_subjects': [
        'clarivate.com',     # 科睿唯安ESI官网
        'webofscience.com',  # Web of Science
        'esi.qa.com.cn',     # ESI中国官网
        'moe.gov.cn',        # 教育部官网
        'cuaa.net'           # 中国校友会网
    ],
    'teaching_awards': [
        'moe.gov.cn',        # 教育部官网
        'gjjxcg.moe.edu.cn', # 国家级教学成果奖官网
        'heec.edu.cn',       # 高等教育评估中心
        'chinaedu.edu.cn',   # 中国教育在线
        'eol.cn'             # 教育在线
    ],
    'first_class_majors': [
        'moe.gov.cn',        # 教育部官网
        'zlzy.moe.edu.cn',   # 一流专业建设官网
        'heec.edu.cn',       # 高等教育评估中心
        'chinaedu.edu.cn'    # 中国教育在线
    ],
    'first_class_courses': [
        'moe.gov.cn',        # 教育部官网
        'zlkc.moe.edu.cn',   # 一流课程官网
        'icourse163.org',    # 中国大学MOOC
        'xuetangx.com',      # 学堂在线
        'smartedu.cn'        # 国家智慧教育平台
    ],
    'professional_accreditation': [
        'ceeaa.org.cn',      # 中国工程教育专业认证协会
        'camea.org.cn',      # 中国医学教育认证委员会
        'moe.gov.cn',        # 教育部官网
        'heec.edu.cn'        # 高等教育评估中心
    ],
    'provincial_data': [
        'gdedu.gov.cn',      # 广东省教育厅
        'gdhed.edu.cn',      # 广东省高等教育
        'chinaedu.edu.cn',   # 中国教育在线
        'eol.cn'             # 教育在线
    ]
}

# 广东省权威教育网站
GUANGDONG_EDUCATION_SOURCES = [
    'gdedu.gov.cn',      # 广东省教育厅
    'gdhed.edu.cn',      # 广东省高等教育
    'gdjy.cn',           # 广东教育
    'gdpx.com.cn'        # 广东培训网
]

# =============================================================================
# 🔥 学校别名映射系统 🔥
# =============================================================================

UNIVERSITY_ALIASES = {
    # 改名学校的历史名称映射
    "广州新华学院": {
        "official_name": "广州新华学院",
        "historical_names": ["中山大学新华学院", "中大新华", "中大新华学院"],
        "short_names": ["新华学院", "广州新华"],
        "search_names": ["广州新华学院", "中山大学新华学院", "中大新华", "中大新华学院"],
        "change_year": 2020,
        "notes": "2020年转设为独立设置的民办普通本科高校"
    },
    "广州城市理工学院": {
        "official_name": "广州城市理工学院",
        "historical_names": ["华南理工大学广州学院"],
        "short_names": ["城市理工", "广州城理"],
        "search_names": ["广州城市理工学院", "华南理工大学广州学院"],
        "change_year": 2021,
        "notes": "2021年转设更名"
    },
    "广州软件学院": {
        "official_name": "广州软件学院",
        "historical_names": ["广州大学华软软件学院"],
        "short_names": ["华软", "软件学院"],
        "search_names": ["广州软件学院", "广州大学华软软件学院", "华软"],
        "change_year": 2020,
        "notes": "2020年转设更名"
    },
    "广州南方学院": {
        "official_name": "广州南方学院",
        "historical_names": ["中山大学南方学院"],
        "short_names": ["南方学院", "中大南方"],
        "search_names": ["广州南方学院", "中山大学南方学院", "中大南方"],
        "change_year": 2020,
        "notes": "2020年转设更名"
    },
    "广州华商学院": {
        "official_name": "广州华商学院",
        "historical_names": ["广东财经大学华商学院"],
        "short_names": ["华商学院", "华商"],
        "search_names": ["广州华商学院", "广东财经大学华商学院", "华商"],
        "change_year": 2020,
        "notes": "2020年转设更名"
    },
    "广州理工学院": {
        "official_name": "广州理工学院",
        "historical_names": ["广东技术师范大学天河学院"],
        "short_names": ["广理工", "理工学院"],
        "search_names": ["广州理工学院", "广东技术师范大学天河学院"],
        "change_year": 2021,
        "notes": "2021年转设更名"
    },
    "广州华立学院": {
        "official_name": "广州华立学院",
        "historical_names": ["广东工业大学华立学院"],
        "short_names": ["华立学院", "华立"],
        "search_names": ["广州华立学院", "广东工业大学华立学院", "华立"],
        "change_year": 2020,
        "notes": "2020年转设更名"
    },
    "广州应用科技学院": {
        "official_name": "广州应用科技学院",
        "historical_names": ["广州大学松田学院"],
        "short_names": ["应用科技", "松田学院"],
        "search_names": ["广州应用科技学院", "广州大学松田学院", "松田"],
        "change_year": 2020,
        "notes": "2020年转设更名"
    },
    # 其他重要学校（避免混淆）
    "广东工业大学": {
        "official_name": "广东工业大学",
        "historical_names": [],
        "short_names": ["广工", "广东工大"],
        "search_names": ["广东工业大学", "广工"],
        "change_year": None,
        "notes": "避免与广州理工大学混淆"
    },
    "华南理工大学": {
        "official_name": "华南理工大学",
        "historical_names": [],
        "short_names": ["华工", "华南理工"],
        "search_names": ["华南理工大学", "华工"],
        "change_year": None,
        "notes": "985高校"
    }
}

# 学校官网映射
UNIVERSITY_OFFICIAL_WEBSITES = {
    # 重点大学
    "中山大学": "sysu.edu.cn",
    "华南理工大学": "scut.edu.cn",
    "暨南大学": "jnu.edu.cn",
    "华南师范大学": "scnu.edu.cn",
    "华南农业大学": "scau.edu.cn",
    "广州医科大学": "gzhmu.edu.cn",
    "广州中医药大学": "gzucm.edu.cn",
    "广东药科大学": "gdpu.edu.cn",
    "南方医科大学": "smu.edu.cn",
    "广州大学": "gzhu.edu.cn",
    "广东工业大学": "gdut.edu.cn",
    "广东外语外贸大学": "gdufs.edu.cn",
    "广东财经大学": "gdufe.edu.cn",
    
    # 体育、艺术院校
    "广州体育学院": "gzsport.edu.cn/",
    "广州美术学院": "gzarts.edu.cn",
    "星海音乐学院": "xhcom.edu.cn",
    
    # 师范、技术院校
    "广东技术师范大学": "gpnu.edu.cn",
    "广东第二师范学院": "gdei.edu.cn",
    "仲恺农业工程学院": "zhku.edu.cn",
    "广东警官学院": "gdppla.edu.cn",
    "广东金融学院": "gduf.edu.cn",
    "广州航海学院": "gzmtu.edu.cn",
    
    # 独立学院和民办大学
    "广州城市理工学院": "gcu.edu.cn",
    "广州软件学院": "seig.edu.cn/",
    "广州南方学院": "nfu.edu.cn",
    "广东外语外贸大学南国商学院": "gwng.edu.cn",
    "广州华商学院": "gdhsc.edu.cn",
    "华南农业大学珠江学院": "scauzj.edu.cn",
    "广州理工学院": "gzist.edu.cn/",
    "广州华立学院": "hualixy.edu.cn",
    "广州应用科技学院": "gzasc.edu.cn",
    "广州商学院": "gcc.edu.cn",
    "广州工商学院": "gzgs.edu.cn",
    "广州新华学院": "xhsysu.edu.cn/",
    "广东白云学院": "baiyunu.edu.cn",
    "广东培正学院": "peizheng.edu.cn",
    
    # 职业技术大学
    "广东轻工职业技术大学": "gdqy.edu.cn",
    "广州科技职业技术大学": "gkd.edu.cn/",
    "广州番禺职业技术学院": "gzpyp.edu.cn",
    
    # 特殊情况
    "香港科技大学（广州）": "hkust-gz.edu.cn",
    
    # 历史名称映射（向后兼容）
    "中山大学新华学院": "xhsysu.edu.cn/",
    "中大新华": "xhsysu.edu.cn/",
    "华南理工大学广州学院": "gcu.edu.cn",
    "广州大学华软软件学院": "seig.edu.cn/",
    "中山大学南方学院": "nfu.edu.cn",
    "广东财经大学华商学院": "gdhsc.edu.cn",
    "广东技术师范大学天河学院": "gzist.edu.cn/",
    "广东工业大学华立学院": "hualixy.edu.cn",
    "广州大学松田学院": "gzasc.edu.cn"
}

# =============================================================================
# 🔥 工具函数 🔥
# =============================================================================

def get_university_aliases(university_name: str) -> Dict[str, Any]:
    """获取学校别名信息"""
    return UNIVERSITY_ALIASES.get(university_name, {
        "official_name": university_name,
        "historical_names": [],
        "short_names": [],
        "search_names": [university_name],
        "change_year": None,
        "notes": ""
    })

def get_university_official_website(university_name: str) -> str:
    """获取学校官方网站域名"""
    return UNIVERSITY_OFFICIAL_WEBSITES.get(university_name, "")

def get_all_search_names(university_name: str) -> List[str]:
    """获取学校的所有搜索名称（包括别名）"""
    alias_info = get_university_aliases(university_name)
    return alias_info.get("search_names", [university_name])

def build_search_query_with_aliases(university_name: str, keywords: str, exclude_confused: bool = True) -> List[str]:
    """构建包含别名的搜索查询"""
    alias_info = get_university_aliases(university_name)
    search_names = alias_info.get("search_names", [university_name])
    
    queries = []
    for name in search_names:
        base_query = f'"{name}" {keywords}'
        
        # 排除混淆学校
        if exclude_confused:
            confusion_exclusions = {
                "广州新华学院": ['-"安徽新华学院"', '-"新华学院"'],
                "广州理工学院": ['-"广东工业大学"', '-"广工"', '-"华南理工大学"'],
                "广东工业大学": ['-"广州理工"', '-"理工学院"'],
            }
            
            exclusions = confusion_exclusions.get(university_name, [])
            if exclusions:
                base_query += " " + " ".join(exclusions)
        
        queries.append(base_query)
    
    return queries

# =============================================================================
# 🔥 数据类定义 🔥
# =============================================================================

@dataclass
class EducationSearchConfig:
    """教育数据搜索配置类"""
    name: str
    system_role: str
    user_prompt: str
    temperature: float = 0.2
    model: str = "deepseek-v3"
    max_iterations: int = 5
    description: str = ""
    target_sources: List[str] = None
    enable_search: bool = True

    def __post_init__(self):
        if self.target_sources is None:
            self.target_sources = [
                "教育部官网", "教育部评估中心", "学校官网", "ESI数据库",
                "软科排名", "一流大学建设名单", "专业认证官网"
            ]

# =============================================================================
# 🔥 主要管理器类 🔥
# =============================================================================

class EducationSearchManager:
    """教育数据搜索管理器"""
    
    def __init__(self):
        self.configs = {}
        self.universities = []
        
        # 指标中文名称映射
        self.metric_names = {
            'esi_1_percent': 'ESI前1%学科数量',
            'esi_1_permille': 'ESI前1‰学科数量',
            'undergraduate_majors_total': '本科专业总数',
            'major_accreditation': '专业认证通过数',
            'national_first_class_majors': '国家级一流本科专业数量',
            'provincial_first_class_majors': '省级一流本科专业数量',
            'national_teaching_awards': '国家级教学成果奖数量',
            'provincial_teaching_awards': '省级教学成果奖数量',
            'youth_teacher_competition': '全国高校青年教师教学竞赛获奖数量',
            'national_first_class_courses': '国家级一流本科课程数量',
            'provincial_first_class_courses': '省级一流本科课程数量',
            'national_smart_platform_courses': '国家高等教育智慧平台课程数量',
            'provincial_smart_platform_courses': '省级高等教育智慧平台课程数量'
        }
        
        # 初始化配置
        self._init_education_configs()

    # =========================================================================
    # 🔥 公共接口方法 🔥
    # =========================================================================
    
    def get_config(self, config_name: str) -> EducationSearchConfig:
        """获取指定配置"""
        if config_name not in self.configs:
            raise ValueError(f"配置 '{config_name}' 不存在")
        return self.configs[config_name]
    
    def list_configs(self) -> Dict[str, str]:
        """列出所有可用配置"""
        return {name: config.description for name, config in self.configs.items()}
    
    def load_universities(self, csv_path: str):
        """从CSV文件加载大学列表"""
        try:
            df = pd.read_csv(csv_path, encoding='utf-8')
            self.universities = df['学校名称'].unique().tolist()
            print(f"✅ 加载了 {len(self.universities)} 所大学")
        except Exception as e:
            print(f"❌ 加载大学列表失败: {e}")

    # =========================================================================
    # 🔥 消息创建方法 - 统一使用多源搜索 🔥
    # =========================================================================
    
    def create_messages(self, config_name: str, university: str) -> List[Dict[str, str]]:
        """根据配置和大学创建消息列表（兼容旧版）"""
        return self.create_messages_with_year(config_name, university, datetime.now().year)
    
    def create_messages_with_year(self, config_name: str, university: str, target_year: int) -> List[Dict[str, str]]:
        """🔥 统一使用多源搜索策略 🔥"""
        return self.create_messages_with_multi_source_search(config_name, university, target_year)
    
    def create_messages_with_multi_source_search(self, config_name: str, university: str, year: int) -> List[Dict]:
        """多源权威搜索消息创建（主要搜索方法）"""
        config = self.get_config(config_name)
        official_website = get_university_official_website(university)
        alias_info = get_university_aliases(university)
        
        # 获取该指标的权威数据源
        metric_category = self._get_metric_category(config_name)
        authoritative_sources = AUTHORITATIVE_DATA_SOURCES.get(metric_category, [])

        # 🔥 针对不同指标的时间搜索策略 🔥
        time_search_strategy = self._build_time_search_strategy(config_name, year)
        
        # 构建增强的搜索提示
        enhanced_system_role = f"""{config.system_role}

🎯 **多源权威搜索模式**
目标学校：{university}
搜索指标：{config.description}
官方网站：{official_website}

🔍 **搜索层级策略**：
1. **第一层：官网搜索** - 优先级最高
2. **第二层：权威机构** - 教育部、省教育厅等官方机构
3. **第三层：权威媒体** - 中国教育在线、教育媒体等
4. **第四层：专业平台** - 相关专业认证、评估平台

📊 **数据源权威性排序**：
{self._format_authoritative_sources(authoritative_sources)}

🔥 **时间完整性策略**：
{time_search_strategy}

✅ **数据验证原则**：
1. 优先使用官方(.gov.cn)和学校(.edu.cn)数据
2. 媒体报道需要与官方数据交叉验证
3. 如果多源数据不一致，分别列出并说明
4. 明确标注每个数据的来源和可信度
5. **重要**: 不要因为找到早期数据就停止搜索，务必寻找年末最新数据"""

        # 构建多源搜索查询
        search_strategies = self._build_multi_source_queries(university, config_name, official_website, authoritative_sources)
        
        enhanced_user_prompt = f"""{config.user_prompt.format(university=university, target_year=year)}

🔍 **具体搜索策略**：
{search_strategies}

📅 **时间完整性要求**：
- **搜索目标**: {year}年12月31日前的完整数据
- **搜索时间范围**: {year}年1月-12月的所有数据更新
- **数据优先级**: {year}年12月 > {year}年6月 > {year}年1月 > {year-1}年12月
- **特别注意**: 某些数据可能在{year}年下半年或年末才公布，不要遗漏，ESI数据可能会在第二年的年初公布去年的数据，这一部分也不要遗漏

🔥 **多时间点搜索策略**：
1. 搜索"{university}" "{config.description}" {year}年12月
2. 搜索"{university}" "{config.description}" {year}年最新
3. 搜索"{university}" "{config.description}" {year}年更新
4. 搜索"{university}" "{config.description}" "截止{year}年"
5. 对于可能的历史名称，也进行相同的多时间点搜索

📊 **输出要求**：
1. 明确的数字结果（基于最新数据）
2. 数据来源列表（按可信度排序）
3. **详细时间信息**：数据发布月份、最后更新时间
4. 如果发现多个时间版本，请列出并说明差异
5. 如果多源数据不一致，分别列出各来源的时间和数值

⚠️ **避免数据遗漏**：
- 不要因为找到{year}年3月的数据就认为任务完成
- 务必检查{year}年6月、9月、12月是否有数据更新
- 如果某个指标通常年末发布，重点搜索{year}年10-12月数据"""

        return [
            {"role": "system", "content": enhanced_system_role},
            {"role": "user", "content": enhanced_user_prompt}
        ]
    
    def create_messages_with_official_website(self, config_name: str, university: str, year: int) -> List[Dict]:
        """官网限定搜索消息创建（备用方法）"""
        config = self.get_config(config_name)
        official_website = get_university_official_website(university)
        alias_info = get_university_aliases(university)
        
        if not official_website:
            return self.create_messages_with_year_and_exclusion(config_name, university, year)
        
        # 生成增强的学校名称用于搜索
        enhanced_university_name = self._generate_enhanced_university_name(university, alias_info)
        
        # 获取搜索关键词和显示名称
        search_keywords = self._get_search_keywords(config_name)
        display_name = self._get_display_name(config_name)
        
        # 构建包含别名信息的学校描述
        historical_context = self._build_historical_context(university, alias_info, enhanced_university_name)

        system_role = f"""{config.system_role}

🚨 **严格官网限定搜索模式** 🚨
- **搜索目标**: {enhanced_university_name}
- **官方网站**: {official_website}
- **绝对要求**: 只能从该学校的官方网站域名搜索数据
- **严禁**: 使用其他学校的数据，即使学校名称相似
{historical_context}

🎯 **搜索策略**:
1. **首选**: site:{official_website} 限定搜索
2. **多名称搜索**: 使用现用名和历史名称进行搜索
3. **验证**: 确保每个结果都来自正确的学校官网
4. **拒绝**: 如果官网无数据，宁可返回"无数据"也不用其他学校数据"""

        user_prompt = f"""🔍 **官网限定搜索任务**

**目标**: 搜索 {enhanced_university_name} 截止{year}年的{display_name}

**搜索要求**:
1. **必须使用**: site:{official_website} 限定搜索
2. **搜索年份**: 截止到{year}年的数据
3. **结果验证**: 确保所有数据都来自 {university} 官网

**🔥 多重搜索策略**:
1. site:{official_website} "{university}" "{search_keywords}" {year}
2. site:{official_website} "{enhanced_university_name}" "{search_keywords}"
3. site:{official_website} "{search_keywords}" {year}

**质量要求**:
- 明确标注数据来源页面URL
- 确认学校名称完全匹配（现用名或历史名）
- 如果官网无相关数据，明确说明"该官网暂无此数据"
- 一定要反复核实数据的真实性，例如专业的真实性，交叉学科和多学科并不算是一个真正的专业，你需要确认是否存在这种专业，如果没有则将其排除掉

⚠️ **严禁行为**:
- 使用非 {official_website} 域名的数据
- 使用其他学校的数据
- 推测或编造数据

请开始搜索..."""

        return [
            {"role": "system", "content": system_role},
            {"role": "user", "content": user_prompt}
        ]
    
    def create_messages_with_year_and_exclusion(self, config_name: str, university: str, year: int) -> List[Dict]:
        """防混淆搜索消息创建（备用方法）"""
        config = self.get_config(config_name)
        alias_info = get_university_aliases(university)
        
        # 生成增强的学校名称用于搜索
        enhanced_university_name = self._generate_enhanced_university_name(university, alias_info)
        
        # 获取搜索关键词和显示名称
        search_keywords = self._get_search_keywords(config_name)
        display_name = self._get_display_name(config_name)
        
        # 构建包含别名信息的学校描述
        historical_context = self._build_historical_context(university, alias_info, enhanced_university_name)

        # 定义容易混淆的学校对应关系
        confusion_map = {
            "广州新华学院": ["安徽新华学院", "新华学院"],
            "广州理工学院": ["广东工业大学", "广工", "华南理工大学"],
            "广东工业大学": ["广州理工学院", "其他理工大学"],
            "广州中医药大学": ["其他中医药大学"],
            "华南师范大学": ["其他师范大学"],
        }
        
        exclude_schools = confusion_map.get(university, [])
        exclude_terms = [f'-"{school}"' for school in exclude_schools]
        exclude_string = " ".join(exclude_terms)

        system_role = f"""{config.system_role}

🚨 **精确学校搜索 - 防混淆模式** 🚨
- **搜索目标**: {enhanced_university_name} (仅此一所)
- **严格排除**: {', '.join(exclude_schools) if exclude_schools else '无'}
- **验证要求**: 每个搜索结果必须明确属于目标学校
{historical_context}

⚠️ **特别警告**:
- 绝对不能使用 {', '.join(exclude_schools)} 的数据
- 如果搜索结果包含其他学校信息，必须明确排除
- 优先使用带有完整学校名称的官方数据
- 历史名称的数据同样有效，但要确认是同一所学校"""

        user_prompt = f"""🔍 **精确学校搜索任务**

**目标**: 搜索 {enhanced_university_name} 截止{year}年的{display_name}
**排除学校**: {', '.join(exclude_schools) if exclude_schools else '无'}

**🔥 多重搜索策略**:
1. "{enhanced_university_name}" "{search_keywords}" {year} {exclude_string}
2. "{university}" "{search_keywords}" {year} {exclude_string}
3. "{enhanced_university_name}" site:edu.cn "{search_keywords}" {exclude_string}

**验证清单**:
- ✅ 结果明确提到 {university}（或其历史名称）
- ✅ 数据确实属于该学校
- ❌ 不包含 {', '.join(exclude_schools)} 的信息
- ✅ 来源可信且时间符合要求

**特别提醒**:
- 如果找到以历史名称发布的数据，同样有效
- 请在结果中说明数据是以哪个名称找到的
- 确保不会与其他同名或类似名称的学校混淆

请开始精确搜索..."""

        return [
            {"role": "system", "content": system_role},
            {"role": "user", "content": user_prompt}
        ]

    # =========================================================================
    # 🔥 私有辅助方法 🔥
    # =========================================================================
    
    def _build_time_search_strategy(self, config_name: str, year: int) -> str:
        """构建针对不同指标的时间搜索策略"""
        
        # 不同指标的数据更新规律
        update_patterns = {
            'esi_1_percent': {
                'update_months': [1, 5, 9, 11],
                'key_period': f'{year}年11月',
                'description': 'ESI数据通常每年1月、5月、9月、11月更新，重点搜索11月最新数据'
            },
            'esi_1_permille': {
                'update_months': [1, 5, 9, 11],
                'key_period': f'{year}年11月',
                'description': 'ESI数据通常每年1月、5月、9月、11月更新，重点搜索11月最新数据'
            },
            'provincial_teaching_awards': {
                'update_months': [6, 7, 8, 9, 10, 11, 12],
                'key_period': f'{year}年下半年',
                'description': '省级教学成果奖通常在年中至年末公布，重点搜索6-12月数据'
            },
            'national_teaching_awards': {
                'update_months': [8, 9, 10, 11, 12],
                'key_period': f'{year}年下半年',
                'description': '国家级教学成果奖通常在下半年公布，重点搜索8-12月数据'
            },
            'national_first_class_majors': {
                'update_months': [3, 6, 9, 12],
                'key_period': f'{year}年分批次',
                'description': '一流专业建设点可能分批次公布，需要搜索全年各批次数据'
            },
            'provincial_first_class_majors': {
                'update_months': [4, 6, 8, 10, 12],
                'key_period': f'{year}年分批次',
                'description': '省级一流专业可能分多批次公布，需要搜索全年数据'
            },
            'national_first_class_courses': {
                'update_months': [4, 7, 11],
                'key_period': f'{year}年分批次',
                'description': '国家级一流课程通常分批次认定，重点搜索4月、7月、11月数据'
            },
            'provincial_first_class_courses': {
                'update_months': [5, 8, 12],
                'key_period': f'{year}年分批次',
                'description': '省级一流课程通常分批次认定，重点搜索5月、8月、12月数据'
            },
            'youth_teacher_competition': {
                'update_months': [10, 11, 12],
                'key_period': f'{year}年年末',
                'description': '青年教师教学竞赛通常在年末公布获奖结果'
            },
            'undergraduate_majors_total': {
                'update_months': [6, 9, 12],
                'key_period': f'{year}年年中至年末',
                'description': '本科专业总数通常在招生季前后更新'
            },
            'major_accreditation': {
                'update_months': [6, 7, 8, 9, 10],
                'key_period': f'{year}年下半年',
                'description': '专业认证结果通常在下半年公布'
            }
        }
        
        pattern = update_patterns.get(config_name, {
            'update_months': [6, 12],
            'key_period': f'{year}年末',
            'description': '重点搜索年中和年末的数据更新'
        })
        
        update_months_str = '、'.join([f'{month}月' for month in pattern['update_months']])
        
        return f"""
📅 **{config_name}数据更新规律**：
- **常见更新时间**: {update_months_str}
- **重点搜索期**: {pattern['key_period']}
- **策略说明**: {pattern['description']}

🔍 **时间搜索要求**：
1. 优先搜索{pattern['key_period']}的最新数据
2. 如果未找到最新数据，按月份倒序搜索：{update_months_str}
3. 对于每个时间点，搜索格式："{year}年X月 {config_name}"
4. 特别关注包含"最新"、"更新"、"截止"等关键词的{year}年数据
5. **避免早停**：即使找到{year}年早期数据，也要继续搜索是否有年末更新"""
    
    def _get_metric_category(self, config_name: str) -> str:
        """获取指标类别"""
        category_mapping = {
            'esi_1_percent': 'esi_subjects',
            'esi_1_permille': 'esi_subjects',
            'national_teaching_awards': 'teaching_awards',
            'provincial_teaching_awards': 'teaching_awards',
            'national_first_class_majors': 'first_class_majors',
            'provincial_first_class_majors': 'first_class_majors',
            'national_first_class_courses': 'first_class_courses',
            'provincial_first_class_courses': 'first_class_courses',
            'major_accreditation': 'professional_accreditation',
            'youth_teacher_competition': 'teaching_awards'
        }
        return category_mapping.get(config_name, 'provincial_data')

    def _format_authoritative_sources(self, sources: List[str]) -> str:
        """格式化权威数据源列表"""
        if not sources:
            return "- 学校官网 (.edu.cn)\n- 教育部官网 (moe.gov.cn)\n- 省教育厅官网"
        
        formatted = []
        source_descriptions = {
            'moe.gov.cn': '教育部官网（最高权威）',
            'gdedu.gov.cn': '广东省教育厅（省级权威）',
            'eol.cn': '中国教育在线（权威媒体）',
            'chinaedu.edu.cn': '中国教育（权威媒体）',
            'clarivate.com': '科睿唯安（ESI官方）',
            'heec.edu.cn': '高等教育评估中心'
        }
        
        for i, source in enumerate(sources, 1):
            source_desc = source_descriptions.get(source, source)
            formatted.append(f"{i}. {source_desc}")
        
        return "\n".join(formatted)

    def _build_multi_source_queries(self, university: str, config_name: str, official_website: str, auth_sources: List[str]) -> str:
        """构建多源搜索查询策略"""
        alias_info = get_university_aliases(university)
        all_names = [university] + alias_info.get("historical_names", [])
        
        strategies = []
        
        # 1. 官网搜索
        if official_website:
            search_keywords = self._get_search_keywords(config_name)
            strategies.append(f"""
1️⃣ **官网搜索**（最高优先级）：
   - site:{official_website} {search_keywords}
   - site:{official_website} 获奖 奖项
   - site:{official_website} 荣誉 成果""")
        
        # 2. 政府官网搜索
        search_keywords = self._get_search_keywords(config_name)
        strategies.append(f"""
2️⃣ **政府官网搜索**：
   - site:moe.gov.cn "{university}" {search_keywords}
   - site:gdedu.gov.cn "{university}" 获奖
   - "{search_keywords}" "{university}" """)
        
        # 3. 权威媒体搜索
        strategies.append(f"""
3️⃣ **权威媒体搜索**：
   - site:eol.cn "{university}" {search_keywords}
   - site:chinaedu.edu.cn "{university}" 获奖
   - "{university}" "{search_keywords}" 新闻""")
        
        # 4. 历史名称搜索
        if len(all_names) > 1:
            historical_names = ", ".join(all_names[1:])
            strategies.append(f"""
4️⃣ **历史名称搜索**：
   注意：该校历史名称包括：{historical_names}
   - 对以上历史名称也进行相同搜索
   - 特别注意2020年前后的数据可能使用历史名称""")
        
        return "\n".join(strategies)

    def _generate_enhanced_university_name(self, university: str, alias_info: Dict[str, Any]) -> str:
        """生成增强的学校名称，包含关键别名信息"""
        historical_names = alias_info.get("historical_names", [])
        
        if not historical_names:
            return university
        
        # 为不同学校生成特定的增强名称
        enhancement_rules = {
            "广州新华学院": "广州新华学院(曾用名中大新华)",
            "广州城市理工学院": "广州城市理工学院(曾用名华工广州学院)",
            "广州南方学院": "广州南方学院(曾用名中大南方)",
            "广州华商学院": "广州华商学院(曾用名财大华商)",
            "广州理工学院": "广州理工学院(曾用名技师天河)",
            "广州华立学院": "广州华立学院(曾用名广工华立)",
            "广州应用科技学院": "广州应用科技学院(曾用名广大松田)",
            "广州软件学院": "广州软件学院(曾用名华软)"
        }
        
        # 如果有预定义的增强规则，使用它
        if university in enhancement_rules:
            return enhancement_rules[university]
        
        # 否则，动态生成增强名称
        main_historical_name = historical_names[0]
        
        # 提取历史名称的关键部分
        if "大学" in main_historical_name and "学院" in main_historical_name:
            parts = main_historical_name.split("大学")
            if len(parts) >= 2:
                university_part = parts[0]
                college_part = parts[1].replace("学院", "")
                short_name = f"{university_part[0:2]}{college_part}"
                return f"{university}(曾用名{short_name})"
        
        # 如果无法智能简化，使用完整历史名称
        return f"{university}(曾用名{main_historical_name})"

    def _get_search_keywords(self, config_name: str) -> str:
        """获取搜索关键词"""
        search_keywords_map = {
            'esi_1_percent': 'ESI前1%学科',
            'esi_1_permille': 'ESI前1‰学科',
            'undergraduate_majors_total': '本科专业总数',
            'major_accreditation': '专业认证',
            'national_first_class_majors': '国家级一流专业',
            'provincial_first_class_majors': '省级一流专业',
            'national_teaching_awards': '国家级教学成果奖',
            'provincial_teaching_awards': '省级教学成果奖',
            'youth_teacher_competition': '青年教师教学竞赛',
            'national_first_class_courses': '国家级一流课程',
            'provincial_first_class_courses': '省级一流课程',
            'national_smart_platform_courses': '国家智慧教育平台',
            'provincial_smart_platform_courses': '省级智慧教育平台'
        }
        return search_keywords_map.get(config_name, config_name.replace('_', ' '))

    def _get_display_name(self, config_name: str) -> str:
        """获取显示名称"""
        return self.metric_names.get(config_name, config_name.replace('_', ' '))

    def _build_historical_context(self, university: str, alias_info: Dict[str, Any], enhanced_university_name: str) -> str:
        """构建历史背景信息"""
        historical_names = alias_info.get("historical_names", [])
        
        if historical_names:
            main_historical_name = historical_names[0]
            return f"""

🏫 **学校信息**:
- **搜索目标**: {enhanced_university_name}
- **现用名称**: {university}
- **历史名称**: {main_historical_name}
- **改名时间**: {alias_info.get("change_year", "未知")}年
- **备注**: {alias_info.get("notes", "")}

⚠️ **重要**: 搜索时使用增强名称以提高准确性！"""
        else:
            return f"""

🏫 **学校信息**:
- **搜索目标**: {enhanced_university_name}"""

    def _create_enhanced_base_config(self, name: str, chinese_name: str, search_keywords: str) -> EducationSearchConfig:
        """🔥 创建增强的基础配置模板（集成时间搜索策略）🔥"""
        return EducationSearchConfig(
            name=name,
            system_role=f"""你是专业的教育数据分析师，专门搜索{chinese_name}数据。

🔥 **数据时间完整性原则**：
1. 必须搜索到目标年份12月31日的完整数据
2. 不要因为找到年初数据就停止搜索
3. 优先搜索年末最新数据，如果没有则按月份倒序搜索
4. 特别关注包含"最新"、"更新"、"截止"等关键词的数据

重要原则：
1. 必须精确匹配学校名称，绝对不能混淆不同学校
2. 如果某学校确实没有{chinese_name}，应明确回答"0个"或"无"
3. 不要因为搜索不到数据就使用其他学校的数据
4. 优先从权威网站获取信息：教育部官网、学校官网等
5. 必须在搜索时加上学校全称进行精确查找
6. 必须注明数据的具体更新时间（精确到月份）""",
            
            user_prompt=f"""请搜索 **{{university}}** 的{chinese_name}。

🚨 严格要求：
1. 搜索时必须使用完整的学校名称"{{university}}"，不能模糊匹配
2. 确认搜索结果确实是关于"{{university}}"这所学校的，而不是其他学校
3. 如果找不到"{{university}}"的相关数据，请明确说明"未找到数据"，不要使用其他学校的数据
4. 某些学校可能确实没有{chinese_name}，这种情况请如实回答"0个"

🔥 **多时间点搜索策略**：
1. 优先搜索：{{university}} {chinese_name} {{target_year}}年12月
2. 备选搜索：{{university}} {chinese_name} {{target_year}}年11月
3. 补充搜索：{{university}} {chinese_name} {{target_year}}年更新
4. 验证搜索：{{university}} {chinese_name} "截止{{target_year}}年"

搜索要求：
1）从权威网站搜索：教育部官网、{{university}}官网
2）提供具体的{search_keywords}（如果有的话）
3）给出准确的数量统计
4）注明数据来源和更新时间（精确到月份）
5）在回答开头明确确认：这是关于"{{university}}"的{{target_year}}年数据

⚠️ **避免数据遗漏**：
- 不要因为找到{{target_year}}年早期数据就停止搜索
- 务必寻找{{target_year}}年年末的最新更新
- 如果数据有多个版本，说明时间差异并选择最新版本""",
            
            description=f"搜索各大学{chinese_name}"
        )

    def _init_education_configs(self):
        """🔥 初始化教育数据搜索配置（分层架构）🔥"""
        
        # 🔥 大部分指标使用增强的基础配置 🔥
        basic_configs = [
            ("undergraduate_majors_total", "本科专业总数", "专业类别"),
            ("major_accreditation", "本科专业认证通过数量", "认证专业名称"),
            ("national_first_class_majors", "国家级一流本科专业建设点数量", "专业名称列表"),
            ("provincial_first_class_majors", "省级一流本科专业建设点数量", "专业名称列表"),
            ("national_teaching_awards", "国家级教学成果奖数量", "获奖项目名称"),
            ("youth_teacher_competition", "全国高校青年教师教学竞赛获奖", "获奖教师姓名和项目"),
            ("national_first_class_courses", "国家级一流本科课程数量", "课程名称"),
            ("provincial_first_class_courses", "省级一流本科课程数量", "课程名称"),
            ("national_smart_platform_courses", "国家级高等教育智慧平台课程数量", "课程名称和类别"),
            ("provincial_smart_platform_courses", "省级高等教育智慧平台课程数量", "课程名称和类别")
        ]
        
        # 批量创建增强的基础配置
        for name, chinese_name, keywords in basic_configs:
            self.configs[name] = self._create_enhanced_base_config(name, chinese_name, keywords)
        
        # 🔥 只有真正需要特殊处理的指标才单独配置 🔥
        # 省级教学成果奖需要特殊的多源搜索策略
        self.configs['provincial_teaching_awards'] = EducationSearchConfig(
            name="provincial_teaching_awards",
            system_role="""你是教学成果奖数据专家，专门搜索省级教学成果奖信息。

🔥 **数据时间完整性原则**：
1. 必须搜索到目标年份12月31日的完整数据
2. 省级教学成果奖通常在年中至年末公布，重点搜索6-12月数据
3. 不要因为找到年初数据就停止搜索
4. 特别关注包含"最新"、"更新"、"截止"等关键词的数据

🎯 多源权威搜索策略：
1. **官网优先**: 首先搜索学校官网的获奖信息
2. **省厅权威**: 搜索广东省教育厅官网的公布名单
3. **教育媒体**: 搜索权威教育媒体的报道
4. **历年数据**: 搜索近年来的所有获奖记录

🔍 权威数据源：
- 学校官网 (.edu.cn域名)
- 广东省教育厅官网 (gdedu.gov.cn)
- 中国教育在线 (eol.cn)
- 教育部官网相关信息
- 权威教育媒体报道

重要原则：
1. 必须精确匹配学校名称，包括历史名称
2. 搜索近5-10年的获奖记录
3. 接受权威第三方媒体的报道作为补充数据源
4. 如果学校确实没有获奖记录，明确说明
5. 优先使用官方数据，媒体报道作为佐证
6. 必须确保你搜索到的数据的url是真实有效的，不能使用虚假或伪造的url和数据源，请你去真实的检索，而不是简单的去做一个url的生成""",
            
            user_prompt="""请搜索 **{university}** 获得的省级教学成果奖数量（广东省教学成果奖）。

🔍 **多维度搜索策略**：

1️⃣ **学校官网搜索**：
   - 搜索学校官网的教学成果奖信息
   - 查找获奖新闻和荣誉展示

2️⃣ **省教育厅官网搜索**：
   - 搜索: site:gdedu.gov.cn "{university}" 教学成果奖
   - 搜索: "广东省教学成果奖" "{university}"
   - 搜索历年获奖名单中的该校信息

3️⃣ **权威媒体搜索**：
   - 搜索: site:eol.cn "{university}" 教学成果奖
   - 搜索权威教育媒体的获奖报道

4️⃣ **综合搜索**：
   - 搜索: "{university}" "广东省教学成果奖" 获奖
   - 搜索近5-10年的获奖记录

🚨 **关键要求**：
1. 学校名称精确匹配（注意可能的历史名称变更）
2. 统计所有年份的获奖总数
3. 按等级分类统计（特等奖、一等奖、二等奖等）
4. 提供具体的获奖项目名称和年份
5. 明确标注数据来源（官网/省厅/媒体报道）
6. 如果多个来源数据不一致，请说明并提供各来源的具体数据

📊 **预期输出格式**：
- 总获奖数量：X项
- 分级统计：特等奖X项，一等奖X项，二等奖X项
- 具体获奖项目列表（项目名称、获奖年份、奖项等级）
- 数据来源：[具体网站名称和链接]
- 数据更新时间：YYYY年

如果确实未找到获奖记录，请明确说明"经多源搜索未找到{university}的省级教学成果奖获奖记录"。""",
            description="搜索各大学省级教学成果奖（多源权威搜索）",
            target_sources=["学校官网", "省教育厅", "权威教育媒体", "教育部官网"]
        )
        # 🔥 ESI前1%学科专属特殊搜索策略 🔥
        self.configs['esi_1_percent'] = EducationSearchConfig(
            name="esi_1_percent",
            system_role="""你是一名专业的学术数据分析助手。请基于**科睿唯安（Clarivate）Essential Science Indicators (ESI)** 数据库的官方数据，执行以下精确查询任务：""",
            
            user_prompt="""请搜索 **{university}** 的ESI前1%学科数量和具体学科名称。

  **具体要求：**
1.  **学校名称：** 请严格匹配学校官方全称 `[例如：北京大学、清华大学、Harvard University、Stanford University]`。*（注意：如果学校有常用简称或别名，请在此处明确指出，例如：“浙江大学”也称“浙大”，但请优先使用“浙江大学”）*
2.  **年份：** 指定年份 `[例如：2023, 2022]`。请确保数据反映的是该**自然年结束（通常是12月31日）或该年份最后一次ESI更新（通常为3月、5月、9月、11月）时**的学科状态。*（请明确你期望的截止时间点，例如：“2023年12月数据” 或 “基于2023年11月更新的ESI数据”）*
3.  **数据来源：** **仅限**科睿唯安ESI数据库。请**不要**包含其他排名系统（如QS, THE, ARWU）的数据。可以在中国教育在线（https://www.eol.cn）等权威教育媒体上查找相关报道作为权威数据
4.  **目标排名：** **仅**列出在该时间点被ESI认定为全球排名进入**前1%** 的学科。
5.  **输出格式：**
    *   清晰列出所有符合条件的 **ESI学科领域名称**（例如：`Chemistry`, `Clinical Medicine`, `Engineering`, `Materials Science`, `Computer Science`等）。
    *   如果该校在指定年份有学科进入前1%，请按学科名称的字母顺序排列。
    *   如果该校在指定年份**没有任何**学科进入ESI前1%，请明确输出：“`[学校完整官方名称]` 在 `[年份]` 的ESI数据中没有学科进入全球前1%。”
    *   如果存在学校名称歧义（例如：存在多个同名或相似名称的学校），请**暂停**并向我确认具体指的是哪一所学校（提供国家、地区等关键信息）。
    *   请注明结果所依据的**具体数据发布日期或统计周期**（例如：“基于2023年11月发布的ESI数据（覆盖时间范围2013年1月1日-2023年8月31日）”）。""",
            description="搜索各大学ESI前1%学科（专业权威搜索）",
            target_sources=["科睿唯安官网", "学校官网", "ESI统计平台", "权威教育媒体"]
        )

        # 🔥 ESI前1‰学科专属特殊搜索策略 🔥
        self.configs['esi_1_permille'] = EducationSearchConfig(
            name="esi_1_permille",
            system_role="""你是一名学术数据分析专家，请基于 **科睿唯安（Clarivate）Essential Science Indicators (ESI)** 数据库的官方数据，执行以下任务：""",
            
            user_prompt="""请搜索 **{university}** 的ESI前1‰（千分之一）学科数量和具体学科名称。

**查询目标**  
检索并确认 `[学校完整官方名称]` 在 `[年份]` **自然年结束时（或指定统计周期）** 是否进入 **ESI 全球前 1‰** 的学科，并列出所有符合条件的学科名称。

**关键要求**  
1. **学校名称**  
   - 使用学校 **官方注册全称**（如 `清华大学`、`Harvard University`），避免简称。若存在多校区或重名，需明确标注地区（如 `University of California, Berkeley`）。  
   - *示例*：`河北工业大学`、`济南大学`:cite[1]:cite[6]。  

2. **年份与数据版本**  
   - 年份：`[指定自然年，如 2025]`。  
   - **必须绑定 ESI 更新版本**（如 `2025 年 3 月数据`），因 ESI 每年更新 6 次（2月、5月、7月、9月、11月等），不同版本数据差异显著:cite[1]:cite[6]:cite[10]。  
   - *示例*：`基于 2025 年 3 月发布的 ESI 数据（覆盖 2015-2025 年统计周期）`:cite[1]。  

3. **学科范围与门槛**  
   - 仅检索 **全球前 0.1%（千分之一）** 学科，排除前 1% 或更低阈值学科。  
   - 学科名称需严格匹配 ESI 的 **22 个官方领域**（如 `工程学`、`化学`、`环境/生态学`，不可简写为“工程”或“环境”）:cite[9]:cite[10]。  

4. **数据来源**  
   - 仅限 **科睿唯安 ESI 数据库**（https://esi.clarivate.com），排除其他排名系统（如 QS、THE）:cite[9]。
   - 可以在中国教育在线（https://www.eol.cn）等权威教育媒体上查找相关报道作为权威数据

5. **输出格式**  
   - **若存在千分之一学科**：  
     - 按学科名称字母顺序列出（如 `Chemistry, Engineering`）。  
     - 注明 **统计周期**（如“基于 2025 年 3 月数据，覆盖 2015.01.01-2024.12.31”）:cite[6]:cite[10]。  
   - **若无符合学科**：  
     - 明确输出：`[学校名称] 在 [年份] 的 ESI 数据中无学科进入全球前 1‰`。  
   - **名称歧义处理**：  
     - 若校名存在多个匹配机构（如 `北京工业大学` vs `河北工业大学`），暂停并请求用户确认地区/国家:cite[1]:cite[2]。  

6. **验证依据**  
   - 需在结果中标注 **数据发布日期**（如“科睿唯安 2025 年 3 月 13 日发布”）及 **被引频次排名位次**（如“全球第 193 位”）:cite[1]:cite[6]:cite[10]。  """,
            description="搜索各大学ESI前1‰学科（超精密权威搜索）",
            target_sources=["科睿唯安高级数据", "学校重大成就", "顶级评价机构", "学术突破报道"]
        )

# =============================================================================
# 🔥 全局实例 🔥
# =============================================================================

# 创建全局教育搜索管理器实例
education_manager = EducationSearchManager()