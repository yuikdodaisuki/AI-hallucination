import os
import hashlib
from datetime import datetime

import requests
import json
from bs4 import BeautifulSoup
import time
import urllib.parse
import re
from urllib.parse import urlparse, urljoin

from .utils import get_base_url, find_initPubProperty, extract_urls, is_src_site_format, is_jyb_format
from requests.exceptions import ChunkedEncodingError, ConnectionError, Timeout


def scrape_all_pages(base_url, search_term, download_keywords, max_pages=10):
    """
    爬取教育部网站搜索结果的多个页面
    
    Args:
        base_url: 基础URL
        search_term: 搜索关键词
        download_keywords: 下载筛选词列表
        max_pages: 最大爬取页数
    
    Returns:
        int: 实际爬取的页数
    """
    # 第一页URL
    encoded_term = urllib.parse.quote(search_term)
    print(encoded_term)
    current_url = f"{base_url}s?siteCode=bm05000001&tab=gk&qt={encoded_term}#anchor"
    page = 1
    total_processed = 0

    # 模拟浏览器访问
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/91.0.4472.124 Safari/537.36",
    }
    print(f"正在请求搜索: {current_url}")

    # 获取第一页（用于提取搜索参数）
    try:
        response = requests.get(current_url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        
        if response.status_code != 200:
            print(f"搜索页面请求失败，状态码: {response.status_code}")
            return 0
            
        # 保存调试文件
        test_html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../test.html")
        with open(test_html_path, "w", encoding="utf-8") as f:
            f.write(response.text)
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
    except Exception as e:
        print(f"请求异常: {e}")
        return 0

    # 分页爬取循环
    while page <= max_pages:
        print(f"正在爬取第 {page} 页 (最多 {max_pages} 页)")
        
        # 处理当前页
        page_result = extract_links_from_page(soup, page, download_keywords)
        
        if not page_result:
            print(f"第 {page} 页无更多结果，爬取结束")
            break
            
        total_processed += 1
        page += 1
        
        # 添加延时避免请求过快
        time.sleep(1)

    print(f"爬取完成，共处理 {total_processed} 页")
    return total_processed


# 这个函数用于对于单页内容进行解析，模拟搜索拉取的post请求，从而获得当前页面的所有搜索结果的json。我们可以获取其中的url进行进一步访问
# 可以更改输入的page从而进行不同页的请求
def extract_links_from_page(soup, page, download_keywords): # 新增 download_keywords 参数
    # 创建会话对象以维持cookies
    session = requests.Session()
    # 使用find_initPubProperty方法来获取原html文件里的相关参数，以用于传输
    params_list = find_initPubProperty(soup)

    #  构建搜索请求参数
    search_url = "https://api.so-gov.cn/s"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://so.moe.gov.cn",
        "Referer": "https://so.moe.gov.cn/",
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, '
                      'like Gecko)'
                      'Chrome/135.0.0.0 Mobile Safari/537.36 ',
        "suid": params_list[13],
        # 建议包含的辅助头
        "Accept": "application/json",
        "sec-ch-ua": '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site"
    }
    # print(params_list[8])
    data = {
        "siteCode": params_list[0],  # 假设值，需要根据实际情况调整
        "tab": params_list[1],
        "timestamp": params_list[6],
        "wordToken": params_list[7],
        "tabToken": params_list[8],
        "page": page,
        "pageSize": params_list[5],
        "qt": params_list[2],  # 搜索关键词
        "timeOption": 0,
        "sort": "relevance",
        "keyPlace": 0,
        "fileType": ""

    }

    #  发送搜索请求

    search_response = session.post(search_url, data=data, headers=headers)
    a = requests.post(search_url, data=data, headers=headers)

    if search_response.status_code == 200:
        search_results = search_response.json()
        print(search_results)
        # 使用extract_urls读取我们所解析的html文件里的url并将其转化为数组
        urls = extract_urls(search_results)
        # single_response = extract_single_article(urls[0])
        if not urls:
            return False
        # 对于每一个url都进行单独页面的解析。这里是解析内容的关键
        for item in urls:
            url = item
            single_response = extract_single_article(url, download_keywords) # 新增 download_keywords 参数

        return True

    else:
        print(f"搜索请求失败，状态码: {search_response.status_code}")
        print(search_response.text)
        return None


