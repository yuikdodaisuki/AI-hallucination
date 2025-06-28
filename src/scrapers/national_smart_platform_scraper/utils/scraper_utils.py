import asyncio
import os
import json
import re
import tempfile
import time
from typing import List, Optional, Tuple
from urllib.parse import quote
from pydantic import BaseModel, Field

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode, LLMConfig, CrawlResult
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from crawl4ai import *

from models.course import Course
from config import *


def get_browser_config() -> BrowserConfig:
    """
    获取浏览器配置
    """
    print("🔧 配置浏览器参数...")
    config = BrowserConfig(
        browser_type="chromium",
        headless=False,  # 设为False便于调试观察
        verbose=True,
    )
    print("✅ 浏览器配置完成")
    return config


def build_school_search_url(school_name: str) -> str:
    """
    构建学校搜索URL
    """
    encoded_school = quote(school_name)
    return SEARCH_URL_TEMPLATE.format(school_name=encoded_school)


def create_auto_chunking_llm_strategy(school_name: str) -> LLMExtractionStrategy:
    """
    🔥 创建完全使用Crawl4ai自动分块的LLM策略
    """
    print("🤖 创建自动分块LLM提取策略...")
    
    extraction_instruction = f"""你是专业的课程信息提取专家。请从以下"{school_name}"的网页内容中提取所有课程信息。

**严格提取要求：**
1. 仔细分析整个内容，提取每一门具体课程及其对应教师
2. 课程名称：具体的学科名称（如"高等数学"、"大学英语"、"程序设计"等）
3. 教师姓名：真实的人名（2-4个中文字符或完整英文姓名）
4. 确保不遗漏任何课程信息，但避免重复提取
5. 忽略导航菜单、广告、页脚等无关内容

**输出格式（严格JSON数组）：**
[
  {{"school": "{school_name}", "course": "课程名称", "teacher": "教师姓名"}},
  {{"school": "{school_name}", "course": "课程名称", "teacher": "教师姓名"}}
]

**重要说明：**
- 这可能是内容片段，请提取片段中的所有完整课程信息
- 如果确实没有明确的课程-教师对应关系，返回空数组 []
- 不要猜测或推断信息，只提取明确显示的内容
- 确保每个course和teacher字段都有实际内容且非空

请开始详细提取："""
    
    llm_strategy = LLMExtractionStrategy(
        llm_config=LLMConfig(
            provider=LLM_MODEL,
            api_token=os.getenv(API_KEY_ENV, os.getenv("DEEPSEEK_API_KEY")),
            base_url=LLM_BASE_URL,
        ),
        schema=f'[{{"school": "{school_name}", "course": "str", "teacher": "str"}}]',
        extraction_type="schema",
        instruction=extraction_instruction,
        
        # 🔥 核心：启用Crawl4ai自动分块
        apply_chunking=True,           # 启用自动分块
        chunk_token_threshold=6000,    # 6000 tokens 的分块大小
        overlap_rate=0.15,             # 15% 重叠率，防止课程信息丢失
        
        input_format="markdown",
        extra_args={
            "temperature": 0.0,        # 确保输出稳定
            "max_tokens": 8000,        # 足够的输出空间
            "top_p": 0.1,              # 减少随机性
        }
    )
    
    print("✅ 自动分块LLM策略创建完成")
    return llm_strategy


def validate_course_data(course_data: dict) -> bool:
    """
    🔍 验证提取的课程数据质量
    """
    course_name = course_data.get('course', '').strip()
    teacher_name = course_data.get('teacher', '').strip()
    
    # 基本长度检查
    if len(course_name) < 2 or len(teacher_name) < 2:
        return False
    
    # 过滤明显错误的课程名称
    invalid_course_patterns = [
        r'^(详情|更多|查看|点击|链接|按钮|登录|注册|首页|导航|菜单).*',
        r'.*\.(com|cn|org|net).*',
        r'^\d+$',  # 纯数字
        r'^(null|undefined|none|暂无|待定|tbd).*'
    ]
    
    for pattern in invalid_course_patterns:
        if re.match(pattern, course_name, re.IGNORECASE):
            return False
    
    # 过滤明显错误的教师名称
    invalid_teacher_patterns = [
        r'^(详情|更多|查看|点击|链接|按钮|学校|学院|系|部门).*',
        r'.*\.(com|cn|org|net).*',
        r'^\d+$',  # 纯数字
        r'^(null|undefined|none|暂无|待定|tbd).*'
    ]
    
    for pattern in invalid_teacher_patterns:
        if re.match(pattern, teacher_name, re.IGNORECASE):
            return False
    
    # 检查是否是合理的姓名格式
    # 中文姓名：2-4个中文字符
    # 英文姓名：字母、空格、点号组合
    chinese_name_pattern = r'^[\u4e00-\u9fa5]{2,4}$'
    english_name_pattern = r'^[A-Za-z\s\.]{2,30}$'
    mixed_name_pattern = r'^[\u4e00-\u9fa5A-Za-z\s\.]{2,10}$'
    
    if not (re.match(chinese_name_pattern, teacher_name) or 
            re.match(english_name_pattern, teacher_name) or
            re.match(mixed_name_pattern, teacher_name)):
        return False
    
    return True


