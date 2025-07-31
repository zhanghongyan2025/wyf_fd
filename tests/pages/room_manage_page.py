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


class RoomManagePage:
    """房间管理页面自动化测试类，用于处理与房间管理相关的UI操作和验证"""

    def __init__(self, page: Page):
        """
        初始化RoomManagePage类

        Args:
            page (Page): Playwright的Page对象，用于操作浏览器页面
        """
        self.page = page

    def navigate_to_register(self):
        """
        导航到房间管理页面并处理可能的异常

        Args:
            base_url (str): 基础URL地址

        Returns:
            bool: 导航成功返回True，失败返回False
        """
        try:
            # 导航到首页
            # 等待并点击房间管理链接，增加重试机制
            room_manage = self.page.get_by_role("button", name="备案房间")
            room_manage.wait_for(state="visible", timeout=5000)
            room_manage.click(timeout=3000)

            # 可添加导航成功的日志或断言
            logger.info("成功导航到房间管理页面")
            return True
        except TimeoutError as e:
            logger.error(f"导航超时: {e}")
            self.page.screenshot(path="navigation_timeout.png")
            return False
        except Exception as e:
            logger.error(f"导航失败: {e}")
            self.page.screenshot(path="navigation_error.png")
            return False