# 单独分析一个url里的内容
def extract_single_article(url, download_keywords, max_retries=3): # 新增 download_keywords 参数
    """单独分析一个url里的内容，添加重试机制"""
    print(f"正在处理: {url}")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, '
                      'like Gecko)'
                      'Chrome/135.0.0.0 Mobile Safari/537.36 '
    }
    for attempt in range(max_retries):
        try:
            print(f"尝试第 {attempt + 1} 次请求: {url}")
            
            # 添加超时设置
            response = requests.get(
                url, 
                headers=headers, 
                timeout=(10, 30),  # (连接超时, 读取超时)
                stream=False,      # 禁用流式传输
                verify=True        # 验证SSL证书
            )
            
            response.encoding = 'utf-8'
            
            if response.status_code != 200:
                print(f"请求失败，状态码: {response.status_code}")
                if attempt < max_retries - 1:
                    time.sleep(2)  # 等待2秒后重试
                    continue
                return None
            
            # 请求成功，处理内容
            policy_info = parse_policy_document(response.text, url)
            
            # 检查是否包含关键词
            content_to_check = policy_info.get('文件标题', '') + policy_info.get('正文内容', '')
            should_download = False
            
            for keyword in download_keywords:
                if keyword in content_to_check:
                    should_download = True
                    break
            
            if should_download:
                saved_path = save_policy_data(policy_info, get_base_url(url))
                print(f"数据已保存至：{saved_path}")
                return saved_path
            else:
                print(f"文件内容未包含检索词条，跳过下载：{policy_info.get('文件标题', '未知标题')}")
                return None
                
        except ChunkedEncodingError as e:
            print(f"分块编码错误 (尝试 {attempt + 1}/{max_retries}): {str(e)}")
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2  # 递增等待时间
                print(f"等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
                continue
            else:
                print(f"达到最大重试次数，跳过该URL: {url}")
                return None
                
        except (ConnectionError, Timeout) as e:
            print(f"网络连接错误 (尝试 {attempt + 1}/{max_retries}): {str(e)}")
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 3  # 网络错误等待更长时间
                print(f"等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
                continue
            else:
                print(f"网络连接失败，跳过该URL: {url}")
                return None
                
        except Exception as e:
            print(f"未知错误 (尝试 {attempt + 1}/{max_retries}): {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            else:
                print(f"处理失败，跳过该URL: {url}")
                return None
    
    return None


# 解析html文件为详细的内容，借助了不同页面的格式来进行识别
def parse_policy_document(html_content, siteUrl, download_dir='downloads'):
    """
    Parse policy document HTML and download attachments.

    Args:
        html_content (str): HTML content of the policy document
        siteUrl(str) :
        download_dir (str): Directory to save downloaded attachments
    """
    # Create BeautifulSoup object
    soup = BeautifulSoup(html_content, 'html.parser')
    base_url = get_base_url(siteUrl)
    policy_info = {}
    # ================== 页面类型识别 ==================
    if is_src_site_format(soup):
        # 传入所有必要参数到src_site解析器
        parse_src_site_format(soup, policy_info, base_url)
    elif is_jyb_format(soup):
        parse_jyb_format(soup, policy_info)
    else:
        raise ValueError("无法识别的页面格式")

    return policy_info


# ------------------ 新版解析器实现 ------------------
# 解析src_site,同时解析附件
def parse_src_site_format(soup, policy_info, base_url):

    # 原有表格解析逻辑
    table_rows = soup.find_all('tr')
    for row in table_rows:
        title_cells = row.find_all('td', class_='policy-item-title')
        cont_cells = row.find_all('td', class_='policy-item-cont')
        for i, title_cell in enumerate(title_cells):
            title = title_cell.get_text(strip=True).replace('：', '')
            if i < len(cont_cells):
                policy_info[title] = cont_cells[i].get_text(strip=True)

    # 正文内容解析
    content_div = soup.find('div', id='downloadContent')
    if content_div:
        # 标题
        h1 = content_div.find('h1')
        policy_info['文件标题'] = h1.get_text(strip=True) if h1 else ''

        # 文号
        doc_num = content_div.find('p', class_='moe-policy-wenhao')
        policy_info['文号'] = doc_num.get_text(strip=True) if doc_num else ''

        # 正文内容
        content_paragraphs = []
        for p in content_div.find_all('p'):
            if not p.get('class') or 'moe-policy-wenhao' not in p.get('class'):
                content_paragraphs.append(p.get_text(strip=True))
        policy_info['正文内容'] = '\n'.join(content_paragraphs)

        # 仅src_site格式处理附件
        process_attachments(content_div, base_url, policy_info)


def parse_jyb_format(soup, policy_info):
    """处理jyb格式（无附件处理）"""
    detail_box = soup.find('div', class_='moe-detail-box')

    # 标题
    h1 = detail_box.find('h1')
    policy_info['文件标题'] = h1.get_text(strip=True) if h1 else ''

    # 副标题
    h2 = detail_box.find('h2')
    policy_info['副标题'] = h2.get_text(strip=True) if h2 else ''

    # 正文内容
    editor_div = detail_box.find('div', class_='TRS_Editor')
    if editor_div:
        paragraphs = [p.get_text(strip=True) for p in editor_div.find_all('p')]
        policy_info['正文内容'] = '\n'.join(paragraphs)
    else:
        policy_info['正文内容'] = ''

    # 明确设置为空数组（根据需求可选）
    policy_info['附件'] = []


# ------------------ 附件处理（仅被src_site调用） ------------------
def process_attachments(content_div, base_url, policy_info):

    attachments = []
    for a in content_div.find_all('a'):
        # 增加附件类型过滤（可选）
        attachments.append({
            'name': a.get_text(strip=True),
            'url': a.get('href'),
            'original_src': a.get('oldsrc')
        })

    policy_info['附件'] = attachments


def download_attachment(attachment, base_url, download_dir):

    # 确保传入参数有效性
    if not attachment.get('url'):
        print("附件缺少URL")
        return None

    # 构建完整URL
    relative_url = attachment['url']
    full_url = urljoin(base_url, relative_url)

    # 生成安全文件名（优先使用original_src）
    filename = generate_safe_filename(
        attachment.get('original_src') or relative_url,
        fallback_name=attachment['name']
    )

    # 创建下载目录（集成到存储体系）
    os.makedirs(download_dir, exist_ok=True)
    file_path = os.path.join(download_dir, filename)

    # 复用原有下载头设置
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/91.0.4472.124 Safari/537.36',
        'Referer': base_url,
    }

    try:
        print(f"正在下载 {attachment['name']} ({full_url})")
        response = requests.get(full_url, headers=headers, stream=True, timeout=30)

        if response.status_code == 200:
            # 写入文件（自动处理编码）
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:  # 过滤keep-alive chunks
                        f.write(chunk)
            print(f"下载成功：{file_path}")
            return file_path
        else:
            print(f"下载失败 HTTP {response.status_code}")
            return None

    except Exception as e:
        print(f"下载异常：{str(e)}")
        return None


def generate_safe_filename(raw_name, fallback_name="file"):
    """生成安全文件名（保留扩展名）"""
    # 提取原始文件名和扩展名
    basename = os.path.basename(raw_name)
    name_part, ext = os.path.splitext(basename)

    # 清理非法字符（保留中文）
    clean_name = re.sub(r'[<>:"/\\|?*]', '_', name_part)
    clean_name = clean_name.strip()

    # 处理空文件名情况
    if not clean_name:
        clean_name = re.sub(r'[^\\w]', '_', fallback_name)[:50]

    # 限制文件名长度
    max_length = 100
    if len(clean_name) > max_length:
        clean_name = clean_name[:max_length]

    # 保留扩展名
    return f"{clean_name}{ext or ''}"


def print_policy_info(policy_info):
    """Print policy information in a readable format."""
    print("\n===== 政策文件信息 =====")
    for key, value in policy_info.items():
        if key != '附件' and key != '正文内容':
            print(f"{key}: {value}")

    print("\n===== 正文内容 =====")
    print(policy_info.get('正文内容', '无正文内容'))

    print("\n===== 附件列表 =====")
    for i, attachment in enumerate(policy_info.get('附件', []), 1):
        print(f"{i}. {attachment['name']} - 原始文件名: {attachment['original_src']}")


def save_policy_data(policy_info, base_url, base_dir="../../data/moepolicies"):
    """
    增强版数据存储函数
    :param policy_info: 解析后的政策信息字典
    :param base_url: 原始页面URL（用于构建附件完整URL）
    :param base_dir: 根存储目录
    :return: 元数据文件路径
    """

    # 1. 获取当前文件所在目录，构建绝对路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    absolute_base_dir = os.path.join(current_dir, base_dir)

    #  创建唯一文档目录
    doc_hash = generate_doc_hash(policy_info)
    doc_dir = os.path.join(absolute_base_dir, doc_hash)
    os.makedirs(doc_dir, exist_ok=True)

    # 2. 处理附件（仅当存在附件时）
    if '附件' in policy_info and policy_info['附件']:
        attachment_dir = os.path.join(doc_dir, 'attachments')
        os.makedirs(attachment_dir, exist_ok=True)

        processed_attachments = []
        for att in policy_info['附件']:
            # 执行下载（关键修改点）
            local_path = download_attachment(
                attachment=att,  # 传递完整附件字典
                base_url=base_url,
                download_dir=attachment_dir
            )

            # 记录结果（处理下载失败情况）
            attachment_record = {
                "name": att['name'],
                "original_url": att['url'],
                "download_status": "success" if local_path else "failed"
            }

            if local_path:
                attachment_record.update({
                    "local_path": os.path.relpath(local_path, doc_dir),
                    "filesize": os.path.getsize(local_path)
                })

            processed_attachments.append(attachment_record)

        policy_info['附件'] = processed_attachments

    # 3. 保存元数据（增加时间戳）
    meta_info = {
        "metadata": {
            "doc_hash": doc_hash,
            "saved_at": datetime.now().isoformat(),
            "source_url": base_url
        },
        "content": policy_info
    }

    meta_path = os.path.join(doc_dir, 'meta.json')
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(meta_info, f, ensure_ascii=False, indent=2)

    return meta_path


def generate_doc_hash(policy_info):
    """生成文档唯一标识"""
    raw_str = f"{policy_info.get('文件标题', '')}-{policy_info.get('发布日期', '')}"
    return hashlib.md5(raw_str.encode('utf-8')).hexdigest()[:8]


def generate_attachment_name(attachment, index):
    """生成安全的附件文件名"""
    original_name = os.path.basename(urlparse(attachment['url']).path)
    clean_name = re.sub(r'[^\w\-_.]', '_', original_name)  # 替换非法字符

    # 添加哈希后缀防止冲突
    name_hash = hashlib.md5(attachment['url'].encode()).hexdigest()[:4]
    return f"{index + 1:02d}_{clean_name}_{name_hash}"


def startScrape():
    # 在这里对附件进行检索
    download = ["双一流"] #检索词条
    scrape_all_pages("https://so.moe.gov.cn/", "双一流", download) # 修改：传入 download 列表
    