async def crawl_school_courses_with_auto_chunking(
    school_name: str,
    session_id: str
) -> List[Course]:
    """
    🔥 完全使用 Crawl4ai 自动分块的课程提取
    """
    print(f"\n{'='*80}")
    print(f"🏫 开始自动分块爬取: {school_name}")
    print(f"🤖 策略：完整页面加载 + Crawl4ai自动分块 + LLM分析")
    print(f"{'='*80}")
    
    search_url = build_school_search_url(school_name)
    print(f"🔗 搜索URL: {search_url}")
    
    # 创建独立的session ID
    unique_timestamp = int(time.time() * 1000)
    school_session_id = f"{session_id}_{school_name.replace(' ', '_').replace('/', '_').replace('（', '_').replace('）', '_')}_{unique_timestamp}"
    print(f"🆔 Session ID: {school_session_id}")
    
    async with AsyncWebCrawler(config=get_browser_config()) as crawler:
        try:
            # 🔥 第一步：完整页面加载
            print("🚀 第一步：加载完整页面内容...")
            
            load_and_extract_js = f"""
            (async function() {{
                console.log('🔄 开始自动分块数据加载流程...');
                
                let loadMoreAttempts = 0;
                let maxAttempts = {MAX_SCROLL_ATTEMPTS};
                let scrollDelay = {SCROLL_DELAY * 1000};
                let loadMoreDelay = {LOAD_MORE_DELAY * 1000};
                
                console.log('📍 当前URL:', window.location.href);
                console.log('📄 页面标题:', document.title);
                
                // 等待页面完全加载
                console.log('⏳ 等待页面完全加载...');
                await new Promise(resolve => setTimeout(resolve, 8000));
                
                const initialDivCount = document.querySelectorAll('div').length;
                console.log(`📊 初始页面元素: ${{initialDivCount}} 个div`);
                
                // 数据加载循环
                const buttonSelectors = [
                    'button.text-white.bg-blue-600',
                    'button[class*="bg-blue-600"]',
                    'button[class*="text-white"]',
                    'button[class*="btn"]',
                    'button[class*="load"]',
                    'button[class*="more"]',
                    'a[class*="load"]',
                    'a[class*="more"]',
                    'button',
                    '.load-more',
                    '.loadmore',
                    '.show-more',
                    '[role="button"]'
                ];
                
                const loadMoreTexts = [
                    '加载更多', '更多', 'load more', '查看更多', 
                    '显示更多', 'show more', '继续加载', 
                    'continue', '下一页', 'next', '展开',
                    'expand', '全部', 'all', '更多课程'
                ];
                
                while (loadMoreAttempts < maxAttempts) {{
                    console.log(`🔄 第 ${{loadMoreAttempts + 1}} 次加载尝试`);
                    
                    // 滚动策略
                    const scrollSteps = 5;
                    for (let step = 0; step < scrollSteps; step++) {{
                        const targetY = (document.body.scrollHeight / scrollSteps) * (step + 1);
                        window.scrollTo({{ top: targetY, behavior: 'smooth' }});
                        await new Promise(resolve => setTimeout(resolve, 1000));
                    }}
                    
                    window.scrollTo({{ top: document.body.scrollHeight, behavior: 'smooth' }});
                    await new Promise(resolve => setTimeout(resolve, scrollDelay));
                    
                    // 智能按钮查找
                    let loadMoreButton = null;
                    
                    for (let selector of buttonSelectors) {{
                        try {{
                            const buttons = document.querySelectorAll(selector);
                            for (let btn of buttons) {{
                                const text = (btn.textContent || btn.innerText || '').trim().toLowerCase();
                                const isVisible = btn.offsetParent !== null && 
                                                window.getComputedStyle(btn).display !== 'none' &&
                                                window.getComputedStyle(btn).visibility !== 'hidden';
                                const isEnabled = !btn.disabled && !btn.classList.contains('disabled');
                                
                                const isLoadMore = loadMoreTexts.some(loadText => 
                                    text.includes(loadText.toLowerCase())
                                );
                                
                                if (isLoadMore && isVisible && isEnabled) {{
                                    loadMoreButton = btn;
                                    console.log(`🎯 找到加载按钮: "${{btn.textContent?.trim()}}" (选择器: ${{selector}})`);
                                    break;
                                }}
                            }}
                            if (loadMoreButton) break;
                        }} catch (e) {{
                            // 忽略选择器错误，继续尝试下一个
                        }}
                    }}
                    
                    if (loadMoreButton) {{
                        try {{
                            console.log('🔘 准备点击加载按钮...');
                            
                            // 确保按钮可见
                            loadMoreButton.scrollIntoView({{ 
                                behavior: 'smooth', 
                                block: 'center',
                                inline: 'center'
                            }});
                            await new Promise(resolve => setTimeout(resolve, 3000));
                            
                            const beforeClickElements = document.querySelectorAll('div').length;
                            
                            // 多种点击方式
                            let clickSuccess = false;
                            
                            // 方式1：直接点击
                            try {{
                                loadMoreButton.click();
                                clickSuccess = true;
                                console.log('✅ 直接点击成功');
                            }} catch (e) {{
                                console.log('⚠️ 直接点击失败，尝试事件触发');
                                
                                // 方式2：事件触发
                                try {{
                                    const clickEvent = new MouseEvent('click', {{
                                        bubbles: true,
                                        cancelable: true,
                                        view: window
                                    }});
                                    loadMoreButton.dispatchEvent(clickEvent);
                                    clickSuccess = true;
                                    console.log('✅ 事件触发点击成功');
                                }} catch (e2) {{
                                    console.log('❌ 所有点击方式都失败');
                                }}
                            }}
                            
                            if (clickSuccess) {{
                                console.log('🕐 等待内容加载...');
                                await new Promise(resolve => setTimeout(resolve, loadMoreDelay));
                                
                                const afterClickElements = document.querySelectorAll('div').length;
                                const addedElements = afterClickElements - beforeClickElements;
                                
                                console.log(`📈 点击后元素变化: ${{beforeClickElements}} -> ${{afterClickElements}} (+${{addedElements}})`);
                                
                                if (addedElements <= 0) {{
                                    console.log('⚠️ 没有新增内容，可能已全部加载');
                                    break;
                                }}
                            }} else {{
                                console.log('❌ 所有点击方式都失败');
                                break;
                            }}
                            
                            loadMoreAttempts++;
                        }} catch (error) {{
                            console.log('❌ 点击按钮过程中出错:', error);
                            break;
                        }}
                    }} else {{
                        console.log('✅ 未找到更多加载按钮，数据可能已全部加载');
                        break;
                    }}
                    
                    await new Promise(resolve => setTimeout(resolve, 2000));
                }}
                
                const finalDivCount = document.querySelectorAll('div').length;
                console.log(`📊 数据加载完成统计:`);
                console.log(`  初始元素: ${{initialDivCount}}`);
                console.log(`  最终元素: ${{finalDivCount}}`);
                console.log(`  总共加载: ${{finalDivCount - initialDivCount}} 个元素`);
                console.log(`  加载尝试次数: ${{loadMoreAttempts}}`);
                
                // 最终确保页面内容完全可见
                window.scrollTo(0, 0);
                await new Promise(resolve => setTimeout(resolve, 2000));
                window.scrollTo(0, document.body.scrollHeight);
                await new Promise(resolve => setTimeout(resolve, 4000));
                
                console.log('🎉 页面完整性加载完成，准备自动分块LLM分析');
                
                return {{
                    success: true,
                    loadAttempts: loadMoreAttempts,
                    initialElements: initialDivCount,
                    finalElements: finalDivCount,
                    elementsAdded: finalDivCount - initialDivCount,
                    message: '页面内容已全部加载，准备自动分块提取'
                }};
            }})();
            """
            
            # 🔥 第二步：创建自动分块LLM策略
            print("🤖 第二步：创建自动分块LLM策略...")
            llm_strategy = create_auto_chunking_llm_strategy(school_name)
            
            # 🔥 第三步：直接使用自动分块进行LLM分析
            print("⚡ 第三步：使用Crawl4ai自动分块进行LLM分析...")
            
            result = await crawler.arun(
                url=search_url,
                config=CrawlerRunConfig(
                    cache_mode=CacheMode.BYPASS,
                    session_id=school_session_id,
                    js_code=load_and_extract_js,
                    
                    # 🔥 关键：添加自动分块LLM策略
                    extraction_strategy=llm_strategy,
                    
                    delay_before_return_html=180.0,
                    wait_for_images=False,
                    page_timeout=150000,  # 增加超时时间到2.5分钟
                    override_navigator=True,
                ),
            )
            
            if not result.success:
                print(f"❌ 页面加载失败: {result.error_message}")
                return []
            
            print(f"✅ 页面加载成功，HTML长度: {len(result.cleaned_html):,} 字符")
            
            # 🔥 第四步：处理自动分块LLM提取结果
            print("📊 第四步：处理自动分块LLM提取结果...")
            
            if result.extracted_content:
                try:
                    print(f"🔍 LLM提取原始结果长度: {len(result.extracted_content):,} 字符")
                    print(f"🔍 LLM提取内容预览: {result.extracted_content[:200]}...")
                    
                    # 解析LLM提取的结果
                    extracted_data = json.loads(result.extracted_content)
                    
                    # 确保结果是列表格式
                    if isinstance(extracted_data, dict):
                        if 'courses' in extracted_data:
                            course_list = extracted_data['courses']
                        elif 'data' in extracted_data:
                            course_list = extracted_data['data']
                        else:
                            # 可能是其他包装格式，尝试获取第一个列表值
                            for value in extracted_data.values():
                                if isinstance(value, list):
                                    course_list = value
                                    break
                            else:
                                print(f"⚠️ 无法识别的提取结果格式: {extracted_data}")
                                course_list = []
                    elif isinstance(extracted_data, list):
                        course_list = extracted_data
                    else:
                        print(f"⚠️ 意外的LLM返回格式: {type(extracted_data)}")
                        course_list = []
                    
                    print(f"📋 解析得到 {len(course_list)} 个课程条目")
                    
                    # 🔥 处理提取的课程数据
                    all_courses = []
                    for i, course_data in enumerate(course_list):
                        if isinstance(course_data, dict):
                            course_name = course_data.get('course', '').strip()
                            teacher = course_data.get('teacher', '').strip()
                            
                            # 验证数据质量
                            if course_name and teacher:
                                if validate_course_data(course_data):
                                    course = Course(
                                        school=school_name,
                                        course_name=course_name,
                                        teacher=teacher
                                    )
                                    all_courses.append(course)
                                    print(f"  ✅ 提取 {i+1}: {course_name} - {teacher}")
                                else:
                                    print(f"  ❌ 验证失败 {i+1}: {course_name} - {teacher}")
                            else:
                                print(f"  ⚠️ 数据不完整 {i+1}: course='{course_name}', teacher='{teacher}'")
                        else:
                            print(f"  ⚠️ 非字典格式的数据 {i+1}: {course_data}")
                    
                    # 🔥 去重处理
                    unique_courses = []
                    seen_courses = set()
                    
                    for course in all_courses:
                        course_key = f"{course.course_name.strip().lower()}_{course.teacher.strip().lower()}"
                        if course_key not in seen_courses:
                            seen_courses.add(course_key)
                            unique_courses.append(course)
                        else:
                            print(f"🔄 去重: {course.course_name} - {course.teacher}")
                    
                    print(f"🎉 自动分块LLM分析完成!")
                    print(f"  📚 提取课程总数: {len(all_courses)}")
                    print(f"  ✨ 去重后课程数: {len(unique_courses)}")
                    
                    # 显示样例
                    if unique_courses:
                        print("📚 提取的课程样例:")
                        for i, course in enumerate(unique_courses[:15], 1):
                            print(f"  {i}. {course.course_name} - {course.teacher}")
                        if len(unique_courses) > 15:
                            print(f"  ... 还有 {len(unique_courses) - 15} 门课程")
                    else:
                        print("⚠️ 去重后没有有效课程")
                        
                        # 如果没有结果，保存原始HTML用于调试
                        debug_file = f"debug_no_results_{school_name}_{int(time.time())}.html"
                        with open(debug_file, 'w', encoding='utf-8') as f:
                            f.write(result.cleaned_html)
                        print(f"🔍 原始HTML已保存到: {debug_file}")
                        
                        debug_extract_file = f"debug_extract_{school_name}_{int(time.time())}.json"
                        with open(debug_extract_file, 'w', encoding='utf-8') as f:
                            f.write(result.extracted_content)
                        print(f"🔍 LLM提取结果已保存到: {debug_extract_file}")
                    
                    # 🔥 显示LLM使用统计
                    try:
                        if hasattr(llm_strategy, 'show_usage'):
                            llm_strategy.show_usage()
                    except Exception as e:
                        print(f"📊 LLM使用统计获取失败: {e}")
                    
                    return unique_courses
                    
                except json.JSONDecodeError as e:
                    print(f"❌ JSON解析失败: {e}")
                    print(f"原始提取内容: {result.extracted_content[:1000]}...")
                    
                    # 保存解析失败的内容用于调试
                    error_file = f"debug_json_error_{school_name}_{int(time.time())}.txt"
                    with open(error_file, 'w', encoding='utf-8') as f:
                        f.write(f"JSON解析错误: {e}\n\n")
                        f.write(f"原始提取内容:\n{result.extracted_content}")
                    print(f"🔍 解析错误详情已保存到: {error_file}")
                    
                    return []
                    
            else:
                print("❌ LLM未提取到任何内容")
                
                # 保存原始HTML用于调试
                debug_file = f"debug_empty_extract_{school_name}_{int(time.time())}.html"
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write(result.cleaned_html)
                print(f"🔍 原始HTML已保存到: {debug_file}")
                
                return []
            
        except Exception as e:
            print(f"❌ {school_name} 自动分块爬取异常: {e}")
            import traceback
            traceback.print_exc()
            return []


