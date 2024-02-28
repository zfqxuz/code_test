import os
import sys
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from datetime import datetime, timedelta

# 获取币种代码和中文名的映射并保存为本地JSON文件
def fetch_currency_mapping(driver):
    try:
        wait = WebDriverWait(driver, 10)
        driver.get("https://www.11meigui.com/tools/currency")
        # 等待页面元素加载完毕
        wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="desc"]/table')))
        currency_mapping = {}
        # 查找并遍历所有表格以获取币种信息
        tables = driver.find_elements(By.XPATH, '//*[@id="desc"]/table')
        for table in tables:
            rows = table.find_elements(By.TAG_NAME, 'tr')[2:] # 从第三行开始是币种信息
            for row in rows:
                columns = row.find_elements(By.TAG_NAME, 'td')
                if len(columns) >= 5: # 确保行中有足够的列
                    currency_name = columns[1].text.strip() # 币种名称
                    currency_code = columns[4].text.strip() # 币种代码
                    currency_mapping[currency_code] = currency_name
        # 将映射保存到本地
        with open('currency_codes_to_names.json', 'w', encoding='utf-8') as f:
            json.dump(currency_mapping, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"获取币种映射失败: {e}")

# 根据日期和货币代码查询汇率
def query_exchange_rate(driver, date, currency_code):
    try:
        with open('currency_codes_to_names.json', 'r', encoding='utf-8') as f:
            currency_mapping = json.load(f)
        currency_name = currency_mapping.get(currency_code.upper())
        if currency_name:
            wait = WebDriverWait(driver, 10)
            driver.get("https://www.boc.cn/sourcedb/whpj/")
            start_date = datetime.strptime(date, "%Y%m%d").date()
            end_date = start_date + timedelta(days=1)
            # 输入查询条件
            driver.find_element(By.ID, "erectDate").send_keys(start_date.strftime("%Y-%m-%d"))
            driver.find_element(By.ID, "nothing").send_keys(end_date.strftime("%Y-%m-%d"))
            Select(driver.find_element(By.ID, "pjname")).select_by_visible_text(currency_name)
            # 点击查询按钮
            driver.find_element(By.XPATH, '//*[@id="historysearchform"]/div/table/tbody/tr/td[7]/input').click()
            # 等待查询结果加载
            wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div/div[4]')))
            # 获取并打印结果
            result = driver.find_element(By.XPATH, '/html/body/div/div[4]').text.split('\n')[1]
            print(result.split('\n')[0].split(' ')[1])
        else:
            print("未找到货币代码对应的映射。")
    except Exception as e:
        print(f"查询汇率失败: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("使用方法: python yourscript.py <date> <currency_code>")
        exit(0)
    date, currency_code = sys.argv[1], sys.argv[2]

    driver = webdriver.Chrome()
    try:
        # 如果本地不存在币种映射文件，则先获取映射
        if not os.path.exists('currency_codes_to_names.json'):
            fetch_currency_mapping(driver)
        query_exchange_rate(driver, date, currency_code)
    finally:
        driver.quit()
