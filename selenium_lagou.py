"""
This module is Lagou spider
Created by zhangwl.
"""

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import FirefoxBinary
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from pyquery import PyQuery as pq
from model.lagou import Lagou
import time


class LagouSpider:
    def __init__(self, city='深圳', search_key='web前端'):
        self.city = city
        self.search_key = search_key

    def get_jobs(self, driver):
        try:
            select_area = WebDriverWait(driver, 10).until(
                EC.visibility_of(driver.find_element_by_partial_link_text(self.city))
            )
            # 选择城市
            select_area.click()
            print('选择城市:', self.city)
        except Exception as e:
            driver.close()
            print(e)

        try:
            search = driver.find_element(By.ID, 'search_input')
            # 搜索岗位
            search.send_keys(self.search_key)
            search.send_keys(Keys.RETURN)
            print('搜索岗位:', self.search_key)
            time.sleep(3)
        except Exception as e:
            driver.close()
            print(e)

        page = 1
        while True:
            try:
                # 判断是否含有职位item
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'con_list_item')))
            except Exception as e:
                print('没有找到职位item,自动中断')
                print(e)
                driver.close()
                break

            doc = pq(driver.page_source)
            print('开始解析第 {} 页数据'.format(page))
            for item in doc('.item_con_list li').items():
                job_name = item.find('h3').text()
                addr = item.find('em').text()
                format_time = item.find('.format-time').text()
                money = item.find('.money').text()
                money_span = item.find('.p_bot .li_b_l span')
                money_span.replace_with('')
                experience_education = item.find('.p_bot .li_b_l').text().split('/')
                experience, education = experience_education[0].strip(), experience_education[1].strip()
                company = item.find('.company_name a').text()
                company_industry = item.find('.industry').text()
                company_good_point = item.find('.li_b_r').text()
                job_tags = item.find('.list_item_bot .li_b_l').text()
                url = item.find('.position_link').attr('href')
                json = {
                    'job_name': job_name,
                    'job_tags': job_tags,
                    'addr': addr,
                    'money': money,
                    'experience': experience,
                    'education': education,
                    'company': company,
                    'company_industry': company_industry,
                    'company_good_point': company_good_point,
                    'format_time': format_time,
                    'url': url,
                }
                # 根据自己的方法存储数据
                print(json)
                Lagou.new(json)

            try:
                # 判断下一页按钮是否可以点击
                WebDriverWait(driver, 10).until(
                    EC.invisibility_of_element_located((By.CLASS_NAME, 'pager_next_disabled')))
                next_page = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'pager_next')))
                next_page.click()
                page += 1
                time.sleep(3)
            except Exception as e:
                print('没有下一页了,自动中断')
                print(e)
                driver.close()
                break

    def crawl(self, url='https://www.lagou.com/'):
        fireFoxOptions = webdriver.FirefoxOptions()
        # 设置无界面模式
        fireFoxOptions.set_headless()
        binary = FirefoxBinary('/usr/bin/firefox-zh')
        driver = webdriver.Firefox(executable_path='/home/zxiaobai/driver/geckodriver', firefox_binary=binary,
                                   firefox_options=fireFoxOptions)
        driver.set_page_load_timeout(30)
        driver.get(url)
        self.get_jobs(driver)


if __name__ == '__main__':
    spider = LagouSpider(city='深圳', search_key='python')
    spider.crawl()