# 🔥 主要函数：爬取单个学校的课程信息
async def crawl_school_courses(
    school_name: str,
    session_id: str
) -> List[Course]:
    """
    爬取单个学校的所有课程信息 - 使用自动分块
    """
    print(f"🎯 开始爬取学校: {school_name}")
    print(f"🆔 Session ID: {session_id}")
    
    try:
        return await crawl_school_courses_with_auto_chunking(school_name, session_id)
    except Exception as e:
        print(f"❌ 爬取 {school_name} 异常: {e}")
        import traceback
        traceback.print_exc()
        return []


# 🔥 多学校爬取函数
async def crawl_multiple_schools_with_recovery(
    school_names: List[str],
    session_base_id: str = "multi_school_auto"
) -> dict:
    """
    🏫 爬取多个学校的课程信息 - 使用自动分块
    """
    results = {}
    
    for i, school_name in enumerate(school_names):
        print(f"\n🎯 处理学校 {i+1}/{len(school_names)}: {school_name}")
        
        max_retries = 2
        for retry in range(max_retries):
            try:
                # 每个学校使用独立的session
                session_id = f"{session_base_id}_{i}_{int(time.time())}"
                
                courses = await crawl_school_courses_with_auto_chunking(school_name, session_id)
                
                results[school_name] = courses
                print(f"✅ {school_name}: 成功获取 {len(courses)} 门课程")
                
                # 成功后稍作休息，避免过于频繁的请求
                await asyncio.sleep(3)
                break
                
            except Exception as e:
                print(f"❌ {school_name} 第 {retry+1} 次尝试失败: {e}")
                
                if retry < max_retries - 1:
                    print(f"🔄 {school_name} 将进行第 {retry+2} 次重试...")
                    await asyncio.sleep(5)
                else:
                    print(f"💀 {school_name}: 所有重试均失败")
                    results[school_name] = []
    
    return results


