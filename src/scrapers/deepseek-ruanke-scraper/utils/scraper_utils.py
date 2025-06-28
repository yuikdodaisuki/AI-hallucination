import json
import os
from typing import List, Set, Tuple

from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CacheMode,
    CrawlerRunConfig,
    LLMExtractionStrategy,
)

from models.venue import Venue
from utils.data_utils import is_complete_venue, is_duplicate_venue


def get_browser_config() -> BrowserConfig:
    """
    Returns the browser configuration for the crawler.

    Returns:
        BrowserConfig: The configuration settings for the browser.
    """
    # https://docs.crawl4ai.com/core/browser-crawler-config/
    return BrowserConfig(
        browser_type="chromium",  # Type of browser to simulate
        headless=False,  # Whether to run in headless mode (no GUI)
        verbose=True,  # Enable verbose logging
    )


def get_llm_strategy() -> LLMExtractionStrategy:
    """
    Returns the configuration for the language model extraction strategy.

    Returns:
        LLMExtractionStrategy: The settings for how to extract data using LLM.
    """
    # https://docs.crawl4ai.com/api/strategies/#llmextractionstrategy
    return LLMExtractionStrategy(
        provider="groq/deepseek-r1-distill-llama-70b",  # Name of the LLM provider
        api_token=os.getenv("GROQ_API_KEY"),  # API token for authentication
        schema=Venue.model_json_schema(),  # JSON schema of the data model
        extraction_type="schema",  # Type of extraction to perform
        instruction=(
            "Extract university ranking data from the table. "
            "For each university, extract: "
            "1. name: the university name "
            "2. layer: the percentage layer/tier information (like '前1%', '前5%', etc.) "
            "Look for span elements containing percentage information that indicates which tier the university belongs to. "
            "The layer field should contain the percentage range like '前1%' or '前5%' etc. "
            "Return as JSON array with objects containing 'name' and 'layer' fields."
        ),  # Instructions for the LLM
        input_format="markdown",  # Format of the input content
        verbose=True,  # Enable verbose logging
    )


async def check_no_results(
    crawler: AsyncWebCrawler,
    url: str,
    session_id: str,
) -> bool:
    """
    Checks if the "No Results Found" message is present on the page.

    Args:
        crawler (AsyncWebCrawler): The web crawler instance.
        url (str): The URL to check.
        session_id (str): The session identifier.

    Returns:
        bool: True if "No Results Found" message is found, False otherwise.
    """
    # Fetch the page without any CSS selector or extraction strategy
    result = await crawler.arun(
        url=url,
        config=CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            session_id=session_id,
            delay_before_return_html=2.0,
        ),
    )

    if result.success:
        if "No Results Found" in result.cleaned_html:
            return True
    else:
        print(
            f"Error fetching page for 'No Results Found' check: {result.error_message}"
        )

    return False


