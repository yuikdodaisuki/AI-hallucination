"""页面解析工具"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import random
from ..config import BROWSER_CONFIG, SELECTORS, TARGET_RATINGS


class PageParser:
    """页面解析器"""
    
    def __init__(self, driver):
        self.driver = driver
    
    def get_category_elements(self):
        """获取学科类别元素"""
        return WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, SELECTORS['categories']))
        )
    
    def get_subject_elements(self):
        """获取学科元素"""
        return WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, SELECTORS['subjects']))
        )
    
    def click_and_wait(self, element):
        """点击元素并等待"""
        element.click()
        time.sleep(random.uniform(*BROWSER_CONFIG['click_wait']))
    
    def parse_evaluation_results(self):
        """解析评估结果"""
        result_content = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "vsb_content"))
        )
        
        html = result_content.get_attribute("innerHTML")
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table")
        
        schools_by_rating = {}
        current_rating = None
        
        if table:
            for tr in table.find_all("tr"):
                tds = tr.find_all("td")
                if len(tds) >= 1:
                    # 检查第一个td是否包含评级
                    if tds[0].has_attr('rowspan'):
                        rating = tds[0].get_text(strip=True)
                        if rating not in TARGET_RATINGS:
                            print(f"  跳过非目标评级: {rating}")
                            continue
                        
                        current_rating = rating
                        if current_rating not in schools_by_rating:
                            schools_by_rating[current_rating] = []
                        
                        # 处理同一行的学校信息
                        if len(tds) > 1:
                            school_info = self._extract_school_info(tds[1])
                            if school_info:
                                schools_by_rating[current_rating].append(school_info)
                    
                    elif current_rating and len(tds) > 0:
                        # 只有学校信息的行
                        school_info = self._extract_school_info(tds[0])
                        if school_info:
                            schools_by_rating[current_rating].append(school_info)
        
        return schools_by_rating
    
    def _extract_school_info(self, td_element):
        """提取学校信息"""
        school_info = td_element.get_text(strip=True)
        if school_info:
            parts = school_info.split()
            if len(parts) >= 2:
                return {
                    "code": parts[0].strip(),
                    "name": ' '.join(parts[1:]).strip()
                }
        return None