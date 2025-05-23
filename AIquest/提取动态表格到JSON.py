import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import json
import os
import traceback # 新增导入
from bs4 import BeautifulSoup

# 目标网页URL
url = 'https://www.cdgdc.edu.cn/dslxkpgjggb/'
# 输出JSON文件名
output_filename = '学科评估数据.json'

def extract_table_to_json(url, output_filename):
    # 创建undetected_chromedriver实例
    options = uc.ChromeOptions()
    # 添加一些随机的窗口大小，使每次访问看起来都不同
    window_width = random.randint(1000, 1200)
    window_height = random.randint(800, 1000)
    options.add_argument(f"--window-size={window_width},{window_height}")

    # 创建driver实例
    driver = uc.Chrome(options=options)

    try:
        # 访问网页前随机等待一段时间
        time.sleep(random.uniform(1, 3))
        driver.get(url)

        # 随机等待页面加载
        time.sleep(random.uniform(5, 10))

        # 找到class="yxphb"的div
        yxphb_div = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "yxphb"))
        )

        # 找到iframe
        iframe = yxphb_div.find_element(By.TAG_NAME, "iframe")
        iframe_src = iframe.get_attribute("src")

        # 构建完整的iframe URL
        if iframe_src.startswith("http"):
            iframe_url = iframe_src
        else:
            # 相对路径转绝对路径
            base_url = url.rsplit('/', 1)[0]
            iframe_url = f"{base_url}/{iframe_src}"

        print(f"正在访问iframe: {iframe_url}")

        # 访问iframe URL
        driver.get(iframe_url)
        time.sleep(random.uniform(3, 5))

        # 保存iframe内容以便调试
        with open('iframe_content.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print("已保存iframe内容到iframe_content.html文件")

        # 查找所有class="Zmen"和class="Zmen2"的元素 (第一列：学科类别)
        zmen_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".Zmen, .Zmen2"))
        )

        # 创建结果数据结构
        result_data = {}

        # 遍历第一列的元素（学科类别）
        # 注意：这里需要复制一份元素列表，因为点击操作可能会导致原始列表失效
        for i in range(len(zmen_elements)):
            # 重新查找当前学科类别元素，避免StaleElementReferenceException
            # 使用索引来定位元素，确保每次都获取最新的引用
            current_zmen_element = WebDriverWait(driver, 10).until(
                 EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".Zmen, .Zmen2"))
            )[i]

            # 获取学科类别名称
            category_name = current_zmen_element.text.strip()
            print(f"处理学科类别: {category_name}")

            # 点击学科类别
            current_zmen_element.click()
            time.sleep(random.uniform(1, 2))  # 等待第二列加载

            # 查找第二列的所有元素（学科代码和名称）
            # 在点击第一列元素后重新查找第二列元素，避免StaleElementReferenceException
            subject_elements = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#leftgundong a.hei12"))
            )

            # 创建学科类别的数据结构
            result_data[category_name] = {}

            # 遍历第二列的元素（学科）
            # 注意：这里需要复制一份元素列表，因为点击操作可能会导致原始列表失效
            for j in range(len(subject_elements)):
                 # 重新查找当前学科元素，避免StaleElementReferenceException
                 # 使用索引来定位元素，确保每次都获取最新的引用
                 current_subject_element = WebDriverWait(driver, 10).until(
                     EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#leftgundong a.hei12"))
                 )[j]

                # 获取学科代码和名称
                 subject_code_name = current_subject_element.text.strip()
                 subject_id = current_subject_element.get_attribute("id") # 虽然id可能为空，但保留获取
                 print(f"  处理学科: {subject_code_name}")

                # 点击学科
                 current_subject_element.click()
                 time.sleep(random.uniform(1, 2))  # 等待第三列加载

                # 查找第三列的内容（评估结果）
                 result_content = WebDriverWait(driver, 10).until(
                     EC.presence_of_element_located((By.ID, "vsb_content"))
                 )
                 html = result_content.get_attribute("innerHTML")
                 soup = BeautifulSoup(html, "html.parser")
                 table = soup.find("table")
                 schools_by_rating = {}
                 current_rating = None
                 if table: # 检查是否找到表格
                     for tr in table.find_all("tr"):
                         tds = tr.find_all("td")
                         if len(tds) >= 1: # 至少有一个td
                             # 检查第一个td是否包含评级（rowspan属性）
                             if tds[0].has_attr('rowspan'):
                                 rating = tds[0].get_text(strip=True)
                                 if rating not in ["A+","A","A-"]:
                                     # 跳过非A+、A、A-的评级
                                    print(f"  跳过非A+、A、A-的评级: {rating}")
                                    continue
                                 current_rating = rating
                                 if current_rating not in schools_by_rating:
                                     schools_by_rating[current_rating] = []
                                 # 处理同一行可能包含学校信息的情况
                                 if len(tds) > 1:
                                     school_info = tds[1].get_text(strip=True)
                                     if school_info:
                                         parts = school_info.split()
                                         if len(parts) >= 2:
                                             school_name = ' '.join(parts[1:]).strip() # 提取学校名称
                                             schools_by_rating[current_rating].append({
                                                 "code": parts[0].strip(), # 提取学校代码
                                                 "name": school_name
                                             })
                             elif current_rating and len(tds) > 0: # 如果没有评级td，且有当前评级
                                 # 这是只有学校信息的行
                                 school_info = tds[0].get_text(strip=True)
                                 if school_info:
                                     parts = school_info.split()
                                     if len(parts) >= 2:
                                         school_name = ' '.join(parts[1:]).strip() # 提取学校名称
                                         schools_by_rating[current_rating].append({
                                             "code": parts[0].strip(), # 提取学校代码
                                             "name": school_name
                                         })

                 # 将评估结果添加到学科数据中
                 result_data[category_name][subject_code_name] = schools_by_rating

        # 将数据保存为JSON文件
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)

        print(f"成功提取表格数据并保存到 {output_filename}")

    except Exception as e:
        print(f"处理过程中发生错误: {e}")
        print("详细错误信息:") # 新增
        traceback.print_exc() # 新增，打印完整的堆栈信息
        # 保存当前页面源码以便调试
        with open('error_page.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print("已保存错误页面到error_page.html文件")
    finally:
        # 关闭浏览器
        driver.quit()

# 转换数据为指定格式
def convert_to_specified_format(input_json, output_json):
    try:
        # 读取原始JSON数据
        with open(input_json, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 创建新的数据结构
        formatted_data = []

        # 遍历所有学科类别
        for category, subjects in data.items():
            # 遍历该类别下的所有学科
            for subject, ratings in subjects.items():
                # 提取学科代码和名称
                subject_parts = subject.split(maxsplit=1)
                subject_code = subject_parts[0] if subject_parts else ""
                subject_name = subject_parts[1] if len(subject_parts) > 1 else ""

                # 遍历该学科下的所有评级
                for rating, schools in ratings.items():
                    # 遍历该评级下的所有学校
                    for school in schools:
                        # 创建一条记录
                        record = {
                            # "category": category,
                            # "subject_code": subject_code,
                            "subject_name": subject_name,
                            "rating": rating,
                            # "school_code": school.get("code", ""), # 使用.get()避免KeyError
                            "school_name": school.get("name", "") # 使用.get()避免KeyError
                        }
                        formatted_data.append(record)

        # 将数据保存为新的JSON文件
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(formatted_data, f, ensure_ascii=False, indent=2)

        print(f"成功转换数据并保存到 {output_json}")

    except Exception as e:
        print(f"转换数据过程中发生错误: {e}")
        traceback.print_exc() # 打印转换过程中的详细错误信息


if __name__ == '__main__':
    # 提取表格数据到JSON
    extract_table_to_json(url, 'raw_' + output_filename)

    # 转换为指定格式
    convert_to_specified_format('raw_' + output_filename, output_filename)