# 🔥 测试函数
async def test_auto_chunking_extraction(
    school_name: str,
    session_id: str
) -> None:
    """
    测试自动分块LLM提取功能
    """
    print(f"🧪 开始测试自动分块提取功能: {school_name}")
    
    courses = await crawl_school_courses_with_auto_chunking(school_name, session_id)
    
    print(f"\n{'='*50}")
    print(f"📊 测试结果统计:")
    print(f"  学校: {school_name}")
    print(f"  提取课程数: {len(courses)}")
    print(f"{'='*50}")
    
    if courses:
        print("📝 提取的课程详情:")
        for i, course in enumerate(courses[:20], 1):  # 显示前20个
            print(f"  {i}. {course.course_name} - {course.teacher}")
        if len(courses) > 20:
            print(f"  ... 还有 {len(courses) - 20} 门课程")
    else:
        print("⚠️ 未提取到任何课程")


# 🔥 调试函数
async def debug_page_structure(
    url: str,
    session_id: str
) -> None:
    """
    调试页面结构，查看实际的HTML内容
    """
    print(f"🔍 开始调试页面结构: {url}")
    
    debug_js = """
    (async function() {
        console.log('🔍 开始页面结构调试...');
        
        await new Promise(resolve => setTimeout(resolve, 5000));
        
        // 统计各种元素
        const stats = {
            'total_divs': document.querySelectorAll('div').length,
            'course_keywords': document.body.textContent.toLowerCase().split('课程').length - 1,
            'teacher_keywords': document.body.textContent.toLowerCase().split('教师').length - 1,
            'articles': document.querySelectorAll('article').length,
            'sections': document.querySelectorAll('section').length,
            'lists': document.querySelectorAll('ul, ol').length,
            'buttons': document.querySelectorAll('button').length,
            'text_length': document.body.textContent.length
        };
        
        console.log('📊 页面元素统计:', stats);
        
        return { success: true, stats: stats };
    })();
    """
    
    async with AsyncWebCrawler(config=get_browser_config()) as crawler:
        try:
            result = await crawler.arun(
                url=url,
                config=CrawlerRunConfig(
                    cache_mode=CacheMode.BYPASS,
                    session_id=session_id,
                    js_code=debug_js,
                    delay_before_return_html=15.0,
                ),
            )
            
            if result.success:
                print("✅ 页面结构调试完成")
                
                # 保存HTML到文件用于分析
                debug_file = f"debug_structure_{session_id}.html"
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write(result.cleaned_html)
                print(f"📁 页面HTML已保存到: {debug_file}")
                
                # 分析页面内容
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(result.cleaned_html, 'html.parser')
                text = soup.get_text()
                
                course_count = text.lower().count('课程')
                teacher_count = text.lower().count('教师') + text.lower().count('讲师') + text.lower().count('老师')
                
                print(f"📊 页面内容分析:")
                print(f"  课程相关词汇出现次数: {course_count}")
                print(f"  教师相关词汇出现次数: {teacher_count}")
                print(f"  页面文本长度: {len(text):,} 字符")
                
            else:
                print(f"❌ 页面结构调试失败: {result.error_message}")
                
        except Exception as e:
            print(f"❌ 调试异常: {e}")


