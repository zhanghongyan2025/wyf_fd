import re
import time

from playwright.sync_api import Playwright, sync_playwright, expect
from tests.utils.page_utils import upload_file, get_label_corresponding_element

from playwright.async_api import Playwright

from tests.conftest import base_url
from conf.logging_config import logger
from tests.utils.page_utils import *
from tests.utils.validator import *
from playwright.sync_api import Page, sync_playwright

import re
import os
import time
import logging


class lyManagePage:
    """房间管理页面自动化测试类，用于处理与房间管理相关的UI操作和验证"""

    def __init__(self, page: Page):
        """
        初始化RoomManagePage类

        Args:
            page (Page): Playwright的Page对象，用于操作浏览器页面
        """
        self.page = page
        self.add_Ly_button = self.page.get_by_role("button", name="新增楼宇")
        self.expand_query_button = self.page.get_by_role("button", name="展开查询")
        self.query_input = self.page.locator('//input[@placeholder="请输入楼宇名称"]')
        self.query_button = self.page.get_by_role("button", name="搜索")
        self.reset_button = self.page.get_by_role("button", name="重置")
        self.ly_list = self.page.locator("tbody")


    def add_ly(self,ly_name: str, expected_text: str, test_filed: str = None):

      # 等待并点击新增楼宇按钮，增加重试机制

      self.page.get_by_role("textbox", name="请输入楼宇名称").fill(ly_name)
      self.page.get_by_role("button", name="确 定").click()
      is_matched, actual_text = check_alert_text(self.page, expected_text)
      return is_matched

    def query_ly(self,ly_name: str):

        self.query_input.fill(ly_name)
        self.query_button.click()
        # XPath 方式：定位 tbody 下 class 为 "el-table_1_column_2" 的所有 div
        result_elements = self.page.locator('//tbody//td[contains(@class, "el-table_1_column_2")]//div')

        # 遍历所有元素，查找匹配的文本
        found = False
        result = None
        for i in range(result_elements.count()):
            element_text = result_elements.nth(i).text_content().strip()
            if element_text == ly_name:
                found = True
                logger.info(f"✅ 找到匹配文本在第 {i + 1} 个元素: {ly_name}")
                # 可选：对匹配元素执行操作
                result_elements.nth(i).click()
                result = result_elements.nth(i)
                break

        if not found:
            logger.info(f"❌ 找到匹配文本在第 {i + 1} 个元素: {ly_name}")

        return result

    def get_ly_option(self, ly_name: str, operation: str):
        self.query_ly(ly_name).locator("../following-sibling::td//button[text()= {operation}\"]")

    # def modified_ly(self):



    def ly_name_error(self, expected_text):
        return get_element_corresponding_error_tip(
            self.page.get_by_text("楼宇名称", exact=True), '../..//div[contains(@class, "el-form-item__error")]', expected_text
        )

    def  ly_name_duplicate_error(self, expected_text):
        is_matched, actual_text = check_alert_text(self.page, expected_text)
        return is_matched


# def run(playwright: Playwright) -> None:
#     browser = playwright.chromium.launch(headless=False)
#     context = browser.new_context()
#     page = context.new_page()
#     page.goto("http://192.168.40.61:3333/login_fd?redirect=%2Ffangwu_fangdong%2Ffangjian%2Fadd")
#     file_path = '../data/evidence_files/1.png'
#     # 登录逻辑
#     page.get_by_role("textbox", name="账号").fill("hongyan20256")
#     page.get_by_role("textbox", name="密码").fill("Aa123123!")
#     page.get_by_role("button", name="登 录").click()
#
#     # 导航到民宿管理页面
#     page.get_by_role("menuitem", name="房屋管理").click()
#     page.get_by_role("link", name="民宿管理").click()
#
#     # 循环添加100个民宿
#     for i in range(112, 200):  # 从12到111
#         # 点击新增民宿按钮
#         page.get_by_role("button", name=" 新增民宿").click()
#
#         # 输入民宿名称（按序号递增）
#         page.get_by_role("textbox", name="请输入民宿名称").fill(f"石家庄民宿{i}")
#
#         # 选择行政区划（保持原有逻辑）
#         page.get_by_role("textbox", name="请选择行政区划").click()
#         page.get_by_text("河北省").click()
#         page.get_by_text("石家庄市").click()
#         page.get_by_text("长安区").click()
#         page.get_by_text("建北街道").click()
#
#         # 输入详细地址（微调序号）
#         page.get_by_role("textbox", name="请输入详细地址").fill(f"棉一小区")
#         get_label_corresponding_element(page,"负责人证件照(正面)", 'following-sibling::div//input[@type="file"]').set_input_files(file_path)
#         time.sleep(1)
#         get_label_corresponding_element(page,"负责人证件照(反面)", 'following-sibling::div//input[@type="file"]').set_input_files(file_path)
#         page.get_by_role("button", name="保 存").click()
#
#     context.close()
#     browser.close()
#
#
# with sync_playwright() as playwright:
#     run(playwright)