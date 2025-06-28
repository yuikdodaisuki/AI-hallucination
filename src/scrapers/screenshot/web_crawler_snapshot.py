"""
使用crawl4ai进行网页爬取和快照截取
"""
import base64
import asyncio
import os
from datetime import datetime
from crawl4ai import *
current_dir = os.path.dirname(os.path.abspath(__file__))

async def demo_screenshot():
    async with AsyncWebCrawler() as crawler:
        result : CrawlResult = await crawler.arun(
                url="https://www.eol.cn/news/yaowen/202408/t20240801_2627275.shtml",
                config=CrawlerRunConfig(screenshot=True)
        )

        if result.screenshot:
            screenshot_path = f"{current_dir}/snapshots/screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            with open(screenshot_path, 'wb') as f:
                f.write(base64.b64decode(result.screenshot))
            print(f"📸 截图已保存: {screenshot_path}")

async def main():
    await demo_screenshot()

if __name__ == "__main__":
    asyncio.run(main())
    from PIL import Image

    # 打开原始图片
    img = Image.open("snapshots\screenshot_20250619_213839.png")
    width, height = img.size

    # 检查高度是否符合要求
    if height == 40000:
        # 分割图片
        for i in range(10):
            # 计算裁剪区域 (左, 上, 右, 下)
            box = (0, i*4000, width, (i+1)*4000)
            chunk = img.crop(box)
            chunk.save(f"分割图_{i+1}.png")  # 保存为PNG保证质量
        print("分割完成！共生成10张图片")
    else:
        print(f"错误：图片高度应为40000像素，当前为{height}像素")