import asyncio
import os
import json
import re
import time
from typing import List, Optional, Dict
from datetime import datetime

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode, LLMConfig
from crawl4ai.extraction_strategy import LLMExtractionStrategy

from models.school_intro_data import SchoolIntroData, CrawlResult
from config import *


def get_browser_config() -> BrowserConfig:
    """
    获取浏览器配置
    """
    print("🔧 配置浏览器参数...")
    config = BrowserConfig(
        browser_type="chromium",
        headless=ENABLE_HEADLESS,
        verbose=True,
    )
    print("✅ 浏览器配置完成")
    return config


def create_school_intro_llm_strategy() -> LLMExtractionStrategy:
    """
    创建学校简介信息提取的LLM策略
    """
    print("🤖 创建学校简介信息提取策略...")
    
    extraction_instruction = """你是专业的教育数据提取专家。请从以下学校简介或学校概况网页内容中提取核心教学数据。

**提取目标数据：**
1. 学校名称：完整的学校名称
2. 本科专业总数：学校开设的本科专业数量
3. 国家级一流本科专业建设点：获得国家级一流本科专业建设点的数量
4. 省级一流本科专业建设点：获得省级一流本科专业建设点的数量  

**数据识别关键词参考：**
- 本科专业：可能表述为"本科专业"、"专业"、"学科专业"、"招生专业"、"开设专业"等
- 一流专业：可能表述为"一流本科专业建设点"、"一流专业"、"金专"、"国家级专业"、"省级专业"、"专业建设点"等

**提取要求：**
- 仔细分析整个网页内容，重点关注学校简介、学校概况、专业设置、教学成果等部分
- 如果某项数据未明确提及，请填写0
- 确保提取的数据准确可靠，不要推测或猜测
- 优先提取明确的数字，避免模糊表述
- 注意区分国家级和省级的不同

**输出格式（严格JSON数组）：**
[
    {
    "school_name": "学校名称",
    "undergraduate_majors": 本科专业总数,
    "national_first_class_majors": 国家级一流专业数,
    "provincial_first_class_majors": 省级一流专业数,
    },
    {
    "school_name": "学校名称",
    "undergraduate_majors": 本科专业总数,
    "national_first_class_majors": 国家级一流专业数,
    "provincial_first_class_majors": 省级一流专业数,
    }
]

**重要说明：**
- 所有数字字段必须是整数类型，不能是字符串
- 如果找不到相关信息，对应字段填写0
- 不要猜测或推断信息，只提取明确显示的内容
- 学校名称必须完整准确
- 如果确实无法提取到学校信息，返回null

请开始详细提取："""
    
    llm_strategy = LLMExtractionStrategy(
        llm_config=LLMConfig(
            provider=LLM_MODEL,
            api_token=os.getenv(API_KEY_ENV, os.getenv("DEEPSEEK_API_KEY")),
            base_url=LLM_BASE_URL,
        ),
        schema='[{"school_name": "str", "undergraduate_majors": "int", "national_first_class_majors": "int", "provincial_first_class_majors": "int"}]',
        extraction_type="schema",
        instruction=extraction_instruction,
        
        # 启用Crawl4ai自动分块
        apply_chunking=True,
        chunk_token_threshold=6000,
        overlap_rate=0.15,
        
        input_format="markdown",
        extra_args={
            "temperature": 0.0,
            "max_tokens": 8000,
            "top_p": 0.1,
        }
    )
    print("✅ 学校简介信息提取策略创建完成")
    return llm_strategy


def validate_school_intro_data(school_data: dict, expected_school: str) -> bool:
    """
    验证提取的学校简介数据质量
    """
    if not school_data:
        return False
        
    school_name = school_data.get('school_name', '').strip()
    
    # 基本检查
    if len(school_name) < 2:
        print(f"⚠️ 学校名称过短: {school_name}")
        return False
    
    # 检查数字字段
    required_fields = ['undergraduate_majors', 'national_first_class_majors', 
                      'provincial_first_class_majors']
    
    for field in required_fields:
        value = school_data.get(field)
        if value is None:
            print(f"⚠️ 缺少字段: {field}")
            return False
            
        # 尝试转换为整数
        try:
            int_value = int(value)
            if int_value < 0:
                print(f"⚠️ 字段 {field} 不能为负数: {int_value}")
                return False
            school_data[field] = int_value  # 确保是整数类型
        except (ValueError, TypeError):
            print(f"⚠️ 字段 {field} 不是有效数字: {value} (类型: {type(value)})")
            return False
    
    # 过滤明显错误的学校名称
    invalid_patterns = [
        r'^(详情|更多|查看|点击|链接|按钮|登录|注册|首页|导航|菜单|关于我们|联系我们).*',
        r'.*\.(com|cn|org|net).*',
        r'^\d+$',  # 纯数字
        r'^(新闻|通知|公告|资讯|网站|官网).*',
        r'^(学院|专业|课程|教师|学生)$',  # 单个通用词
    ]
    
    for pattern in invalid_patterns:
        if re.match(pattern, school_name, re.IGNORECASE):
            print(f"⚠️ 学校名称格式无效: {school_name}")
            return False
    
    return True


