import asyncio
import os
import json
import re
import time
from typing import List

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode, LLMConfig
from crawl4ai.extraction_strategy import LLMExtractionStrategy

from models.course_data import ProvincialCourseData
from config import *


def get_browser_config() -> BrowserConfig:
    """
    获取浏览器配置
    """
    print("🔧 配置浏览器参数...")
    config = BrowserConfig(
        browser_type="chromium",
        headless=False,
        verbose=True,
    )
    print("✅ 浏览器配置完成")
    return config


def create_provincial_course_llm_strategy() -> LLMExtractionStrategy:
    """
    创建省级一流课程数据提取的LLM策略
    """
    print("🤖 创建省级一流课程数据提取策略...")
    
    extraction_instruction = """你是专业的教育数据提取专家。请从以下网页内容中提取各个学校的省级一流课程数据。

**严格提取要求：**
1. 仔细分析整个内容，提取每个学校的省级一流课程统计数据
2. 学校名称：完整的大学名称（如"北京大学"、"清华大学"等）
3. 第一批数量：该学校省级一流课程第一批的数量（整数）
4. 第二批数量：该学校省级一流课程第二批的数量（整数）
5. 第三批数量：该学校省级一流课程第三批的数量（整数）
6. 合计数量：该学校省级一流课程的总数量（整数）
7. 确保不遗漏任何学校的数据，但避免重复提取
8. 忽略导航菜单、广告、页脚等无关内容

**输出格式（严格JSON数组）：**
[
  {"school": "学校名称", "first": 第一批数量, "second": 第二批数量, "third": 第三批数量, "total": 合计数量},
  {"school": "学校名称", "first": 第一批数量, "second": 第二批数量, "third": 第三批数量, "total": 合计数量}
]

**重要说明：**
- 数字字段(first, second, third, total)必须是整数类型，不能是字符串
- 如果某批次数量为0，请填写0而不是省略
- 确保total等于first + second + third的和
- 如果确实没有找到相关数据，返回空数组 []
- 不要猜测或推断信息，只提取明确显示的内容

请开始详细提取："""
    
    llm_strategy = LLMExtractionStrategy(
        llm_config=LLMConfig(
            provider=LLM_MODEL,
            api_token=os.getenv(API_KEY_ENV, os.getenv("DEEPSEEK_API_KEY")),
            base_url=LLM_BASE_URL,
        ),
        schema='[{"school": "str", "first": "int", "second": "int", "third": "int", "total": "int"}]',
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
    
    print("✅ 省级一流课程LLM策略创建完成")
    return llm_strategy


def validate_course_data(course_data: dict) -> bool:
    """
    验证提取的省级课程数据质量
    """
    school_name = course_data.get('school', '').strip()
    
    # 基本检查
    if len(school_name) < 2:
        return False
    
    # 检查数字字段
    required_fields = ['first', 'second', 'third', 'total']
    for field in required_fields:
        value = course_data.get(field)
        if not isinstance(value, int) or value < 0:
            print(f"⚠️ 字段 {field} 验证失败: {value}")
            return False
    
    # 检查总数是否合理（允许一定误差）
    calculated_total = course_data['first'] + course_data['second'] + course_data['third']
    actual_total = course_data['total']
    
    if abs(calculated_total - actual_total) > 5:  # 允许5个课程的误差
        print(f"⚠️ {school_name} 总数验证失败: 计算值({calculated_total}) vs 实际值({actual_total})")
        return False
    
    # 过滤明显错误的学校名称
    invalid_patterns = [
        r'^(详情|更多|查看|点击|链接|按钮|登录|注册|首页|导航|菜单|合计|总计|小计).*',
        r'.*\.(com|cn|org|net).*',
        r'^\d+$',  # 纯数字
    ]
    
    for pattern in invalid_patterns:
        if re.match(pattern, school_name, re.IGNORECASE):
            return False
    
    return True


async def crawl_provincial_course_data(target_url: str) -> List[ProvincialCourseData]:
    """
    爬取省级一流课程数据
    """
    print(f"\n{'='*80}")
    print(f"🏫 开始爬取省级一流课程数据")
    print(f"🎯 目标URL: {target_url}")
    print(f"🤖 策略：简单页面加载 + Crawl4ai自动分块 + LLM分析")
    print(f"{'='*80}")
    
    # 创建session ID
    unique_timestamp = int(time.time() * 1000)
    session_id = f"provincial_courses_{unique_timestamp}"
    print(f"🆔 Session ID: {session_id}")
    
    async with AsyncWebCrawler(config=get_browser_config()) as crawler:
        try:
            print("🚀 加载页面...")
            
            # 简单的等待JS代码
            simple_wait_js = """
            (async function() {
                console.log('🔄 开始等待页面内容加载...');
                console.log('📍 当前URL:', window.location.href);
                console.log('📄 页面标题:', document.title);
                
                // 等待页面完全加载
                await new Promise(resolve => setTimeout(resolve, 8000));
                
                const divCount = document.querySelectorAll('div').length;
                console.log(`📊 页面包含 ${divCount} 个div元素`);
                
                // 滚动到页面底部确保所有内容可见
                window.scrollTo(0, document.body.scrollHeight);
                await new Promise(resolve => setTimeout(resolve, 3000));
                
                console.log('✅ 页面内容准备完成');
                
                return {
                    success: true,
                    elements: divCount,
                    message: '省级课程数据页面已准备就绪'
                };
            })();
            """
            
            # 创建LLM策略
            print("🤖 创建LLM提取策略...")
            llm_strategy = create_provincial_course_llm_strategy()
            
            # 执行爬取
            print("⚡ 开始LLM分析...")
            
            result = await crawler.arun(
                url=target_url,
                config=CrawlerRunConfig(
                    cache_mode=CacheMode.BYPASS,
                    session_id=session_id,
                    js_code=simple_wait_js,
                    extraction_strategy=llm_strategy,
                    delay_before_return_html=15.0,  # 简化等待时间
                    wait_for_images=False,
                    page_timeout=60000,  # 1分钟超时
                    override_navigator=True,
                ),
            )
            
            if not result.success:
                print(f"❌ 页面加载失败: {result.error_message}")
                return []
            
            print(f"✅ 页面加载成功，HTML长度: {len(result.cleaned_html):,} 字符")
            
            # 处理LLM提取结果
            print("📊 处理提取结果...")
            
            if result.extracted_content:
                try:
                    print(f"🔍 LLM提取结果长度: {len(result.extracted_content):,} 字符")
                    print(f"🔍 LLM提取内容预览: {result.extracted_content[:200]}...")
                    
                    # 解析LLM提取的结果
                    extracted_data = json.loads(result.extracted_content)
                    
                    # 确保结果是列表格式
                    if isinstance(extracted_data, dict):
                        if 'data' in extracted_data:
                            course_list = extracted_data['data']
                        else:
                            for value in extracted_data.values():
                                if isinstance(value, list):
                                    course_list = value
                                    break
                            else:
                                course_list = []
                    elif isinstance(extracted_data, list):
                        course_list = extracted_data
                    else:
                        print(f"⚠️ 意外的LLM返回格式: {type(extracted_data)}")
                        course_list = []
                    
                    print(f"📋 解析得到 {len(course_list)} 个学校数据条目")
                    
                    # 处理提取的课程数据
                    all_courses = []
                    for i, course_data in enumerate(course_list):
                        if isinstance(course_data, dict):
                            school_name = course_data.get('school', '').strip()
                            first = course_data.get('first', 0)
                            second = course_data.get('second', 0)
                            third = course_data.get('third', 0)
                            total = course_data.get('total', 0)
                            
                            # 验证数据质量
                            if school_name:
                                if validate_course_data(course_data):
                                    course = ProvincialCourseData(
                                        school=school_name,
                                        first=first,
                                        second=second,
                                        third=third,
                                        total=total
                                    )
                                    all_courses.append(course)
                                    print(f"  ✅ 提取 {i+1}: {school_name} - 第一批({first}) 第二批({second}) 第三批({third}) 合计({total})")
                                else:
                                    print(f"  ❌ 验证失败 {i+1}: {school_name}")
                            else:
                                print(f"  ⚠️ 数据不完整 {i+1}: {course_data}")
                    
                    # 去重处理
                    unique_courses = []
                    seen_schools = set()
                    
                    for course in all_courses:
                        school_key = course.school.strip().lower()
                        if school_key not in seen_schools:
                            seen_schools.add(school_key)
                            unique_courses.append(course)
                        else:
                            print(f"🔄 去重: {course.school}")
                    
                    print(f"🎉 省级课程数据提取完成!")
                    print(f"  🏫 提取学校总数: {len(all_courses)}")
                    print(f"  ✨ 去重后学校数: {len(unique_courses)}")
                    
                    # 显示样例
                    if unique_courses:
                        print("🏫 提取的学校数据样例:")
                        for i, course in enumerate(unique_courses[:10], 1):
                            print(f"  {i}. {course}")
                        if len(unique_courses) > 10:
                            print(f"  ... 还有 {len(unique_courses) - 10} 所学校")
                    
                    return unique_courses
                    
                except json.JSONDecodeError as e:
                    print(f"❌ JSON解析失败: {e}")
                    print(f"原始提取内容: {result.extracted_content[:1000]}...")
                    return []
                    
            else:
                print("❌ LLM未提取到任何内容")
                return []
            
        except Exception as e:
            print(f"❌ 省级课程数据爬取异常: {e}")
            import traceback
            traceback.print_exc()
            return []