"""改进的学科爬虫 - 提取完整专业名"""
# filepath: c:\Users\83789\PycharmProjects\scrapetest\deepseek-ai-web-crawler\utils\subject_crawler.py

import asyncio
from typing import List, Dict, Set
from urllib.parse import urljoin

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
from bs4 import BeautifulSoup

from utils.scraper_utils import fetch_and_process_page, get_browser_config, get_llm_strategy
from utils.data_utils import save_venues_to_csv
from config import TEST_MODE, MAX_SUBJECTS, MAX_PAGES_PER_SUBJECT


async def extract_subject_links(
    crawler: AsyncWebCrawler, 
    index_url: str,
    link_selector: str,
    session_id: str
) -> List[Dict[str, str]]:
    """
    从学科索引页面提取所有学科链接和完整学科名
    """
    print(f"🔍 开始提取学科链接从: {index_url}")
    
    try:
        result = await crawler.arun(
            url=index_url,
            config=CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,
                session_id=session_id,
                delay_before_return_html=5.0,
            ),
        )
        
        if result.success:
            soup = BeautifulSoup(result.html, 'html.parser')
            subject_links = []
            
            # 🔥 查找所有学科链接 🔥
            links = soup.select(link_selector)
            
            print(f"📋 找到 {len(links)} 个潜在学科链接")
            
            for index, link in enumerate(links):
                href = link.get('href')
                
                # 🔥 改进：提取完整的专业名（包含所有span内容） 🔥
                spans = link.find_all('span')
                
                if spans:
                    # 将所有span的文本连接起来
                    subject_parts = []
                    for span in spans:
                        text = span.get_text(strip=True)
                        if text:
                            subject_parts.append(text)
                    
                    # 用空格连接所有部分，形成完整专业名
                    subject_name = ' '.join(subject_parts)
                else:
                    # 如果没有span，使用整个链接的文本
                    subject_name = link.get_text(strip=True)
                
                if href and subject_name:
                    # 处理相对链接
                    full_url = urljoin(index_url, href)
                    
                    subject_info = {
                        "subject_name": subject_name,
                        "url": full_url
                    }
                    
                    subject_links.append(subject_info)
                    print(f"学科 {index + 1}: {subject_name} -> {full_url}")
                    
                    # 🔥 测试模式：只提取指定数量的链接 🔥
                    if TEST_MODE and len(subject_links) >= MAX_SUBJECTS:
                        print(f"🧪 测试模式：已提取 {MAX_SUBJECTS} 个学科链接，停止提取")
                        break
            
            print(f"✅ 成功提取 {len(subject_links)} 个学科链接")
            return subject_links
            
        else:
            print(f"❌ 提取学科链接失败: {result.error_message}")
            return []
            
    except Exception as e:
        print(f"❌ 提取学科链接异常: {e}")
        return []


async def crawl_single_subject_ranking(
    crawler: AsyncWebCrawler,
    subject_info: Dict[str, str],
    css_selector: str,
    llm_strategy,
    session_id: str,
    required_keys: List[str]
) -> List[Dict]:
    """
    爬取单个学科的排名数据（测试模式限制页数）
    """
    subject_name = subject_info["subject_name"]
    subject_url = subject_info["url"]
    
    print(f"\n{'='*60}")
    print(f"🎯 开始爬取学科: {subject_name}")
    print(f"🔗 URL: {subject_url}")
    print(f"{'='*60}")
    
    all_venues = []
    seen_names = set()
    page_number = 1
    
    # 🔥 测试模式：限制页数 🔥
    max_pages = MAX_PAGES_PER_SUBJECT if TEST_MODE else 20
    print(f"📄 {'测试模式' if TEST_MODE else '正常模式'}：最多爬取 {max_pages} 页")
    
    consecutive_empty_pages = 0
    
    while page_number <= max_pages:
        try:
            venues, should_stop = await fetch_and_process_page(
                crawler,
                page_number,
                subject_url,
                subject_name,
                css_selector,
                llm_strategy,
                f"{session_id}_{subject_name.replace(' ', '_')}",
                required_keys,
                seen_names,
            )
            
            if should_stop:
                print(f"🔚 {subject_name} 检测到停止条件")
                break
                
            if not venues:
                consecutive_empty_pages += 1
                print(f"⚠️ {subject_name} 第 {page_number} 页无数据 (连续空页: {consecutive_empty_pages})")
                
                if consecutive_empty_pages >= 2:  # 测试模式下更快停止
                    print(f"🔚 {subject_name} 连续2页无数据，停止爬取")
                    break
            else:
                consecutive_empty_pages = 0
                
                # 🔥 为每条数据添加学科信息 🔥
                for venue in venues:
                    venue["subject"] = subject_name
                
                all_venues.extend(venues)
                print(f"📊 {subject_name} 累计数据: {len(all_venues)} 条")
            
            page_number += 1
            
            # 页面间延迟（测试模式下减少延迟）
            if page_number <= max_pages:
                delay = 2 if TEST_MODE else 3
                await asyncio.sleep(delay)
            
        except Exception as e:
            print(f"❌ {subject_name} 第 {page_number} 页异常: {e}")
            consecutive_empty_pages += 1
            if consecutive_empty_pages >= 2:
                break
            page_number += 1
    
    print(f"🎉 {subject_name} 爬取完成，共 {len(all_venues)} 条数据")
    return all_venues


async def crawl_all_subject_rankings(
    index_url: str,
    subject_link_selector: str,
    ranking_css_selector: str,
    required_keys: List[str]
) -> List[Dict]:
    """
    爬取所有学科的排名数据（支持测试模式）
    """
    browser_config = get_browser_config()
    llm_strategy = get_llm_strategy()
    session_id = "subject_ranking_crawl"
    
    all_subject_data = []
    
    async with AsyncWebCrawler(config=browser_config) as crawler:
        
        # 🔥 第一步：提取学科链接 🔥
        subject_links = await extract_subject_links(
            crawler,
            index_url,
            subject_link_selector,
            session_id
        )
        
        if not subject_links:
            print("❌ 未找到任何学科链接")
            return []
        
        mode_info = f"{'🧪 测试模式' if TEST_MODE else '🚀 正常模式'}"
        print(f"\n📋 {mode_info} - 找到 {len(subject_links)} 个学科，开始逐个爬取...")
        
        # 🔥 第二步：逐个爬取每个学科的排名 🔥
        for index, subject_info in enumerate(subject_links):
            print(f"\n🔄 进度: {index + 1}/{len(subject_links)}")
            
            try:
                subject_data = await crawl_single_subject_ranking(
                    crawler,
                    subject_info,
                    ranking_css_selector,
                    llm_strategy,
                    session_id,
                    required_keys
                )
                
                all_subject_data.extend(subject_data)
                print(f"📊 总累计数据: {len(all_subject_data)} 条")
                
                # 学科间延迟（测试模式下减少延迟）
                if index < len(subject_links) - 1:
                    delay = 5 if TEST_MODE else 15
                    print(f"⏱️ 等待 {delay} 秒后爬取下一个学科...")
                    await asyncio.sleep(delay)
                    
            except Exception as e:
                print(f"❌ 爬取学科 {subject_info['subject_name']} 失败: {e}")
                continue
    
    return all_subject_data