async def crawl_single_school_intro(school_name: str, url: str) -> CrawlResult:
    """
    爬取单个学校的简介信息
    """
    print(f"\n🏫 [{school_name}] 开始爬取: {url}")
    
    # 创建session ID
    unique_timestamp = int(time.time() * 1000)
    session_id = f"school_intro_{school_name}_{unique_timestamp}"
    
    async with AsyncWebCrawler(config=get_browser_config()) as crawler:
        try:
            # 简化的等待JS代码
            simple_wait_js = """
            (async function() {
                console.log('🔄 开始等待学校简介页面加载...');
                
                // 等待页面完全加载
                await new Promise(resolve => setTimeout(resolve, 3000));
                
                // 滚动到页面底部确保所有内容可见
                window.scrollTo(0, document.body.scrollHeight);
                await new Promise(resolve => setTimeout(resolve, 1000));
                
                console.log('✅ 学校简介页面准备完成');
                return { success: true };
            })();
            """
            
            # 创建LLM策略
            print("🤖 创建LLM提取策略...")
            llm_strategy = create_school_intro_llm_strategy()
            
            # 执行爬取
            print("⚡ 开始LLM分析...")
            
            result = await crawler.arun(
                url=url,
                config=CrawlerRunConfig(
                    cache_mode=CacheMode.BYPASS,
                    session_id=session_id,
                    js_code=simple_wait_js,
                    extraction_strategy=llm_strategy,
                    delay_before_return_html=5.0,
                    wait_for_images=False,
                    page_timeout=30000,
                    override_navigator=True,
                ),
            )
            
            if not result.success:
                error_msg = f"页面加载失败: {result.error_message}"
                print(f"❌ [{school_name}] {error_msg}")
                return CrawlResult(
                    success=False,
                    school_name=school_name,
                    error_message=error_msg,
                    url=url
                )
            
            print(f"✅ [{school_name}] 页面加载成功，HTML长度: {len(result.cleaned_html):,} 字符")
            print(f"🔄  {result.extracted_content}")
            
            # 处理LLM提取结果
            print("📊 处理提取结果...")
            
            if result.extracted_content:
                try:
                    print(f"🔍 [{school_name}] LLM提取结果长度: {len(result.extracted_content):,} 字符")
                    print(f"🔍 [{school_name}] LLM提取内容预览: {result.extracted_content[:300]}...")
                    
                    # 解析LLM提取的结果
                    extracted_data = json.loads(result.extracted_content)
                    
                    # 处理不同的返回格式
                    school_data = None
                    
                    if isinstance(extracted_data, dict):
                        # 直接是字典格式
                        if 'school_name' in extracted_data:
                            school_data = extracted_data
                        else:
                            # 可能包装在其他键中
                            for key, value in extracted_data.items():
                                if isinstance(value, dict) and 'school_name' in value:
                                    school_data = value
                                    break
                    
                    elif isinstance(extracted_data, list):
                        # 是列表格式，寻找有效的字典项
                        print(f"🔍 [{school_name}] 收到列表格式结果，尝试解析...")
                        
                        for item in extracted_data:
                            if isinstance(item, dict):
                                # 跳过错误项
                                if item.get('error') == True:
                                    print(f"❌ [{school_name}] LLM返回错误: {item.get('content', 'Unknown error')}")
                                    continue
                                
                                # 检查是否包含必要字段
                                if 'school_name' in item:
                                    school_data = item
                                    print(f"✅ [{school_name}] 从列表中找到有效数据项")
                                    break
                    
                    if school_data and validate_school_intro_data(school_data, school_name):
                        school_intro = SchoolIntroData(
                            school_name=school_data['school_name'].strip(),
                            undergraduate_majors=school_data['undergraduate_majors'],
                            national_first_class_majors=school_data['national_first_class_majors'],
                            provincial_first_class_majors=school_data['provincial_first_class_majors'],
                            source_url=url,
                            crawl_timestamp=datetime.now().isoformat()
                        )
                        
                        print(f"✅ [{school_name}] 数据提取成功: {school_intro.school_name}")
                        print(f"  📚 本科专业({school_intro.undergraduate_majors}) 国家级一流专业({school_intro.national_first_class_majors}) 省级一流专业({school_intro.provincial_first_class_majors}) ")
                        
                        return CrawlResult(
                            success=True,
                            school_name=school_name,
                            data=school_intro,
                            url=url
                        )
                    else:
                        error_msg = "数据验证失败或无法解析"
                        print(f"❌ [{school_name}] {error_msg}")
                        if school_data:
                            print(f"提取的数据: {school_data}")
                        return CrawlResult(
                            success=False,
                            school_name=school_name,
                            error_message=error_msg,
                            url=url
                        )
                        
                except json.JSONDecodeError as e:
                    error_msg = f"JSON解析失败: {e}"
                    print(f"❌ [{school_name}] {error_msg}")
                    print(f"原始提取内容: {result.extracted_content[:500]}...")
                    return CrawlResult(
                        success=False,
                        school_name=school_name,
                        error_message=error_msg,
                        url=url
                    )
                    
            else:
                error_msg = "LLM未提取到任何内容"
                print(f"❌ [{school_name}] {error_msg}")
                return CrawlResult(
                    success=False,
                    school_name=school_name,
                    error_message=error_msg,
                    url=url
                )
            
        except Exception as e:
            error_msg = f"爬取异常: {str(e)}"
            print(f"❌ [{school_name}] {error_msg}")
            import traceback
            traceback.print_exc()
            return CrawlResult(
                success=False,
                school_name=school_name,
                error_message=error_msg,
                url=url
            )


