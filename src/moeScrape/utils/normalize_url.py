from urllib.parse import urlparse


# 获取文件的父级url以便于文件下载
def get_base_url(url):
    """
    Get the base URL for relative paths from the current page URL.
    For a URL like http://www.moe.gov.cn/srcsite/A22/moe_843/201709/t20170921_314942.html
    returns http://www.moe.gov.cn/srcsite/A22/moe_843/201709/
    """
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.split('/')

    # Remove the last part (filename)
    if '.' in path_parts[-1]:
        path_parts = path_parts[:-1]

    new_path = '/'.join(path_parts) + '/'
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{new_path}"
    return base_url


# 读取JSON文件
def extract_urls(data):

    # 提取所有URL（假设URL字段名为"url"，根据实际情况修改）
    urls = []
    if data.get("code") == 0:
        results = data.get("data", {}).get("search", {}).get("searchs", [])
        for item in results:
            url = item.get("viewUrl")
            if url:
                urls.append(url)
        # print(f"共提取到 {len(urls)} 个 URL")
        # 保存到文件
        # with open("urls.txt", "w", encoding="utf-8") as f:
        #     f.write("\n".join(urls))
    else:
        print("API 返回错误:", data.get("msg", "未知错误"))

    return urls
