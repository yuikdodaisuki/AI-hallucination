"""WebDriver管理工具"""
import undetected_chromedriver as uc
import random
import time
from ..config import BROWSER_CONFIG


class DriverManager:
    """WebDriver管理器"""
    
    def __init__(self):
        self.driver = None
# 用于创建driver实例
    def create_driver(self):
        
        options = uc.ChromeOptions()
        
        # 随机窗口大小
        window_width = random.randint(*BROWSER_CONFIG['window_width_range'])
        window_height = random.randint(*BROWSER_CONFIG['window_height_range'])
        options.add_argument(f"--window-size={window_width},{window_height}")
        
        self.driver = uc.Chrome(options=options)
        return self.driver
    
    def navigate_to_page(self, url):
        """导航到指定页面"""
        if not self.driver:
            raise ValueError("Driver not initialized")
        
        # 随机等待
        time.sleep(random.uniform(*BROWSER_CONFIG['wait_time_range']))
        self.driver.get(url)
        
        # 随机等待页面加载
        time.sleep(random.uniform(*BROWSER_CONFIG['page_load_wait']))
    
    def navigate_to_iframe(self, base_url, yxphb_selector, iframe_selector):
        """导航到iframe页面"""
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        # 找到yxphb div
        yxphb_div = WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, yxphb_selector))
        )
        
        # 找到iframe
        iframe = yxphb_div.find_element(By.CSS_SELECTOR, iframe_selector)
        iframe_src = iframe.get_attribute("src")
        
        # 构建完整的iframe URL
        if iframe_src.startswith("http"):
            iframe_url = iframe_src
        else:
            base_url_clean = base_url.rsplit('/', 1)[0]
            iframe_url = f"{base_url_clean}/{iframe_src}"
        
        print(f"正在访问iframe: {iframe_url}")
        
        # 访问iframe URL
        self.driver.get(iframe_url)
        time.sleep(random.uniform(*BROWSER_CONFIG['iframe_wait']))
        
        return iframe_url
    
    def save_page_source(self, filename):
        """保存页面源码"""
        if self.driver:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            print(f"已保存页面内容到 {filename}")
    
    def close(self):
        """关闭driver"""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def __enter__(self):
        """上下文管理器入口"""
        self.create_driver()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()