async def fetch_and_process_page(
    crawler: AsyncWebCrawler,
    page_number: int,
    base_url: str,
    subject_name: str,  # 🔥 新增：学科名参数 🔥
    css_selector: str,
    llm_strategy: LLMExtractionStrategy,
    session_id: str,
    required_keys: List[str],
    seen_names: Set[str],
) -> Tuple[List[dict], bool]:
    """
    Fetches and processes a single page of venue data.

    Args:
        crawler (AsyncWebCrawler): The web crawler instance.
        page_number (int): The page number to fetch.
        base_url (str): The base URL of the website.
        css_selector (str): The CSS selector to target the content.
        llm_strategy (LLMExtractionStrategy): The LLM extraction strategy.
        session_id (str): The session identifier.
        required_keys (List[str]): List of required keys in the venue data.
        seen_names (Set[str]): Set of venue names that have already been seen.

    Returns:
        Tuple[List[dict], bool]:
            - List[dict]: A list of processed venues from the page.
            - bool: A flag indicating if the "No Results Found" message was encountered.
    """
    # 🔥 修改这部分：不再使用URL参数，而是通过页码跳转 🔥
    if page_number == 1:
        # 第一页直接访问原始URL
        url = base_url
        print(f" 加载 {subject_name} 第 {page_number} 页...")
        
        # 第一页不需要额外操作
        page_navigation_js = """
        console.log('第一页，无需跳转');
        await new Promise(resolve => setTimeout(resolve, 2000));
        """
    else:
        # 第二页及以后，使用相同URL但通过JavaScript输入页码跳转
        url = base_url  # URL保持不变
        print(f"Navigating to page {page_number} via quick jumper...")
        
        # 🔥 关键：页码跳转的JavaScript代码 🔥
        # 将这部分JavaScript代码替换为更强大的版本：
        page_navigation_js = f"""
        console.log('开始跳转到第 {page_number} 页...');

        // 等待页面加载
        await new Promise(resolve => setTimeout(resolve, 3000));

        // 查找快速跳转容器
        const quickJumper = document.querySelector('.ant-pagination-options-quick-jumper');

        if (quickJumper) {{
            console.log('✅ 找到快速跳转容器');
            
            // 查找输入框
            const pageInput = quickJumper.querySelector('input');
            
            if (pageInput) {{
                console.log('✅ 找到页码输入框');
                console.log('输入框当前值:', pageInput.value);
                
                // 🔥 方法1: 完整的输入和事件序列 🔥
                pageInput.focus();
                pageInput.select();  // 选中所有文本
                pageInput.value = '';  // 清空
                
                // 逐字符输入（模拟真实输入）
                const targetValue = '{page_number}';
                for(let i = 0; i < targetValue.length; i++) {{
                    pageInput.value += targetValue[i];
                    
                    // 触发每个字符的输入事件
                    pageInput.dispatchEvent(new InputEvent('input', {{ 
                        bubbles: true, 
                        data: targetValue[i] 
                    }}));
                    
                    await new Promise(resolve => setTimeout(resolve, 50));
                }}
                
                console.log('📝 已输入页码:', pageInput.value);
                
                // 🔥 触发多种事件确保被检测到 🔥
                
                // 1. 触发 input 事件
                pageInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                
                // 2. 触发 change 事件
                pageInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
                
                // 3. 触发 keyup 事件
                pageInput.dispatchEvent(new KeyboardEvent('keyup', {{
                    key: '{page_number}',
                    bubbles: true
                }}));
                
                await new Promise(resolve => setTimeout(resolve, 500));
                
                // 🔥 方法2: 尝试多种回车方式 🔥
                
                // 1. keydown事件
                const keydownEvent = new KeyboardEvent('keydown', {{
                    key: 'Enter',
                    code: 'Enter',
                    keyCode: 13,
                    which: 13,
                    bubbles: true,
                    cancelable: true
                }});
                pageInput.dispatchEvent(keydownEvent);
                console.log('⌨️ 触发keydown Enter');
                
                await new Promise(resolve => setTimeout(resolve, 200));
                
                // 2. keypress事件
                const keypressEvent = new KeyboardEvent('keypress', {{
                    key: 'Enter',
                    code: 'Enter',
                    keyCode: 13,
                    which: 13,
                    bubbles: true,
                    cancelable: true
                }});
                pageInput.dispatchEvent(keypressEvent);
                console.log('⌨️ 触发keypress Enter');
                
                await new Promise(resolve => setTimeout(resolve, 200));
                
                // 3. keyup事件
                const keyupEvent = new KeyboardEvent('keyup', {{
                    key: 'Enter',
                    code: 'Enter',
                    keyCode: 13,
                    which: 13,
                    bubbles: true
                }});
                pageInput.dispatchEvent(keyupEvent);
                console.log('⌨️ 触发keyup Enter');
                
                await new Promise(resolve => setTimeout(resolve, 500));
                
                // 🔥 方法3: 查找并点击确认按钮 🔥
                const confirmButtons = quickJumper.querySelectorAll('button, .ant-btn');
                console.log(`找到 ${{confirmButtons.length}} 个可能的确认按钮`);
                
                for(let btn of confirmButtons) {{
                    if(btn.offsetParent !== null && !btn.disabled) {{
                        console.log('🔘 点击确认按钮:', btn.textContent.trim());
                        btn.click();
                        break;
                    }}
                }}
                
                await new Promise(resolve => setTimeout(resolve, 1000));
                
                // 🔥 方法4: 触发表单提交（如果输入框在表单中） 🔥
                const form = pageInput.closest('form');
                if(form) {{
                    console.log('📋 找到表单，触发提交');
                    form.dispatchEvent(new Event('submit', {{ bubbles: true }}));
                }}
                
                // 🔥 方法5: 尝试通过React/Vue组件触发 🔥
                if(pageInput._reactInternalFiber || pageInput.__reactInternalInstance) {{
                    console.log('🔄 检测到React组件，尝试React事件');
                    const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                    nativeInputValueSetter.call(pageInput, '{page_number}');
                    
                    const reactEvent = new Event('input', {{ bubbles: true }});
                    reactEvent.simulated = true;
                    pageInput.dispatchEvent(reactEvent);
                }}
                
                // 等待页面跳转
                console.log('⏳ 等待页面跳转...');
                await new Promise(resolve => setTimeout(resolve, 4000));
                
                // 🔥 验证是否跳转成功 🔥
                const currentPageIndicator = document.querySelector('.ant-pagination-item-active');
                if(currentPageIndicator) {{
                    const currentPage = currentPageIndicator.textContent.trim();
                    console.log('📄 当前页码指示器显示:', currentPage);
                    
                    if(currentPage === '{page_number}') {{
                        console.log('✅ 页面跳转成功!');
                    }} else {{
                        console.log('❌ 页面跳转可能失败，期望:', '{page_number}', '实际:', currentPage);
                    }}
                }} else {{
                    console.log('⚠️ 未找到当前页码指示器');
                }}
                
            }} else {{
                console.log('❌ 未找到输入框');
                
                // 🔥 备选方案：查找其他可能的输入框 🔥
                const allInputs = document.querySelectorAll('input[type="number"], input[type="text"]');
                console.log(`找到 ${{allInputs.length}} 个输入框`);
                
                for(let input of allInputs) {{
                    if(input.offsetParent !== null) {{
                        console.log('尝试其他输入框:', input.className, input.placeholder);
                    }}
                }}
            }}
        }} else {{
            console.log('❌ 未找到快速跳转容器');
            
            // 🔥 备选方案：查找其他可能的分页元素 🔥
            const paginationContainers = document.querySelectorAll(
                '.ant-pagination, .pagination, [class*="pagination"], [class*="pager"]'
            );
            console.log(`找到 ${{paginationContainers.length}} 个分页容器`);
            
            for(let container of paginationContainers) {{
                console.log('分页容器:', container.className);
                
                const inputs = container.querySelectorAll('input');
                console.log(`该容器中有 ${{inputs.length}} 个输入框`);
            }}
        }}
        """

    # Check if "No Results Found" message is present
    no_results = await check_no_results(crawler, url, session_id)
    if no_results:
        print(f" {subject_name} 第 {page_number} 页获取失败: {result.error_message}")
        return [], True  # No more results, signal to stop crawling

    # Fetch page content with the extraction strategy
    result = await crawler.arun(
        url=url,
        config=CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,  # Do not use cached data
            extraction_strategy=llm_strategy,  # Strategy for data extraction
            css_selector=css_selector,  # Target specific content on the page
            session_id=session_id,  # Unique session ID for the crawl
            js_code=page_navigation_js,  # 🔥 添加这行：执行页码跳转JavaScript 🔥
            delay_before_return_html=8.0,  # 增加等待时间确保跳转完成
        ),
    )

    if not (result.success and result.extracted_content):
        print(f" {subject_name} 第 {page_number} 页无数据")
        return [], False

    # Parse extracted content
    extracted_data = json.loads(result.extracted_content)
    if not extracted_data:
        print(f"No venues found on page {page_number}.")
        return [], False

    # After parsing extracted content
    print("Extracted data:", extracted_data)

    # Process venues
    complete_venues = []
    for venue in extracted_data:
        # Debugging: Print each venue to understand its structure
        print("Processing venue:", venue)

        # Ignore the 'error' key if it's False
        if venue.get("error") is False:
            venue.pop("error", None)  # Remove the 'error' key if it's False

        #  为每条数据添加学科信息 
        venue["subject"] = subject_name

        if not is_complete_venue(venue, required_keys):
            continue  # Skip incomplete venues

        if is_duplicate_venue(venue["name"], seen_names):
            print(f"Duplicate venue '{venue['name']}' found. Skipping.")
            continue  # Skip duplicate venues

        # Add venue to the list
        seen_names.add(venue["name"])
        complete_venues.append(venue)

    if not complete_venues:
        print(f"No complete venues found on page {page_number}.")
        return [], False

    print(f"Extracted {len(complete_venues)} venues from page {page_number}.")
    return complete_venues, False  # Continue crawling