# 🔥 兼容性函数（如果有其他地方调用旧版本函数）
async def crawl_school_courses_with_llm(
    school_name: str,
    session_id: str
) -> List[Course]:
    """
    兼容旧版本的函数名 - 重定向到自动分块版本
    """
    print("⚠️ 检测到旧版本函数调用，重定向到自动分块版本")
    return await crawl_school_courses_with_auto_chunking(school_name, session_id)


# 废弃的函数（保留以防其他地方调用）
def smart_chunk_content(html_content: str, chunk_size: int = 20000) -> List[str]:
    """
    ⚠️ 此函数已废弃，现在使用Crawl4ai自动分块
    """
    print("⚠️ 警告：手动智能分片已废弃，现在使用Crawl4ai自动分块")
    return []


def create_llm_extraction_strategy(school_name: str):
    """
    ⚠️ 此函数已废弃，现在使用create_auto_chunking_llm_strategy
    """
    print("⚠️ 警告：旧版LLM策略已废弃，重定向到自动分块版本")
    return create_auto_chunking_llm_strategy(school_name)


async def process_chunk_with_llm(*args, **kwargs):
    """
    ⚠️ 此函数已废弃，现在使用Crawl4ai自动分块
    """
    print("⚠️ 警告：手动分片处理已废弃，现在使用Crawl4ai自动分块")
    return []


def get_course_container_selector() -> str:
    """
    ⚠️ 此函数已废弃，现在使用LLM自动分块提取
    """
    print("⚠️ 警告：CSS选择器方式已废弃，现在使用LLM自动分块提取")
    return "使用LLM自动分块提取，无需CSS选择器"