async def crawl_multiple_school_intros(school_websites: Dict[str, str] = None) -> List[CrawlResult]:
    """
    批量爬取学校简介信息
    """
    if school_websites is None:
        school_websites = SCHOOL_WEBSITES
    
    print(f"\n{'='*80}")
    print(f"🏫 开始批量爬取学校简介信息")
    print(f"🎯 目标学校数量: {len(school_websites)}")
    print(f"🤖 策略：页面加载 + LLM分析")
    print(f"🔄 爬取间隔: {CRAWL_INTERVAL}秒")
    print(f"{'='*80}")
    
    if not school_websites:
        print("❌ 没有配置要爬取的学校网址")
        return []
    
    results = []
    
    for i, (school_name, url) in enumerate(school_websites.items(), 1):
        print(f"\n📍 [{i}/{len(school_websites)}] 处理学校: {school_name}")
        
        # 确保URL格式正确
        if not url.startswith('http'):
            url = f"https://{url}"
        
        # 爬取单个学校
        result = await crawl_single_school_intro(school_name, url)
        results.append(result)
        
        # 显示进度
        success_count = sum(1 for r in results if r.success)
        print(f"📊 [{i}/{len(school_websites)}] 当前成功率: {success_count}/{i} ({success_count/i*100:.1f}%)")
        
        # 添加间隔，避免请求过于频繁
        if i < len(school_websites):
            print(f"⏳ 等待 {CRAWL_INTERVAL} 秒...")
            await asyncio.sleep(CRAWL_INTERVAL)
    
    # 结果统计
    total_count = len(results)
    success_count = sum(1 for r in results if r.success)
    failed_count = total_count - success_count
    
    print(f"\n🎉 学校简介信息爬取完成!")
    print(f"{'='*60}")
    print(f"📊 总体统计:")
    print(f"  🏫 目标学校数量: {total_count}")
    print(f"  ✅ 成功提取数量: {success_count}")
    print(f"  ❌ 失败数量: {failed_count}")
    if total_count > 0:
        print(f"  📈 成功率: {success_count/total_count*100:.1f}%")
    
    # 成功的学校
    successful_schools = [r for r in results if r.success]
    if successful_schools:
        print(f"\n✅ 成功提取的学校:")
        for result in successful_schools:
            print(f"  🏫 {result.data.school_name if result.data else result.school_name}")
    
    # 失败的学校
    failed_schools = [r for r in results if not r.success]
    if failed_schools:
        print(f"\n❌ 提取失败的学校:")
        for result in failed_schools:
            print(f"  🏫 {result.school_name}: {result.error_message}")
    
    return results


# 便捷函数：从配置文件读取URL列表并爬取
async def crawl_configured_school_intros() -> List[CrawlResult]:
    """
    从配置文件读取URL列表并爬取学校简介信息
    """
    return await crawl_multiple_school_intros(SCHOOL_WEBSITES)